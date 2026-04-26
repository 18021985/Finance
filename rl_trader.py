import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import yfinance as yf

# Try to import gym/stable-baselines3
try:
    import gymnasium as gym
    from gymnasium import spaces
    GYM_AVAILABLE = True
except ImportError:
    GYM_AVAILABLE = False
    print("Gymnasium not available. Install with: pip install gymnasium")

try:
    from stable_baselines3 import PPO, A2C, DQN
    SB3_AVAILABLE = True
except ImportError:
    SB3_AVAILABLE = False
    print("Stable-Baselines3 not available. Install with: pip install stable-baselines3")

@dataclass
class RLAction:
    """RL action"""
    action: int  # 0=hold, 1=buy, 2=sell
    position_size: float
    confidence: float

@dataclass
class RLState:
    """RL state"""
    features: np.ndarray
    current_position: int  # 0=neutral, 1=long, -1=short
    portfolio_value: float
    unrealized_pnl: float

if GYM_AVAILABLE:
    class TradingEnvironment(gym.Env):
        """
        Custom trading environment for reinforcement learning
        
        Action space: 0=hold, 1=buy, 2=sell
        Observation space: Technical features + position info
        """
        
        def __init__(self, symbol: str, period: str = '2y', initial_balance: float = 100000):
            super().__init__()
        
        self.symbol = symbol
        self.period = period
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.position = 0  # 0=neutral, 1=long, -1=short
        self.position_size = 0
        self.entry_price = 0
        
        # Fetch data
        self.data = self._fetch_data()
        if self.data is None or len(self.data) < 100:
            raise ValueError("Insufficient data for environment")
        
        # Feature names
        self.feature_names = [
            'rsi', 'macd', 'momentum_20d', 'volume_change',
            'price_vs_sma50', 'price_vs_sma200', 'volatility',
            'high_low_range', 'gap', 'trend_strength',
            'current_position', 'unrealized_pnl_pct'
        ]
        
        # Action space: 0=hold, 1=buy, 2=sell
        self.action_space = spaces.Discrete(3)
        
        # Observation space: features + position info
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf,
            shape=(len(self.feature_names),),
            dtype=np.float32
        )
        
        # Current step
        self.current_step = 50  # Start after enough data for features
        
        # Transaction cost
        self.transaction_cost = 0.001  # 0.1%
    
    def _fetch_data(self) -> pd.DataFrame:
        """Fetch historical data"""
        try:
            ticker = yf.Ticker(self.symbol)
            hist = ticker.history(period=self.period)
            return hist
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
    
    def _prepare_features(self, idx: int) -> np.ndarray:
        """Prepare features for a given index"""
        if idx < 50:
            return np.zeros(len(self.feature_names))
        
        hist = self.data.iloc[:idx+1]
        
        features = []
        
        # RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        features.append(rsi.iloc[-1])
        
        # MACD
        ema_12 = hist['Close'].ewm(span=12).mean()
        ema_26 = hist['Close'].ewm(span=26).mean()
        macd = ema_12 - ema_26
        features.append(macd.iloc[-1])
        
        # Momentum
        momentum_20d = (hist['Close'].iloc[-1] / hist['Close'].iloc[-21] - 1) * 100
        features.append(momentum_20d)
        
        # Volume change
        if 'Volume' in hist.columns:
            volume_change = (hist['Volume'].iloc[-1] / hist['Volume'].iloc[-5:].mean() - 1) * 100
        else:
            volume_change = 0
        features.append(volume_change)
        
        # Price vs SMA50
        sma_50 = hist['Close'].rolling(50).mean()
        price_vs_sma50 = (hist['Close'].iloc[-1] / sma_50.iloc[-1] - 1) * 100
        features.append(price_vs_sma50)
        
        # Price vs SMA200
        sma_200 = hist['Close'].rolling(200).mean()
        price_vs_sma200 = (hist['Close'].iloc[-1] / sma_200.iloc[-1] - 1) * 100
        features.append(price_vs_sma200)
        
        # Volatility
        returns = hist['Close'].pct_change()
        volatility = returns.rolling(20).std().iloc[-1] * np.sqrt(252)
        features.append(volatility)
        
        # High-low range
        high_low_range = (hist['High'].iloc[-1] / hist['Low'].iloc[-1] - 1) * 100
        features.append(high_low_range)
        
        # Gap
        gap = (hist['Open'].iloc[-1] / hist['Close'].iloc[-2] - 1) * 100
        features.append(gap)
        
        # Trend strength
        high_diff = hist['High'].diff()
        low_diff = hist['Low'].diff()
        plus_dm = high_diff.where((high_diff > 0) & (low_diff < 0), 0)
        minus_dm = -low_diff.where((low_diff > 0) & (high_diff < 0), 0)
        tr = pd.concat([hist['High'] - hist['Low'], 
                       abs(hist['High'] - hist['Close'].shift(1)),
                       abs(hist['Low'] - hist['Close'].shift(1))], axis=1).max(axis=1)
        
        plus_di = 100 * (plus_dm.rolling(14).mean() / tr.rolling(14).mean())
        minus_di = 100 * (minus_dm.rolling(14).mean() / tr.rolling(14).mean())
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        trend_strength = dx.rolling(14).mean().iloc[-1]
        features.append(trend_strength)
        
        # Current position
        features.append(float(self.position))
        
        # Unrealized PnL
        if self.position != 0 and self.entry_price > 0:
            current_price = hist['Close'].iloc[-1]
            if self.position == 1:
                unrealized_pnl = (current_price - self.entry_price) / self.entry_price
            else:
                unrealized_pnl = (self.entry_price - current_price) / self.entry_price
        else:
            unrealized_pnl = 0
        features.append(unrealized_pnl)
        
        return np.array(features, dtype=np.float32)
    
    def reset(self, seed=None, options=None):
        """Reset environment"""
        super().reset(seed=seed)
        
        self.current_balance = self.initial_balance
        self.position = 0
        self.position_size = 0
        self.entry_price = 0
        self.current_step = 50
        
        observation = self._prepare_features(self.current_step)
        info = {}
        
        return observation, info
    
    def step(self, action):
        """Execute action and return observation, reward, done, truncated, info"""
        current_price = self.data['Close'].iloc[self.current_step]
        
        # Execute action
        if action == 1:  # Buy
            if self.position == 0:
                self.position = 1
                self.entry_price = current_price
                self.position_size = self.current_balance / current_price
                self.current_balance = 0
            elif self.position == -1:
                # Close short
                pnl = (self.entry_price - current_price) * self.position_size
                self.current_balance += pnl * (1 - self.transaction_cost)
                self.position = 0
                self.position_size = 0
                self.entry_price = 0
        
        elif action == 2:  # Sell
            if self.position == 0:
                self.position = -1
                self.entry_price = current_price
                self.position_size = self.current_balance / current_price
                self.current_balance = 0
            elif self.position == 1:
                # Close long
                pnl = (current_price - self.entry_price) * self.position_size
                self.current_balance += pnl * (1 - self.transaction_cost)
                self.position = 0
                self.position_size = 0
                self.entry_price = 0
        
        # Calculate reward
        reward = self._calculate_reward(current_price)
        
        # Move to next step
        self.current_step += 1
        
        # Check if done
        done = self.current_step >= len(self.data) - 1
        truncated = False
        
        # Get new observation
        observation = self._prepare_features(self.current_step)
        
        # Calculate portfolio value
        portfolio_value = self._calculate_portfolio_value(current_price)
        
        info = {
            'portfolio_value': portfolio_value,
            'position': self.position,
            'entry_price': self.entry_price,
            'current_price': current_price
        }
        
        return observation, reward, done, truncated, info
    
    def _calculate_reward(self, current_price: float) -> float:
        """Calculate reward based on position and price change"""
        if self.position == 0:
            return 0  # No reward for holding cash
        
        if self.position == 1:
            # Long position
            if self.entry_price > 0:
                return (current_price - self.entry_price) / self.entry_price
        else:
            # Short position
            if self.entry_price > 0:
                return (self.entry_price - current_price) / self.entry_price
        
        return 0
    
    def _calculate_portfolio_value(self, current_price: float) -> float:
        """Calculate current portfolio value"""
        if self.position == 0:
            return self.current_balance
        
        if self.position == 1:
            return self.current_balance + self.position_size * current_price
        else:
            return self.current_balance + self.position_size * (2 * self.entry_price - current_price)


