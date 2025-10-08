import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
import sys

# Load environment variables - Streamlit compatible
try:
    # For Streamlit Cloud
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    # For local development
    load_dotenv()
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class StreamlitApp:
    def __init__(self):
        if not GEMINI_API_KEY:
            st.error("❌ GEMINI_API_KEY not found. Please check your secrets configuration.")
            st.stop()
        
        self.api_key = GEMINI_API_KEY
    
    async def initialize_agent(self, user_name: str):
        """Initialize agent for user session"""
        try:
            from agent import HealthWellnessPlannerAgent
            from context import UserSessionContext
            
            st.session_state.agent = HealthWellnessPlannerAgent(self.api_key)
            st.session_state.context = UserSessionContext(
                name=user_name,
                uid=hash(user_name)
            )
            await st.session_state.agent.initialize(st.session_state.context)
            return True
        except Exception as e:
            st.error(f"❌ Agent initialization failed: {str(e)}")
            return False
    
    async def process_message(self, user_input: str):
        """Process user message and return response"""
        try:
            if st.session_state.get('agent'):
                response = await st.session_state.agent.process_message(user_input)
                return response.get('response', 'No response generated')
            return "❌ Agent not initialized. Please start a session first."
        except Exception as e:
            return f"❌ Error processing message: {str(e)}"
    
    def run(self):
        """Run the Streamlit app"""
        st.set_page_config(
            page_title="Health & Wellness Planner",
            page_icon="🏥",
            layout="centered",
            initial_sidebar_state="expanded"
        )
        
        # App title and description
        st.title("🏥 Health & Wellness Planner")
        st.markdown("""
        Your personal AI health assistant! Get personalized:
        - 🥗 **Meal plans**
        - 💪 **Workout routines**  
        - 🎯 **Goal tracking**
        - 📊 **Progress monitoring**
        """)
        
        # Initialize session state
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if "session_started" not in st.session_state:
            st.session_state.session_started = False
        
        # Sidebar for user profile
        with st.sidebar:
            st.header("👤 User Profile")
            user_name = st.text_input("Your Name", value="Wellness User", key="user_name")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚀 Start Session", type="primary"):
                    with st.spinner("Initializing your wellness session..."):
                        success = asyncio.run(self.initialize_agent(user_name))
                        if success:
                            st.session_state.session_started = True
                            st.success(f"✅ Session started for {user_name}!")
                        else:
                            st.session_state.session_started = False
                            st.error("❌ Failed to start session")
            
            with col2:
                if st.button("🔄 Reset Session"):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()
            
            st.markdown("---")
            st.header("ℹ️ How to Use")
            st.markdown("""
            1. **Enter your name**
            2. **Click 'Start Session'**
            3. **Start chatting below!**
            
            You can ask about:
            - Weight loss goals
            - Meal plans
            - Workout routines
            - Injury advice
            - Progress tracking
            """)
            
            st.markdown("---")
            st.header("💡 Sample Questions")
            sample_questions = [
                "I want to lose 5kg in one month",
                "Create a vegetarian meal plan for me",
                "I have knee pain, what exercises are safe?",
                "Suggest a 4-day workout routine"
            ]
            
            for question in sample_questions:
                if st.button(question, key=f"sample_{question}"):
                    # Add sample question to chat
                    st.session_state.messages.append({"role": "user", "content": question})
                    # Trigger processing
                    st.rerun()
        
        # Main chat interface
        st.header("💬 Chat with Your Wellness Assistant")
        
        # Display session status
        if st.session_state.get('session_started'):
            st.success("✅ Session Active - You can start chatting!")
        else:
            st.warning("⚠️ Please start a session from the sidebar first!")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("What are your health goals?", disabled=not st.session_state.get('session_started')):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("🤖 Thinking..."):
                    try:
                        response = asyncio.run(self.process_message(prompt))
                        st.markdown(response)
                        
                        # Add assistant response to chat history
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        error_msg = f"❌ Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})

def main():
    app = StreamlitApp()
    app.run()

if __name__ == "__main__":
    main()