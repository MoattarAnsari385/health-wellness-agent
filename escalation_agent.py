import google.generativeai as genai
from typing import Dict, Any


class EscalationAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.agent_name = "EscalationAgent"
        
        # Simple model selection
        try:
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        except:
            try:
                self.model = genai.GenerativeModel('gemini-1.0-pro')
            except:
                # Use any available model
                models = genai.list_models()
                for model in models:
                    if 'generateContent' in model.supported_generation_methods:
                        self.model = genai.GenerativeModel(model.name)
                        break
                else:
                    raise Exception("No working model found")
    
    async def process(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle requests for human coach escalation"""
        
        prompt = f"""
        You are a health coach escalation specialist. A user has requested to speak with a human coach.
        
        User Context: {context}
        User Request: {user_input}
        
        Please acknowledge their request, provide reassurance, and explain what they can expect from a human coach.
        Be empathetic and professional.
        """
        
        try:
            response = self.model.generate_content(prompt)
            message = response.text
            
            return {
                "agent": self.agent_name,
                "response": message,
                "action_taken": "escalated_to_human_coach",
                "follow_up": "A human coach will contact you within 24 hours.",
                "priority": "medium"
            }
        except Exception as e:
            return {
                "agent": self.agent_name,
                "response": f"I understand you'd like to speak with a human coach. Our team will contact you shortly. Error: {str(e)}",
                "error": str(e)
            }