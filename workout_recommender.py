from typing import Dict, Any, List


class WorkoutRecommenderTool:
    def __init__(self):
        self.name = "WorkoutRecommenderTool"
        self.description = "Generate personalized weekly workout routines"
    
    def generate_workouts(self, goal_type: str, intensity: str, days_per_week: int = 4) -> Dict[str, Any]:
        """Generate weekly workout plan based on goals and intensity"""
        
        workout_templates = {
            "weight_loss": {
                "cardio": ["HIIT", "Running", "Cycling", "Swimming"],
                "strength": ["Full-body circuits", "Bodyweight exercises"],
                "rest_days": ["Active recovery", "Light walking"]
            },
            "muscle_gain": {
                "strength": ["Chest & Triceps", "Back & Biceps", "Legs", "Shoulders"],
                "cardio": ["Light cardio 2x week"],
                "rest_days": ["Complete rest", "Stretching"]
            },
            "endurance": {
                "cardio": ["Long runs", "Cycling", "Swimming intervals"],
                "strength": ["Full-body endurance circuits"],
                "rest_days": ["Active recovery"]
            }
        }
        
        template = workout_templates.get(goal_type, workout_templates["general_fitness"])
        
        workouts = []
        for i in range(days_per_week):
            if i % 2 == 0:
                workout_type = template["strength"][i % len(template["strength"])]
                workouts.append(f"Day {i+1}: Strength Training - {workout_type}")
            else:
                workout_type = template["cardio"][i % len(template["cardio"])]
                workouts.append(f"Day {i+1}: Cardio - {workout_type}")
        
        return {
            "weekly_workouts": workouts,
            "goal_specific": goal_type,
            "intensity_level": intensity,
            "recovery_days": 7 - days_per_week,
            "recommendations": [
                "Stay consistent with your schedule",
                "Listen to your body and adjust as needed", 
                "Proper warm-up and cool-down essential"
            ]
        }