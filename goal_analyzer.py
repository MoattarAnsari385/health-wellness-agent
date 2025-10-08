from typing import Dict, Any
from pydantic import BaseModel
from guardrails import GoalValidator


class GoalAnalyzerTool:
    def __init__(self):
        self.name = "GoalAnalyzerTool"
        self.description = "Analyze user's health and fitness goals to extract structured information"
    
    def analyze_goals(self, user_input: str) -> Dict[str, Any]:
        """Extract structured fitness and health goals from user input"""
        try:
            validated_goal = GoalValidator.validate_goal_input(user_input)
            
            if "injured" in user_input.lower() or "pain" in user_input.lower():
                validated_goal["requires_special_attention"] = True
            else:
                validated_goal["requires_special_attention"] = False
            
            if "diet" in user_input.lower() or "nutrition" in user_input.lower():
                validated_goal["nutrition_focus"] = True
            else:
                validated_goal["nutrition_focus"] = False
            
            return {
                "status": "success",
                "analyzed_goal": validated_goal,
                "recommendations": [
                    "Consider consulting with nutrition expert for detailed meal planning",
                    "Regular progress tracking recommended"
                ]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "analyzed_goal": None
            }