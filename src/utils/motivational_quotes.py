"""Motivational quotes system"""
import random
from typing import List


class MotivationalQuotes:
    """Provides motivational quotes for breaks and achievements"""
    
    BREAK_QUOTES = [
        "Take a break - your mind will thank you! 🧠",
        "Rest is not idleness - it's essential for productivity.",
        "A short break now prevents burnout later.",
        "Your best work comes after proper rest.",
        "Stepping away helps you see things more clearly.",
        "Breaks boost creativity and problem-solving.",
        "You've earned this rest - enjoy it!",
        "Great minds think better after breaks.",
        "Refresh your mind, refresh your ideas.",
        "The pause is as important as the work.",
        "Productivity thrives on balanced rest.",
        "Your brain needs breaks to consolidate learning.",
        "Walking away brings fresh perspectives.",
        "Rest is progress in disguise.",
        "Better work awaits after a good break."
    ]
    
    ACHIEVEMENT_QUOTES = [
        "Outstanding achievement! Keep up the great work! 🎉",
        "You're building excellent work habits!",
        "Consistency is the key to success - well done!",
        "Your dedication is truly inspiring!",
        "Success is built one session at a time.",
        "You're proving that small steps lead to big wins!",
        "Excellence is a habit - and you're mastering it!",
        "Your progress speaks volumes!",
        "Remarkable commitment to your wellbeing!",
        "You're crushing your goals!"
    ]
    
    FATIGUE_QUOTES = [
        "Listen to your body - it's asking for rest.",
        "Pushing through fatigue reduces quality.",
        "Smart workers know when to pause.",
        "Your health is more important than any deadline.",
        "Rest now, excel later.",
        "Fatigue is a signal, not a weakness.",
        "Take care of yourself first.",
        "Quality over quantity - rest matters."
    ]
    
    SESSION_START_QUOTES = [
        "Ready to do great work! Let's go! 🚀",
        "Focus mode: activated!",
        "Your best session starts now.",
        "Time to make progress!",
        "You've got this!",
        "Let's create something amazing!",
        "New session, new possibilities.",
        "Your productivity journey continues!"
    ]
    
    @classmethod
    def get_break_quote(cls) -> str:
        """Get a random break quote"""
        return random.choice(cls.BREAK_QUOTES)
    
    @classmethod
    def get_achievement_quote(cls) -> str:
        """Get a random achievement quote"""
        return random.choice(cls.ACHIEVEMENT_QUOTES)
    
    @classmethod
    def get_fatigue_quote(cls) -> str:
        """Get a random fatigue quote"""
        return random.choice(cls.FATIGUE_QUOTES)
    
    @classmethod
    def get_session_start_quote(cls) -> str:
        """Get a random session start quote"""
        return random.choice(cls.SESSION_START_QUOTES)
    
    @classmethod
    def get_random_quote(cls) -> str:
        """Get any random quote"""
        all_quotes = (cls.BREAK_QUOTES + cls.ACHIEVEMENT_QUOTES + 
                     cls.FATIGUE_QUOTES + cls.SESSION_START_QUOTES)
        return random.choice(all_quotes)
