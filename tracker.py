from typing import Dict, Any, List
from datetime import datetime


class ProgressTrackerTool:
    def __init__(self):
        self.name = "ProgressTrackerTool"
        self.description = "Log and track user progress updates"
    
    def track_progress(self, user_id: int, category: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log user progress updates and provide tracking insights"""
        
        timestamp = datetime.now().isoformat()
        
        progress_entry = {
            "user_id": user_id,
            "timestamp": timestamp,
            "category": category,
            "data": update_data,
            "milestones_achieved": self._check_milestones(category, update_data)
        }
        
        return {
            "progress_logged": True,
            "entry": progress_entry,
            "encouragement": self._get_encouragement(category),
            "next_steps": self._suggest_next_steps(category)
        }
    
    def _check_milestones(self, category: str, data: Dict[str, Any]) -> List[str]:
        """Check for achieved milestones"""
        milestones = []
        
        if category == "weight" and "current" in data and "initial" in data:
            loss = data["initial"] - data["current"]
            if loss >= 5:
                milestones.append("Lost 5+ units! Great work!")
        
        if category == "workout" and "consistency" in data:
            if data["consistency"] >= 80:
                milestones.append("Excellent workout consistency!")
        
        return milestones
    
    def _get_encouragement(self, category: str) -> str:
        encouragements = {
            "weight": "Every step counts! Keep up the great work on your weight journey!",
            "workout": "Your consistency is inspiring! The results will follow.",
            "nutrition": "Great choices on nutrition! Your body will thank you.", 
            "general": "You're making fantastic progress! Stay committed to your goals."
        }
        return encouragements.get(category, encouragements["general"])
    
    def _suggest_next_steps(self, category: str) -> List[str]:
        suggestions = {
            "weight": ["Continue tracking weekly", "Adjust calorie intake if plateaued"],
            "workout": ["Increase intensity gradually", "Try new exercises to avoid boredom"],
            "nutrition": ["Experiment with new healthy recipes", "Stay hydrated"]
        }
        return suggestions.get(category, ["Keep up the great work!", "Stay consistent"])