import google.generativeai as genai
from typing import Dict, Any


class NutritionExpertAgent:
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
                
        self.agent_name = "NutritionExpertAgent"
    
    async def process(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle complex nutrition and diet questions"""
        
        prompt = f"""
        You are a certified nutrition expert. Provide detailed, scientifically-backed nutrition advice.
        
        User Context: {context}
        Nutrition Question: {user_input}
        
        Consider dietary restrictions, goals, and preferences. Be specific about portions, timing, and nutritional balance.
        Provide practical advice that the user can implement immediately.
        """
        
        response = self.model.generate_content(prompt)
        message = response.text
        
        return {
            "agent": self.agent_name,
            "response": message,
            "expertise_level": "certified_nutritionist",
            "recommendations": ["Consult with healthcare provider for medical conditions"],
            "supplement_advice": "General multivitamin recommended based on diet"
        }