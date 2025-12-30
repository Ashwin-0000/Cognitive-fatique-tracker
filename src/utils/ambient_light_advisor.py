"""Ambient light recommendations for eye health"""
from datetime import datetime
from typing import Optional
from src.utils.logger import default_logger as logger


class AmbientLightAdvisor:
    """Provides recommendations for ambient lighting based on time and conditions"""
    
    RECOMMENDATIONS = {
        'morning': {
            'time_range': (6, 12),
            'title': '🌅 Morning Light Recommendations',
            'description': 'Morning is ideal for natural light',
            'tips': [
                'Open curtains to let in natural daylight',
                'Position screen perpendicular to windows to avoid glare',
                'Use cooler color temperature (5000-6500K)',
                'Avoid direct sunlight on screen'
            ]
        },
        'afternoon': {
            'time_range': (12, 17),
            'title': '☀️ Afternoon Light Recommendations',
            'description': 'Peak daylight hours require balance',
            'tips': [
                'Use blinds to diffuse harsh direct sunlight',
                'Maintain balanced ambient and screen brightness',
                'Screen brightness should match room brightness',
                'Consider using anti-glare screen protector'
            ]
        },
        'evening': {
            'time_range': (17, 21),
            'title': '🌆 Evening Light Recommendations',
            'description': 'Transition to warmer lighting',
            'tips': [
                'Use warmer color temperature (3000-4000K)',
                'Reduce screen brightness gradually',
                'Ensure adequate ambient lighting (not too dim)',
                'Avoid harsh overhead lights'
            ]
        },
        'night': {
            'time_range': (21, 6),
            'title': '🌙 Night Light Recommendations',
            'description': 'Minimize blue light exposure',
            'tips': [
                'Use warm amber lighting (2700-3000K)',
                'Enable night mode/blue light filter',
                'Keep room lighting dim but not dark',
                'Use task lighting behind screen',
                'Consider amber-tinted glasses'
            ]
        }
    }
    
    def __init__(self):
        """Initialize ambient light advisor"""
        logger.info("Ambient light advisor initialized")
    
    def get_current_recommendation(self) -> dict:
        """Get lighting recommendation for current time"""
        current_hour = datetime.now().hour
        
        for period, data in self.RECOMMENDATIONS.items():
            start, end = data['time_range']
            
            # Handle overnight period (21-6)
            if start > end:
                if current_hour >= start or current_hour < end:
                    return data
            else:
                if start <= current_hour < end:
                    return data
        
        # Default to afternoon
        return self.RECOMMENDATIONS['afternoon']
    
    def get_recommendation_for_time(self, hour: int) -> dict:
        """Get recommendation for specific hour"""
        for period, data in self.RECOMMENDATIONS.items():
            start, end = data['time_range']
            
            if start > end:
                if hour >= start or hour < end:
                    return data
            else:
                if start <= hour < end:
                    return data
        
        return self.RECOMMENDATIONS['afternoon']
    
    def get_screen_brightness_suggestion(self) -> str:
        """Get screen brightness suggestion for current time"""
        hour = datetime.now().hour
        
        if 6 <= hour < 12:
            return "Medium-High (60-80%)"
        elif 12 <= hour < 17:
            return "High (70-90%)"
        elif 17 <= hour < 21:
            return "Medium (50-70%)"
        else:
            return "Low-Medium (30-50%)"
    
    def get_color_temperature_suggestion(self) -> str:
        """Get color temperature suggestion"""
        hour = datetime.now().hour
        
        if 6 <= hour < 12:
            return "Cool (5000-6500K) - Daylight"
        elif 12 <= hour < 17:
            return "Neutral (4000-5000K) - Bright White"
        elif 17 <= hour < 21:
            return "Warm (3000-4000K) - Soft White"
        else:
            return "Very Warm (2700-3000K) - Warm White/Amber"
    
    def check_for_glare_risk(self) -> bool:
        """Check if current time has high glare risk"""
        hour = datetime.now().hour
        # Peak glare risk during mid-afternoon
        return 12 <= hour < 17
    
    def should_enable_night_mode(self) -> bool:
        """Check if night mode should be enabled"""
        hour = datetime.now().hour
        return hour >= 21 or hour < 6
