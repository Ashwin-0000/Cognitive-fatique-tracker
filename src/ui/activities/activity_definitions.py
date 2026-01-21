"""Activity definitions for cognitive refresh exercises"""
from dataclasses import dataclass
from typing import List
from enum import Enum


class ActivityCategory(Enum):
    """Category of refresh activity"""
    EYE = "eye"
    BREATHING = "breathing"
    PHYSICAL = "physical"
    MEDITATION = "meditation"
    COMBO = "combo"


@dataclass
class Activity:
    """Definition of a refresh activity"""
    id: str
    name: str
    category: ActivityCategory
    description: str
    duration_seconds: int
    instructions: List[str]
    benefits: str
    effectiveness_rating: float  # 1-5 based on research
    color: str  # UI color theme


# All available activities
ACTIVITIES = {
    "eye_20_20_20": Activity(
        id="eye_20_20_20",
        name="20-20-20 Eye Rule",
        category=ActivityCategory.EYE,
        description="Look at something 20 feet away for 20 seconds to relax your eye muscles",
        duration_seconds=20,
        instructions=[
            "Find a distant object (at least 20 feet away)",
            "It could be out the window or across the room",
            "Focus on it for 20 seconds",
            "Blink naturally while looking",
            "Return to your work when timer completes"
        ],
        benefits="Relaxes eye muscles, reduces eye strain, prevents computer vision syndrome",
        effectiveness_rating=4.0,
        color="#3B82F6"  # Blue
    ),
    
    "eye_rapid_blink": Activity(
        id="eye_rapid_blink",
        name="Rapid Blinking Exercise",
        category=ActivityCategory.EYE,
        description="Quick blinking to re-moisturize your eyes",
        duration_seconds=30,
        instructions=[
            "Blink rapidly 15 times",
            "Take a 5 second pause",
            "Repeat 2 more times",
            "Close your eyes gently for final 5 seconds"
        ],
        benefits="Re-moisturizes eyes, reduces dryness from reduced blink rate during screen use",
        effectiveness_rating=3.5,
        color="#3B82F6"
    ),
    
    "breathing_physiological_sigh": Activity(
        id="breathing_physiological_sigh",
        name="Physiological Sigh",
        category=ActivityCategory.BREATHING,
        description="Quick stress relief through double-inhale breathing technique",
        duration_seconds=45,
        instructions=[
            "Take a deep breath in through your nose",
            "Take another quick breath in (double inhale)",
            "Slowly exhale through your mouth",
            "Repeat this cycle 3 times",
            "Feel the tension release with each exhale"
        ],
        benefits="Rapid stress reduction, decreases heart rate, immediate sense of calm",
        effectiveness_rating=5.0,
        color="#10B981"  # Green
    ),
    
    "breathing_deep": Activity(
        id="breathing_deep",
        name="Deep Diaphragmatic Breathing",
        category=ActivityCategory.BREATHING,
        description="Deep abdominal breathing to activate your relaxation response",
        duration_seconds=300,
        instructions=[
            "Sit comfortably with one hand on chest, one on belly",
            "Breathe in deeply through nose (belly should rise, not chest)",
            "Hold for 2 seconds",
            "Exhale slowly through mouth (belly falls)",
            "Continue this pattern for 5 minutes",
            "If your mind wanders, gently return focus to breath"
        ],
        benefits="Reduces cortisol levels, lowers blood pressure, improves focus and mental clarity",
        effectiveness_rating=5.0,
        color="#10B981"
    ),
    
    "breathing_box": Activity(
        id="breathing_box",
        name="Box Breathing (4-4-4-4)",
        category=ActivityCategory.BREATHING,
        description="Structured breathing pattern used by Navy SEALs for focus",
        duration_seconds=120,
        instructions=[
            "Inhale through nose for 4 counts",
            "Hold breath for 4 counts",
            "Exhale through mouth for 4 counts",
            "Hold empty for 4 counts",
            "Repeat this cycle for 2 minutes",
            "Visualize drawing a box with each phase"
        ],
        benefits="Reduces stress, improves concentration, balances nervous system",
        effectiveness_rating=4.5,
        color="#10B981"
    ),
    
    "physical_shoulder_release": Activity(
        id="physical_shoulder_release",
        name="Shoulder & Neck Release",
        category=ActivityCategory.PHYSICAL,
        description="Quick stretches to release upper body tension",
        duration_seconds=90,
        instructions=[
            "Roll shoulders backward slowly 5 times",
            "Roll shoulders forward slowly 5 times",
            "Tilt head gently to right, hold 3 seconds",
            "Tilt head gently to left, hold 3 seconds",
            "Repeat the sequence 2 more times",
            "Move slowly and breathe naturally"
        ],
        benefits="Releases trapezius tension, improves circulation to brain, reduces headaches",
        effectiveness_rating=4.0,
        color="#F59E0B"  # Orange
    ),
    
    "physical_wrist_stretch": Activity(
        id="physical_wrist_stretch",
        name="Wrist & Finger Refresher",
        category=ActivityCategory.PHYSICAL,
        description="Prevent repetitive strain with wrist exercises",
        duration_seconds=60,
        instructions=[
            "Extend both arms forward, palms down",
            "Bend wrists up and down 5 times",
            "Make 5 tight fists",
            "Spread fingers wide for 5 seconds",
            "Rotate wrists clockwise 5 times",
            "Rotate wrists counterclockwise 5 times"
        ],
        benefits="Prevents carpal tunnel syndrome, releases repetitive strain from typing",
        effectiveness_rating=3.5,
        color="#F59E0B"
    ),
    
    "physical_walk": Activity(
        id="physical_walk",
        name="Quick Walk Break",
        category=ActivityCategory.PHYSICAL,
        description="2-minute walking break to boost circulation",
        duration_seconds=120,
        instructions=[
            "Stand up from your desk",
            "Walk around your space at a comfortable pace",
            "Swing your arms naturally",
            "Focus on your steps and breathing",
            "Notice how your body feels",
            "Return when timer completes"
        ],
        benefits="Boosts circulation, increases oxygen to brain, improves alertness",
        effectiveness_rating=4.5,
        color="#F59E0B"
    ),
    
    "physical_desk_exercises": Activity(
        id="physical_desk_exercises",
        name="Desk Exercise Combo",
        category=ActivityCategory.PHYSICAL,
        description="Complete upper and lower body stretches at your desk",
        duration_seconds=180,
        instructions=[
            "Stand behind your chair",
            "Do 10 air squats (pretend to sit)",
            "Do 10 desk push-ups (hands on desk)",
            "Seated: extend one leg straight, hold 5 sec, repeat 10x each",
            "Reach arms overhead, hold 10 seconds",
            "Finish with gentle twists to each side"
        ],
        benefits="Full body activation, increases energy, combats prolonged sitting",
        effectiveness_rating=4.5,
        color="#F59E0B"
    ),
    
    "meditation_mindful_breathing": Activity(
        id="meditation_mindful_breathing",
        name="Mindful Breathing Meditation",
        category=ActivityCategory.MEDITATION,
        description="5-minute guided mindfulness to clear mental clutter",
        duration_seconds=300,
        instructions=[
            "Sit comfortably and close your eyes",
            "Take 3 deep breaths to settle in",
            "Focus on your natural breath - don't control it",
            "Notice the sensation of air flowing in and out",
            "When thoughts arise, acknowledge them without judgment",
            "Gently return your attention to your breath",
            "Continue for 5 minutes",
            "End with 3 deep breaths and slowly open eyes"
        ],
        benefits="Enhances focus, reduces mental clutter, improves cognitive flexibility",
        effectiveness_rating=4.5,
        color="#8B5CF6"  # Purple
    ),
    
    "meditation_body_scan": Activity(
        id="meditation_body_scan",
        name="Quick Body Scan",
        category=ActivityCategory.MEDITATION,
        description="3-minute body awareness meditation",
        duration_seconds=180,
        instructions=[
            "Close your eyes and take a deep breath",
            "Start at your feet - notice any sensations",
            "Slowly move attention up to your legs",
            "Notice your torso, chest, breathing",
            "Feel your shoulders, arms, hands",
            "Notice your neck, face, head",
            "Take one final deep breath",
            "Slowly open your eyes"
        ],
        benefits="Releases physical tension, grounds awareness, promotes relaxation",
        effectiveness_rating=4.0,
        color="#8B5CF6"
    ),
    
    "combo_quick_refresh": Activity(
        id="combo_quick_refresh",
        name="Complete Quick Refresh",
        category=ActivityCategory.COMBO,
        description="3-minute combination targeting eyes, breathing, and body",
        duration_seconds=180,
        instructions=[
            "Minute 1: 20-20-20 eye rule + rapid blinking (15x)",
            "Minute 2: 3 physiological sighs + shoulder rolls",
            "Minute 3: Stand and march in place with arm swings",
            "Take a final deep breath and smile!"
        ],
        benefits="Complete refresh addressing multiple fatigue sources simultaneously",
        effectiveness_rating=5.0,
        color="#EC4899"  # Pink
    ),
    
    "combo_energizer": Activity(
        id="combo_energizer",
        name="Energy Boost Combo",
        category=ActivityCategory.COMBO,
        description="5-minute intensive refresh for high fatigue",
        duration_seconds=300,
        instructions=[
            "Minutes 1-2: Deep breathing (12 cycles)",
            "Minute 3: Shoulder, neck, and wrist stretches",
            "Minute 4: 20 jumping jacks or marching in place",
            "Minute 5: Eye exercises + final relaxation breath"
        ],
        benefits="Maximum energy boost, comprehensive fatigue relief",
        effectiveness_rating=5.0,
        color="#EC4899"
    )
}


def get_activities_by_category(category: ActivityCategory) -> List[Activity]:
    """Get all activities in a specific category"""
    return [a for a in ACTIVITIES.values() if a.category == category]


def get_activity_by_id(activity_id: str) -> Activity:
    """Get a specific activity by ID"""
    return ACTIVITIES.get(activity_id)


def get_all_activities() -> List[Activity]:
    """Get all activities"""
    return list(ACTIVITIES.values())
