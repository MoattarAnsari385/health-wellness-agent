from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class UserSessionContext(BaseModel):
    name: str
    uid: int
    goal: Optional[dict] = None
    diet_preferences: Optional[str] = None
    workout_plan: Optional[dict] = None
    meal_plan: Optional[List[str]] = None
    injury_notes: Optional[str] = None
    handoff_logs: List[str] = []
    progress_logs: List[Dict[str, str]] = []
    created_at: str = datetime.now().isoformat()
    
    def add_handoff_log(self, message: str):
        self.handoff_logs.append(f"{datetime.now().isoformat()}: {message}")
    
    def add_progress_log(self, category: str, message: str):
        self.progress_logs.append({
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "message": message
        })
    
    def update_goal(self, goal_data: dict):
        self.goal = goal_data
        self.add_progress_log("goal", f"Goal updated: {goal_data}")