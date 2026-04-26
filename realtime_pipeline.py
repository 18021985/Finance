import yfinance as yf
import pandas as pd
import asyncio
import time
from datetime import datetime, time as dt_time
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
import threading
from queue import Queue

@dataclass
class MarketData:
    """Real-time market data"""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime
    bid: Optional[float] = None
    ask: Optional[float] = None

class RealTimeDataPipeline:
    """
    Real-time data polling pipeline
    
    Polls data at specified intervals during market hours
    Supports callbacks for data updates
    """
    
    def __init__(self, poll_interval: int = 30):
        self.poll_interval = poll_interval  # seconds
        self.symbols: List[str] = []
        self.callbacks: List[Callable] = []
        self.is_running = False
        self.data_cache: Dict[str, MarketData] = {}
        self.thread: Optional[threading.Thread] = None
        self.queue: Queue = Queue()
        
        # Market hours (US Eastern)
        self.market_open = dt_time(9, 30)  # 9:30 AM
        self.market_close = dt_time(16, 0)  # 4:00 PM
        
    def add_symbol(self, symbol: str):
        """Add symbol to watchlist"""
        if symbol not in self.symbols:
            self.symbols.append(symbol)
            print(f"Added {symbol} to watchlist")
    
    def remove_symbol(self, symbol: str):
        """Remove symbol from watchlist"""
        if symbol in self.symbols:
            self.symbols.remove(symbol)
            if symbol in self.data_cache:
                del self.data_cache[symbol]
            print(f"Removed {symbol} from watchlist")
    
    def add_callback(self, callback: Callable):
        """Register callback for data updates"""
        self.callbacks.append(callback)
    
    def is_market_hours(self) -> bool:
        """Check if currently within market hours"""
        now = datetime.now().time()
        return self.market_open <= now <= self.market_close
    
    def is_trading_day(self) -> bool:
        """Check if today is a trading day (weekday)"""
        return datetime.now().weekday() < 5  # Monday=0, Friday=4
    
    def fetch_data(self, symbol: str) -> Optional[MarketData]:
        """Fetch current data for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            # Get most recent data
            hist = ticker.history(period="1d", interval="1m")
            
            if hist.empty:
                return None
            
            latest = hist.iloc[-1]
            prev_close = hist['Close'].iloc[0] if len(hist) > 1 else latest['Close']
            
            change = latest['Close'] - prev_close
            change_percent = (change / prev_close) * 100 if prev_close != 0 else 0
            
            return MarketData(
                symbol=symbol,
                price=round(latest['Close'], 2),
                change=round(change, 2),
                change_percent=round(change_percent, 2),
                volume=int(latest['Volume']) if 'Volume' in latest else 0,
                timestamp=datetime.now(),
                bid=round(latest['Low'], 2) if 'Low' in latest else None,
                ask=round(latest['High'], 2) if 'High' in latest else None
            )
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def poll_data(self):
        """Poll data for all symbols"""
        if not self.is_trading_day():
            print("Not a trading day, skipping poll")
            return
        
        if not self.is_market_hours():
            print("Outside market hours, skipping poll")
            return
        
        for symbol in self.symbols:
            data = self.fetch_data(symbol)
            if data:
                self.data_cache[symbol] = data
                self.queue.put(data)
    
    def notify_callbacks(self, data: MarketData):
        """Notify all registered callbacks"""
        for callback in self.callbacks:
            try:
                callback(data)
            except Exception as e:
                print(f"Error in callback: {e}")
    
    def process_queue(self):
        """Process data from queue and notify callbacks"""
        while not self.queue.empty():
            data = self.queue.get()
            self.notify_callbacks(data)
    
    def run(self):
        """Main polling loop"""
        while self.is_running:
            self.poll_data()
            self.process_queue()
            time.sleep(self.poll_interval)
    
    def start(self):
        """Start the polling thread"""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()
            print(f"Real-time pipeline started (interval: {self.poll_interval}s)")
    
    def stop(self):
        """Stop the polling thread"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("Real-time pipeline stopped")
    
    def get_latest_data(self, symbol: str) -> Optional[MarketData]:
        """Get latest cached data for a symbol"""
        return self.data_cache.get(symbol)
    
    def get_all_data(self) -> Dict[str, MarketData]:
        """Get all cached data"""
        return self.data_cache.copy()


class AsyncRealTimePipeline:
    """
    Async version of real-time data pipeline
    """
    
    def __init__(self, poll_interval: int = 30):
        self.poll_interval = poll_interval
        self.symbols: List[str] = []
        self.callbacks: List[Callable] = []
        self.is_running = False
        self.data_cache: Dict[str, MarketData] = {}
        
    async def fetch_data_async(self, symbol: str) -> Optional[MarketData]:
        """Fetch data asynchronously"""
        # Run blocking yfinance call in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._fetch_data_sync, symbol)
    
    def _fetch_data_sync(self, symbol: str) -> Optional[MarketData]:
        """Synchronous fetch for thread pool"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d", interval="1m")
            
            if hist.empty:
                return None
            
            latest = hist.iloc[-1]
            prev_close = hist['Close'].iloc[0] if len(hist) > 1 else latest['Close']
            
            change = latest['Close'] - prev_close
            change_percent = (change / prev_close) * 100 if prev_close != 0 else 0
            
            return MarketData(
                symbol=symbol,
                price=round(latest['Close'], 2),
                change=round(change, 2),
                change_percent=round(change_percent, 2),
                volume=int(latest['Volume']) if 'Volume' in latest else 0,
                timestamp=datetime.now()
            )
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    async def poll_data_async(self):
        """Poll data asynchronously"""
        for symbol in self.symbols:
            data = await self.fetch_data_async(symbol)
            if data:
                self.data_cache[symbol] = data
                for callback in self.callbacks:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(data)
                        else:
                            callback(data)
                    except Exception as e:
                        print(f"Error in callback: {e}")
    
    async def run_async(self):
        """Main async polling loop"""
        while self.is_running:
            await self.poll_data_async()
            await asyncio.sleep(self.poll_interval)
    
    async def start_async(self):
        """Start async polling"""
        if not self.is_running:
            self.is_running = True
            print(f"Async real-time pipeline started (interval: {self.poll_interval}s)")
            await self.run_async()
    
    def stop(self):
        """Stop async polling"""
        self.is_running = False
        print("Async real-time pipeline stopped")


# Example usage
if __name__ == "__main__":
    # Synchronous version
    pipeline = RealTimeDataPipeline(poll_interval=30)
    
    # Add symbols
    pipeline.add_symbol("AAPL")
    pipeline.add_symbol("GOOGL")
    pipeline.add_symbol("BTC-USD")
    
    # Add callback
    def on_data_update(data: MarketData):
        print(f"{data.symbol}: ${data.price} ({data.change_percent:+.2f}%)")
    
    pipeline.add_callback(on_data_update)
    
    # Start
    pipeline.start()
    
    # Run for 2 minutes
    time.sleep(120)
    
    # Stop
    pipeline.stop()
    
    # Get cached data
    print("\nCached data:")
    for symbol, data in pipeline.get_all_data().items():
        print(f"{symbol}: ${data.price}")
