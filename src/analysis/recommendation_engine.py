"""
Recommendation engine for suggesting refreshing activities based on fatigue metrics.
"""
from typing import List, Optional, Dict, Tuple
import random
from datetime import datetime

from src.models.fatigue_score import FatigueScore
from src.ui.activities.activity_definitions import (
    Activity, ActivityCategory, ACTIVITIES, get_all_activities, get_activities_by_category
)
from src.utils.logger import default_logger as logger


class RecommendationEngine:
    """
    Intelligent engine for recommending activities based on user state.
    
    Implements a two-tier system:
    1. Specific Triggers: High readings in specific metrics (e.g. eye strain)
       trigger specific related activities.
    2. General Recommendation: If no specific triggers, suggest activities
       based on overall fatigue score and context.
    """
    
    def __init__(self):
        self.activities = get_all_activities()
        
    def get_recommendations(self, score: FatigueScore, count: int = 3) -> List[Activity]:
        """
        Get a list of recommended activities based on fatigue score.
        
        Args:
            score: Current fatigue score object with factors
            count: Number of recommendations to return
            
        Returns:
            List of Activity objects, ranked by relevance
        """
        recommended_activities = []
        
        # 1. Check specific triggers (Tier 1)
        trigger_recommendations = self._check_specific_triggers(score)
        recommended_activities.extend(trigger_recommendations)
        
        # 2. Get general recommendations (Tier 2) to fill the rest
        if len(recommended_activities) < count:
            needed = count - len(recommended_activities)
            general_recs = self._get_general_recommendations(score, needed, exclude_ids=[a.id for a in recommended_activities])
            recommended_activities.extend(general_recs)
            
        return recommended_activities[:count]
    
    def get_top_recommendation(self, score: FatigueScore) -> Optional[Activity]:
        """Get the single best recommendation"""
        recs = self.get_recommendations(score, count=1)
        return recs[0] if recs else None
        
    def _check_specific_triggers(self, score: FatigueScore) -> List[Activity]:
        """Check for specific metric spikes that demand specific solutions"""
        triggers = []
        factors = score.factors
        
        # Trigger: High Eye Strain
        # If blink factor is high or eye strain is explicitly mentioned
        eye_strain = factors.get('eye_strain', 0)
        blink_rate = factors.get('blink_rate', 15) # Default to 15 if missing
        
        if eye_strain > 15 or blink_rate < 8:
            logger.debug(f"Trigger: Eye strain detected (strain={eye_strain}, blink={blink_rate})")
            triggers.extend(get_activities_by_category(ActivityCategory.EYE))
            
        # Trigger: High Activity Intensity (Mental/Physical Fatigue)
        # If input intensity was very high
        intensity = factors.get('activity_intensity', 0)
        if intensity > 15:
            logger.debug(f"Trigger: High intensity activity detected ({intensity})")
            # Suggest breathing or meditation to calm down
            triggers.extend(get_activities_by_category(ActivityCategory.BREATHING))
            triggers.extend(get_activities_by_category(ActivityCategory.MEDITATION))
            
        # Trigger: Long Session (Physical stiffness)
        # If session duration is contributing significantly
        duration_factor = factors.get('session_duration', 0)
        if duration_factor > 10:
            logger.debug("Trigger: Long session detected")
            # Suggest physical movement
            triggers.extend(get_activities_by_category(ActivityCategory.PHYSICAL))
            
        # Trigger: High Stress/Anxiety (inferred from high typing speed + erratics? For now just fatigue level)
        if score.score > 80:
             # For critical fatigue, suggest 'Combo' activities for full reset
             triggers.extend(get_activities_by_category(ActivityCategory.COMBO))

        # Shuffle specific triggers to vary suggestions
        random.shuffle(triggers)
        return triggers

    def _get_general_recommendations(self, score: FatigueScore, count: int, exclude_ids: List[str]) -> List[Activity]:
        """Get general recommendations based on fatigue level context"""
        candidates = []
        
        level = score.get_level()
        
        if level == "Low":
            # Prevention: Gentle stretches, simple eye rules
            candidates.extend(get_activities_by_category(ActivityCategory.EYE))
            candidates.extend(get_activities_by_category(ActivityCategory.PHYSICAL))
            
        elif level == "Moderate":
            # Maintenance: Breathing, Walking
            candidates.extend(get_activities_by_category(ActivityCategory.BREATHING))
            candidates.extend(get_activities_by_category(ActivityCategory.PHYSICAL))
            
        elif level == "High":
            # Recovery: Meditation, longer breaks
            candidates.extend(get_activities_by_category(ActivityCategory.MEDITATION))
            candidates.extend(get_activities_by_category(ActivityCategory.COMBO))
            
        else: # Critical
            # Full Stop: Combo energizers, longest breaks
            candidates.extend(get_activities_by_category(ActivityCategory.COMBO))
            candidates.extend(get_activities_by_category(ActivityCategory.MEDITATION))

        # Filter exclusions
        candidates = [a for a in candidates if a.id not in exclude_ids]
        
        # Deduplicate candidates if categories overlapped
        unique_candidates = []
        seen_ids = set()
        for c in candidates:
            if c.id not in seen_ids:
                unique_candidates.append(c)
                seen_ids.add(c.id)
        
        # Randomize selection
        random.shuffle(unique_candidates)
        return unique_candidates[:count]
