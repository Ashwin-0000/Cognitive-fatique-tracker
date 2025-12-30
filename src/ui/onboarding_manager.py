"""Onboarding tutorial system"""
from pathlib import Path
from typing import Optional, List, Dict
import json


class OnboardingManager:
    """Manages first-time user onboarding"""
    
    TUTORIAL_STEPS = [
        {
            'id': 'welcome',
            'title': 'Welcome to Cognitive Fatigue Tracker! 🧠',
            'content': 'This app helps you maintain productivity while preventing burnout by tracking your work patterns and reminding you to take breaks.',
            'action': 'Get Started'
        },
        {
            'id': 'start_session',
            'title': 'Starting a Session',
            'content': 'Click "Start Session" to begin tracking your work. The app will monitor your activity and calculate fatigue levels in real-time.',
            'action': 'Next'
        },
        {
            'id': 'breaks',
            'title': 'Taking Breaks',
            'content': 'Regular breaks are essential! The app will remind you when it\'s time for a break. Click "Take Break" to pause tracking.',
            'action': 'Next'
        },
        {
            'id': 'dashboard',
            'title': 'Understanding Your Dashboard',
            'content': 'Monitor your fatigue score, work time, activity rate, and other metrics in real-time. Charts show your trends over time.',
            'action': 'Next'
        },
        {
            'id': 'keyboard',
            'title': 'Keyboard Shortcuts ⌨️',
            'content': 'Use shortcuts for quick actions:\n• Ctrl+B: Take Break\n• Ctrl+S: Settings\n• Ctrl+Q: Quit\n• F1: Show all shortcuts',
            'action': 'Next'
        },
        {
            'id': 'settings',
            'title': 'Customize Your Experience',
            'content': 'Visit Settings to adjust work intervals, break durations, alert preferences, and enable features like eye tracking.',
            'action': 'Next'
        },
        {
            'id': 'complete',
            'title': 'You\'re Ready! 🎉',
            'content': 'Start your first session and build healthy work habits. Remember: productivity is a marathon, not a sprint!',
            'action': 'Start First Session'
        }
    ]
    
    def __init__(self, onboarding_file: Optional[Path] = None):
        """
        Initialize onboarding manager.
        
        Args:
            onboarding_file: File to track onboarding status
        """
        if onboarding_file is None:
            onboarding_file = Path(__file__).parent.parent.parent / "data" / "onboarding.json"
        
        self.onboarding_file = Path(onboarding_file)
        self.onboarding_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.status = self._load_status()
    
    def _load_status(self) -> Dict:
        """Load onboarding status"""
        if self.onboarding_file.exists():
            try:
                with open(self.onboarding_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            'completed': False,
            'current_step': 0,
            'skipped': False
        }
    
    def _save_status(self):
        """Save onboarding status"""
        try:
            with open(self.onboarding_file, 'w') as f:
                json.dump(self.status, f, indent=2)
        except Exception:
            pass
    
    def should_show_onboarding(self) -> bool:
        """Check if onboarding should be shown"""
        return not self.status['completed'] and not self.status['skipped']
    
    def get_current_step(self) -> Dict:
        """Get current tutorial step"""
        step_index = self.status['current_step']
        if step_index < len(self.TUTORIAL_STEPS):
            return self.TUTORIAL_STEPS[step_index]
        return self.TUTORIAL_STEPS[-1]
    
    def next_step(self):
        """Move to next tutorial step"""
        self.status['current_step'] += 1
        if self.status['current_step'] >= len(self.TUTORIAL_STEPS):
            self.complete_onboarding()
        else:
            self._save_status()
    
    def skip_onboarding(self):
        """Skip the onboarding tutorial"""
        self.status['skipped'] = True
        self._save_status()
    
    def complete_onboarding(self):
        """Mark onboarding as completed"""
        self.status['completed'] = True
        self._save_status()
    
    def reset_onboarding(self):
        """Reset onboarding to start again"""
        self.status = {
            'completed': False,
            'current_step': 0,
            'skipped': False
        }
        self._save_status()
    
    def get_all_steps(self) -> List[Dict]:
        """Get all tutorial steps"""
        return self.TUTORIAL_STEPS