if SB3_AVAILABLE:
    class RLTrader:
        """
        Reinforcement learning trader using stable-baselines3
        
        Algorithms:
        - PPO (Proximal Policy Optimization)
        - A2C (Advantage Actor-Critic)
        - DQN (Deep Q-Network)
        """
        
        def __init__(self, algorithm: str = 'PPO'):
            self.algorithm = algorithm
            self.model = None
            self.env = None
        
        def create_environment(self, symbol: str, period: str = '2y') -> TradingEnvironment:
            """Create trading environment"""
            env = TradingEnvironment(symbol, period)
            return env
        
        def train(self, symbol: str, period: str = '2y', total_timesteps: int = 10000):
            """
            Train RL agent
            
            Args:
                symbol: Stock ticker
                period: Historical period
                total_timesteps: Total training timesteps
            """
            # Create environment
            self.env = self.create_environment(symbol, period)
            
            # Create model based on algorithm
            if self.algorithm == 'PPO':
                self.model = PPO('MlpPolicy', self.env, verbose=1)
            elif self.algorithm == 'A2C':
                self.model = A2C('MlpPolicy', self.env, verbose=1)
            elif self.algorithm == 'DQN':
                self.model = DQN('MlpPolicy', self.env, verbose=1)
            else:
                self.model = PPO('MlpPolicy', self.env, verbose=1)
            
            # Train
            self.model.learn(total_timesteps=total_timesteps)
            
            print(f"Training complete using {self.algorithm}")
        
        def predict(self, symbol: str) -> RLAction:
            """
            Predict action using trained model
            
            Args:
                symbol: Stock ticker
            """
            if self.model is None:
                return RLAction(action=0, position_size=0, confidence=0)
            
            # Create environment
            env = self.create_environment(symbol, '1y')
            obs, _ = env.reset()
            
            # Predict action
            action, _ = self.model.predict(obs, deterministic=True)
            
            # Get action probabilities (for confidence)
            if hasattr(self.model, 'policy'):
                # This would require accessing the policy's action probabilities
                confidence = 0.7  # Placeholder
            else:
                confidence = 0.5
            
            return RLAction(
                action=int(action),
                position_size=0.1,  # Placeholder
                confidence=confidence
            )
        
        def save_model(self, path: str):
            """Save trained model"""
            if self.model is not None:
                self.model.save(path)
                print(f"Model saved to {path}")
        
        def load_model(self, path: str):
            """Load trained model"""
            if self.algorithm == 'PPO':
                self.model = PPO.load(path)
            elif self.algorithm == 'A2C':
                self.model = A2C.load(path)
            elif self.algorithm == 'DQN':
                self.model = DQN.load(path)
            print(f"Model loaded from {path}")
