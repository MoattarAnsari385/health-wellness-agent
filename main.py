import asyncio
import os
from dotenv import load_dotenv

from agent import HealthWellnessPlannerAgent
from context import UserSessionContext


class HealthWellnessApp:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.agent = HealthWellnessPlannerAgent(self.api_key)
    
    async def initialize_user_session(self, name: str, uid: int) -> UserSessionContext:
        """Initialize a new user session"""
        context = UserSessionContext(name=name, uid=uid)
        await self.agent.initialize(context)
        return context
    
    async def stream_conversation(self, user_input: str) -> str:
        """Process conversation with the agent"""
        try:
            result = await self.agent.process_message(user_input)
            return result.get('response', 'No response generated')
        except Exception as e:
            return f"I encountered an error: {str(e)}. Please try again."
    
    async def demo_conversation(self):
        """Run a demo conversation showing the agent's capabilities"""
        print("🏥 Health & Wellness Planner (Gemini) Demo")
        print("=" * 50)
        
        # Initialize session
        context = await self.initialize_user_session("Demo User", 12345)
        print(f"✅ Session initialized for {context.name}")
        
        # Demo conversation flow
        demo_messages = [
            "Hi! I want to lose 5kg in the next month and improve my fitness",
            "Can you create a meal plan for me? I prefer vegetarian options", 
            "What workout routine would you recommend? I can exercise 4 days a week",
            "I have some knee pain when running, what should I do?",
            "I'd like to talk to a human coach about my progress"
        ]
        
        for message in demo_messages:
            print(f"\n👤 User: {message}")
            print("\n🤖 Agent:", end=" ")
            
            response = await self.stream_conversation(message)
            print(response)
            print("-" * 50)
            
            # Small delay for readability
            await asyncio.sleep(1)


async def main():
    """Main application entry point"""
    app = HealthWellnessApp()
    
    print("🚀 Starting Health & Wellness Planner with Gemini...")
    
    # Run demo conversation
    await app.demo_conversation()


if __name__ == "__main__":
    asyncio.run(main())