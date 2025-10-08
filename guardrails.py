import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ValidationError


class GoalValidator(BaseModel):
    goal_type: str
    target: str
    timeframe: str
    intensity: str = "moderate"
    
    @classmethod
    def validate_goal_input(cls, user_input: str) -> Dict[str, Any]:
        """Validate and extract structured goal data from user input"""
        goal_types = ["weight_loss", "muscle_gain", "endurance", "general_fitness", "rehabilitation"]
        timeframes = ["1_week", "2_weeks", "1_month", "3_months", "6_months"]
        
        # Extract goal type
        goal_type = "general_fitness"
        for gt in goal_types:
            if gt in user_input.lower():
                goal_type = gt
                break
        
        # Extract timeframe
        timeframe = "1_month"
        if "week" in user_input.lower():
            if "2" in user_input or "two" in user_input:
                timeframe = "2_weeks"
            else:
                timeframe = "1_week"
        elif "month" in user_input.lower():
            if "3" in user_input or "three" in user_input:
                timeframe = "3_months"
            elif "6" in user_input or "six" in user_input:
                timeframe = "6_months"
            else:
                timeframe = "1_month"
        
        # Extract target
        target_match = re.search(r'(\d+)\s*(kg|lb|pounds?|kilos?)', user_input.lower())
        target = "improve fitness"
        if target_match:
            target = f"{target_match.group(1)} {target_match.group(2)}"
        
        return {
            "goal_type": goal_type,
            "target": target,
            "timeframe": timeframe,
            "intensity": "moderate"
        }


class OutputGuardrail:
    @staticmethod
    def ensure_json_output(output: Any) -> Dict[str, Any]:
        """Ensure output is valid JSON-serializable structure"""
        if isinstance(output, dict):
            return output
        elif isinstance(output, str):
            try:
                import json
                return json.loads(output)
            except:
                return {"response": output}
        else:
            return {"response": str(output)}
    
    @staticmethod
    def validate_meal_plan_output(plan: List[str]) -> bool:
        """Validate meal plan structure"""
        if not isinstance(plan, list):
            return False
        if len(plan) != 7:
            return False
        return all(isinstance(day, str) and len(day) > 0 for day in plan)