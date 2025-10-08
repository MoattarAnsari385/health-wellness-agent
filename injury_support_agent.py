import google.generativeai as genai
from typing import Dict, Any


class InjurySupportAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        
        # Use latest model names
        try:
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        except:
            try:
                self.model = genai.GenerativeModel('gemini-1.0-pro')
            except:
                self.model = genai.GenerativeModel('gemini-pro')
                
        self.agent_name = "InjurySupportAgent"
    
    async def process(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle injury reports and provide supportive guidance"""
        
        prompt = f"""
        You are a rehabilitation and injury support specialist.
        
        User Context: {context}
        Injury Report: {user_input}
        
        Provide gentle guidance for injuries, emphasize rest and professional medical advice, 
        and suggest safe alternative exercises. Always recommend consulting healthcare providers.
        Be empathetic and cautious.
        """
        
        response = self.model.generate_content(prompt)
        message = response.text
        
        return {
            "agent": self.agent_name,
            "response": message,
            "urgency_level": self._assess_urgency(user_input),
            "immediate_actions": ["Rest affected area", "Apply ice if acute", "Consult medical professional"],
            "alternative_exercises": ["Light stretching", "Non-weight bearing activities", "Breathing exercises"]
        }
    
    def _assess_urgency(self, user_input: str) -> str:
        """Assess injury urgency level"""
        urgent_keywords = ["severe", "sharp", "unable to move", "swelling", "numbness"]
        if any(keyword in user_input.lower() for keyword in urgent_keywords):
            return "high"
        return "medium"