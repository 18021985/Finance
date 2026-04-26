from typing import Dict, List, Callable
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class Alert:
    """Represents a trading alert"""
    alert_id: str
    symbol: str
    alert_type: str  # 'price', 'signal', 'momentum', 'pattern'
    condition: str
    triggered: bool
    message: str
    priority: str  # 'low', 'medium', 'high'
    triggered_at: datetime = None

class AlertSystem:
    """Alert system for monitoring signal changes and price movements"""
    
    def __init__(self):
        self.active_alerts = []
        self.alert_history = []
        self.alert_callbacks = {}
    
    def create_price_alert(self, symbol: str, condition: str, 
                          target_price: float, priority: str = 'medium') -> Alert:
        """
        Create a price-based alert
        
        Args:
            symbol: Stock symbol
            condition: 'above', 'below', 'cross_above', 'cross_below'
            target_price: Price level to trigger alert
            priority: Alert priority
        """
        alert_id = f"price_{symbol}_{datetime.now().timestamp()}"
        
        alert = Alert(
            alert_id=alert_id,
            symbol=symbol,
            alert_type='price',
            condition=f"{condition} {target_price}",
            triggered=False,
            message=f"Alert when {symbol} {condition} {target_price}",
            priority=priority
        )
        
        self.active_alerts.append(alert)
        return alert
    
    def create_signal_alert(self, symbol: str, signal_type: str,
                           threshold: float, priority: str = 'medium') -> Alert:
        """
        Create a signal-based alert
        
        Args:
            symbol: Stock symbol
            signal_type: 'bullish_score', 'bearish_score', 'net_score', 'momentum'
            threshold: Threshold value to trigger alert
            priority: Alert priority
        """
        alert_id = f"signal_{symbol}_{signal_type}_{datetime.now().timestamp()}"
        
        alert = Alert(
            alert_id=alert_id,
            symbol=symbol,
            alert_type='signal',
            condition=f"{signal_type} {threshold}",
            triggered=False,
            message=f"Alert when {symbol} {signal_type} crosses {threshold}",
            priority=priority
        )
        
        self.active_alerts.append(alert)
        return alert
    
    def create_pattern_alert(self, symbol: str, pattern: str,
                           priority: str = 'high') -> Alert:
        """
        Create a chart pattern alert
        
        Args:
            symbol: Stock symbol
            pattern: Pattern name (e.g., 'double_top', 'head_shoulders')
            priority: Alert priority
        """
        alert_id = f"pattern_{symbol}_{pattern}_{datetime.now().timestamp()}"
        
        alert = Alert(
            alert_id=alert_id,
            symbol=symbol,
            alert_type='pattern',
            condition=pattern,
            triggered=False,
            message=f"Alert when {symbol} forms {pattern} pattern",
            priority=priority
        )
        
        self.active_alerts.append(alert)
        return alert
    
    def check_price_alerts(self, symbol: str, current_price: float) -> List[Alert]:
        """Check if any price alerts should be triggered"""
        triggered_alerts = []
        
        for alert in self.active_alerts:
            if alert.symbol != symbol or alert.alert_type != 'price' or alert.triggered:
                continue
            
            condition_parts = alert.condition.split()
            condition = condition_parts[0]
            target = float(condition_parts[1])
            
            should_trigger = False
            
            if condition == 'above' and current_price > target:
                should_trigger = True
            elif condition == 'below' and current_price < target:
                should_trigger = True
            elif condition == 'cross_above' and current_price > target:
                should_trigger = True
            elif condition == 'cross_below' and current_price < target:
                should_trigger = True
            
            if should_trigger:
                alert.triggered = True
                alert.triggered_at = datetime.now()
                alert.message = f"{symbol} is now {condition} {target} at {current_price}"
                triggered_alerts.append(alert)
                self.alert_history.append(alert)
        
        return triggered_alerts
    
    def check_signal_alerts(self, symbol: str, current_value: float, 
                           signal_type: str) -> List[Alert]:
        """Check if any signal alerts should be triggered"""
        triggered_alerts = []
        
        for alert in self.active_alerts:
            if (alert.symbol != symbol or alert.alert_type != 'signal' or 
                alert.triggered or signal_type not in alert.condition):
                continue
            
            condition_parts = alert.condition.split()
            threshold = float(condition_parts[-1])
            
            # Simple threshold check (can be enhanced for cross_above/below)
            if current_value > threshold:
                alert.triggered = True
                alert.triggered_at = datetime.now()
                alert.message = f"{symbol} {signal_type} is {current_value:.2f} (threshold: {threshold})"
                triggered_alerts.append(alert)
                self.alert_history.append(alert)
        
        return triggered_alerts
    
    def check_pattern_alerts(self, symbol: str, detected_patterns: List[str]) -> List[Alert]:
        """Check if any pattern alerts should be triggered"""
        triggered_alerts = []
        
        for alert in self.active_alerts:
            if alert.symbol != symbol or alert.alert_type != 'pattern' or alert.triggered:
                continue
            
            if alert.condition in detected_patterns:
                alert.triggered = True
                alert.triggered_at = datetime.now()
                alert.message = f"{symbol} has formed {alert.condition} pattern"
                triggered_alerts.append(alert)
                self.alert_history.append(alert)
        
        return triggered_alerts
    
    def register_callback(self, alert_type: str, callback: Callable):
        """Register a callback function for specific alert types"""
        self.alert_callbacks[alert_type] = callback
    
    def trigger_callback(self, alert: Alert):
        """Trigger registered callback for alert"""
        callback = self.alert_callbacks.get(alert.alert_type)
        if callback:
            callback(alert)
    
    def get_active_alerts(self, symbol: str = None) -> List[Dict]:
        """Get all active alerts, optionally filtered by symbol"""
        alerts = self.active_alerts
        if symbol:
            alerts = [a for a in alerts if a.symbol == symbol]
        
        return [self._alert_to_dict(a) for a in alerts if not a.triggered]
    
    def get_alert_history(self, symbol: str = None, limit: int = 50) -> List[Dict]:
        """Get alert history, optionally filtered by symbol"""
        history = self.alert_history
        if symbol:
            history = [a for a in history if a.symbol == symbol]
        
        return [self._alert_to_dict(a) for a in history[-limit:]]
    
    def cancel_alert(self, alert_id: str) -> bool:
        """Cancel an active alert"""
        for i, alert in enumerate(self.active_alerts):
            if alert.alert_id == alert_id and not alert.triggered:
                self.active_alerts.pop(i)
                return True
        return False
    
    def clear_triggered_alerts(self):
        """Remove all triggered alerts from active list"""
        self.active_alerts = [a for a in self.active_alerts if not a.triggered]
    
    def _alert_to_dict(self, alert: Alert) -> Dict:
        """Convert alert to dictionary"""
        return {
            'alert_id': alert.alert_id,
            'symbol': alert.symbol,
            'alert_type': alert.alert_type,
            'condition': alert.condition,
            'triggered': alert.triggered,
            'triggered_at': alert.triggered_at.isoformat() if alert.triggered_at else None,
            'message': alert.message,
            'priority': alert.priority,
        }
    
    def get_alert_summary(self) -> Dict:
        """Get summary of alert system status"""
        active_count = len([a for a in self.active_alerts if not a.triggered])
        triggered_today = len([a for a in self.alert_history 
                            if a.triggered_at and a.triggered_at.date() == datetime.now().date()])
        
        by_priority = {}
        for alert in self.active_alerts:
            if not alert.triggered:
                by_priority[alert.priority] = by_priority.get(alert.priority, 0) + 1
        
        return {
            'active_alerts': active_count,
            'triggered_today': triggered_today,
            'by_priority': by_priority,
            'total_history': len(self.alert_history),
        }
