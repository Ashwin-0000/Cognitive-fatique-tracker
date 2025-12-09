"""Helper utility functions"""
from datetime import datetime, timedelta
from typing import Union


def format_duration(seconds: Union[int, float]) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted string (e.g., "1h 23m", "45m", "23s")
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    
    minutes = int(seconds // 60)
    if minutes < 60:
        return f"{minutes}m"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if remaining_minutes == 0:
        return f"{hours}h"
    return f"{hours}h {remaining_minutes}m"


def format_time(dt: datetime) -> str:
    """
    Format datetime to time string.
    
    Args:
        dt: Datetime object
    
    Returns:
        Formatted time string (HH:MM:SS)
    """
    return dt.strftime("%H:%M:%S")


def format_datetime(dt: datetime) -> str:
    """
    Format datetime to readable string.
    
    Args:
        dt: Datetime object
    
    Returns:
        Formatted datetime string
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def normalize_score(value: float, min_val: float, max_val: float) -> float:
    """
    Normalize a value to 0-100 scale.
    
    Args:
        value: Value to normalize
        min_val: Minimum possible value
        max_val: Maximum possible value
    
    Returns:
        Normalized value (0-100)
    """
    if max_val == min_val:
        return 0.0
    
    normalized = ((value - min_val) / (max_val - min_val)) * 100
    return max(0.0, min(100.0, normalized))


def calculate_moving_average(values: list, window: int = 5) -> float:
    """
    Calculate moving average of recent values.
    
    Args:
        values: List of numeric values
        window: Window size for moving average
    
    Returns:
        Moving average
    """
    if not values:
        return 0.0
    
    recent_values = values[-window:]
    return sum(recent_values) / len(recent_values)


def time_since(dt: datetime) -> str:
    """
    Get human-readable time since a datetime.
    
    Args:
        dt: Past datetime
    
    Returns:
        Human-readable string (e.g., "5 minutes ago")
    """
    now = datetime.now()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    
    minutes = int(seconds // 60)
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    
    days = hours // 24
    return f"{days} day{'s' if days != 1 else ''} ago"


def validate_percentage(value: float) -> float:
    """
    Ensure a value is a valid percentage (0-100).
    
    Args:
        value: Value to validate
    
    Returns:
        Clamped value between 0-100
    """
    return max(0.0, min(100.0, value))


def get_time_of_day_factor() -> float:
    """
    Get fatigue factor based on time of day.
    Higher values in late afternoon/evening.
    
    Returns:
        Factor value (0.8-1.2)
    """
    hour = datetime.now().hour
    
    # Time-based fatigue curve
    if 6 <= hour < 9:  # Early morning
        return 0.9
    elif 9 <= hour < 12:  # Mid morning
        return 0.8
    elif 12 <= hour < 14:  # Lunch time
        return 1.0
    elif 14 <= hour < 16:  # Early afternoon (post-lunch dip)
        return 1.1
    elif 16 <= hour < 20:  # Late afternoon/evening
        return 1.2
    else:  # Night
        return 1.3


def calculate_work_intensity(activity_count: int, duration_minutes: float) -> str:
    """
    Calculate work intensity based on activity and duration.
    
    Args:
        activity_count: Number of activities
        duration_minutes: Duration in minutes
    
    Returns:
        Intensity level (Low, Medium, High, Very High)
    """
    if duration_minutes <= 0:
        return "Low"
    
    activity_per_minute = activity_count / duration_minutes
    
    if activity_per_minute < 5:
        return "Low"
    elif activity_per_minute < 15:
        return "Medium"
    elif activity_per_minute < 30:
        return "High"
    else:
        return "Very High"
