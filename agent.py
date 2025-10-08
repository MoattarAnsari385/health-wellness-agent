import google.generativeai as genai
import os
from typing import List, Dict, Any, Optional
import asyncio

from context import UserSessionContext
from hook import LifecycleHooks
from guardrails import OutputGuardrail

# Tools imports
from goal_analyzer import GoalAnalyzerTool
from meal_planner import MealPlannerTool
from workout_recommender import WorkoutRecommenderTool
from scheduler import CheckinSchedulerTool
from tracker import ProgressTrackerTool

# Agents imports
from escalation_agent import EscalationAgent
from nutrition_expert_agent import NutritionExpertAgent
from injury_support_agent import InjurySupportAgent


class HealthWellnessPlannerAgent:
    def __init__(self, api_key: str):
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Try different model names - LATEST VERSIONS
        self.model = self._get_working_model(api_key)
        
        self.hooks = None
        self.context = None
        
        # Initialize tools
        self.tools = {
            "goal_analyzer": GoalAnalyzerTool(),
            "meal_planner": MealPlannerTool(), 
            "workout_recommender": WorkoutRecommenderTool(),
            "scheduler": CheckinSchedulerTool(),
            "tracker": ProgressTrackerTool()
        }
        
        # Initialize specialized agents
        self.escalation_agent = EscalationAgent(api_key)
        self.nutrition_agent = NutritionExpertAgent(api_key)
        self.injury_agent = InjurySupportAgent(api_key)
        
        self.guardrail = OutputGuardrail()
    
    def _get_working_model(self, api_key: str):
        """Get a working Gemini model with fallback options"""
        genai.configure(api_key=api_key)
        
        # Try these model names in order
        model_names = [
            'gemini-1.5-pro',           # Latest
            'gemini-1.5-flash',         # Fast model
            'gemini-1.0-pro',           # Previous version
            'models/gemini-1.5-pro',    # Full path
            'models/gemini-1.0-pro',    # Full path
        ]
        
        for model_name in model_names:
            try:
                print(f"🔄 Trying model: {model_name}")
                model = genai.GenerativeModel(model_name)
                # Test with a simple prompt
                response = model.generate_content("Hello")
                print(f"✅ Success with model: {model_name}")
                return model
            except Exception as e:
                print(f"❌ Failed with {model_name}: {e}")
                continue
        
        # If all else fails, try to list and use first available model
        try:
            print("🔄 Listing all available models...")
            models = genai.list_models()
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    print(f"🎯 Trying available model: {model.name}")
                    try:
                        test_model = genai.GenerativeModel(model.name)
                        response = test_model.generate_content("Test")
                        print(f"✅ Using model: {model.name}")
                        return test_model
                    except:
                        continue
        except Exception as e:
            print(f"❌ Error listing models: {e}")
        
        raise Exception("❌ No working Gemini model found! Please check your API key and model availability.")
    
    async def initialize(self, user_context: UserSessionContext):
        """Initialize the agent with user context"""
        self.context = user_context
        self.hooks = LifecycleHooks(user_context)
        await self.hooks.on_agent_start("MainHealthAgent", "Initialization")
        print("✅ Agent initialized successfully!")
    
    async def process_message(self, user_input: str) -> Dict[str, Any]:
        """Process user message with handoff capability"""
        if not self.context:
            raise ValueError("Agent not initialized. Call initialize() first.")
        
        await self.hooks.on_agent_start("MainHealthAgent", user_input)
        
        # Check for handoff conditions
        handoff_result = await self._check_handoff_conditions(user_input)
        if handoff_result:
            return handoff_result
        
        # Process with main agent using Gemini
        try:
            # Create prompt with context
            prompt = self._create_prompt(user_input)
            
            print(f"🔄 Generating response for: {user_input[:50]}...")
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Check if any tools need to be called
            tool_response = await self._check_tool_calls(user_input, response.text)
            if tool_response:
                return tool_response
            
            # Update context
            await self._update_context_from_response(user_input, response.text)
            
            return {
                "agent": "MainHealthAgent",
                "response": response.text,
                "context_updated": True
            }
            
        except Exception as e:
            error_msg = f"I encountered an issue: {str(e)}. Please try again."
            print(f"❌ Error: {e}")
            return {
                "agent": "MainHealthAgent", 
                "response": error_msg,
                "error": str(e)
            }
    
    def _create_prompt(self, user_input: str) -> str:
        """Create prompt with user context"""
        context_str = f"""
        You are a comprehensive health and wellness planner. You help users with:
        1. Analyzing fitness and health goals
        2. Creating personalized meal plans  
        3. Generating workout routines
        4. Scheduling progress check-ins
        5. Tracking user progress
        
        User Context:
        - Name: {self.context.name}
        - Goal: {self.context.goal}
        - Diet Preferences: {self.context.diet_preferences}
        - Injury Notes: {self.context.injury_notes}
        
        User Message: {user_input}
        
        Please provide helpful, personalized health and wellness advice. Be encouraging and supportive in your responses.
        If the user mentions specific goals, injuries, or needs specialized help, acknowledge that you can assist.
        """
        return context_str
    
    async def _check_tool_calls(self, user_input: str, ai_response: str) -> Optional[Dict[str, Any]]:
        """Check if we need to call any tools based on user input"""
        user_input_lower = user_input.lower()
        
        # Check for goal analysis
        if any(keyword in user_input_lower for keyword in ['goal', 'target', 'want to', 'would like to']):
            await self.hooks.on_tool_start("GoalAnalyzerTool", {"user_input": user_input})
            result = self.tools["goal_analyzer"].analyze_goals(user_input)
            await self.hooks.on_tool_end("GoalAnalyzerTool", result)
            
            if result["status"] == "success":
                self.context.update_goal(result["analyzed_goal"])
                return {
                    "agent": "MainHealthAgent",
                    "response": f"{ai_response}\n\n🔍 **Goal Analysis:** I've analyzed your goals: {result['analyzed_goal']}",
                    "goal_analyzed": True
                }
        
        # Check for meal planning
        if any(keyword in user_input_lower for keyword in ['meal', 'diet', 'food', 'nutrition', 'eat']):
            if self.context.goal:
                diet_pref = self.context.diet_preferences or "balanced diet"
                await self.hooks.on_tool_start("MealPlannerTool", {
                    "goal_type": self.context.goal.get("goal_type", "general_fitness"),
                    "diet_preferences": diet_pref
                })
                result = await self.tools["meal_planner"].generate_meal_plan(
                    self.context.goal.get("goal_type", "general_fitness"),
                    diet_pref
                )
                await self.hooks.on_tool_end("MealPlannerTool", result)
                
                if result["status"] == "success":
                    self.context.meal_plan = result["meal_plan"]
                    meal_plan_str = "\n".join(result["meal_plan"][:3])  # Show first 3 days
                    return {
                        "agent": "MainHealthAgent",
                        "response": f"{ai_response}\n\n🍽️ **Meal Plan Preview:**\n{meal_plan_str}\n\n*Full 7-day plan generated!*",
                        "meal_plan_generated": True
                    }
        
        return None
    
    async def _check_handoff_conditions(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Check if message should be handed off to specialized agent"""
        user_input_lower = user_input.lower()
        
        # Check for human coach request
        if any(keyword in user_input_lower for keyword in ['human', 'coach', 'real person', 'talk to someone']):
            await self.hooks.on_handoff("MainHealthAgent", "EscalationAgent", "Human coach requested")
            return await self.escalation_agent.process(user_input, self.context.dict())
        
        # Check for complex nutrition questions
        nutrition_keywords = ['keto', 'paleo', 'vegan diet', 'macros', 'calorie counting', 'supplements']
        if any(keyword in user_input_lower for keyword in nutrition_keywords):
            await self.hooks.on_handoff("MainHealthAgent", "NutritionExpertAgent", "Complex nutrition question")
            return await self.nutrition_agent.process(user_input, self.context.dict())
        
        # Check for injury reports
        injury_keywords = ['injured', 'pain', 'hurt', 'sore', 'recovery', 'physical therapy']
        if any(keyword in user_input_lower for keyword in injury_keywords):
            await self.hooks.on_handoff("MainHealthAgent", "InjurySupportAgent", "Injury reported")
            return await self.injury_agent.process(user_input, self.context.dict())
        
        return None
    
    async def _update_context_from_response(self, user_input: str, response: str):
        """Update user context based on the interaction"""
        # Extract diet preferences
        if any(keyword in user_input.lower() for keyword in ['vegetarian', 'vegan', 'gluten', 'dairy']):
            self.context.diet_preferences = user_input
        
        # Extract potential goal updates
        if "goal" in user_input.lower() or "target" in user_input.lower():
            from guardrails import GoalValidator
            try:
                goal_data = GoalValidator.validate_goal_input(user_input)
                self.context.update_goal(goal_data)
            except Exception as e:
                await self.hooks.on_error("ContextUpdate", e)