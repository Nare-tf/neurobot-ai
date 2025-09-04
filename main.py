import time
import random

# Import the enhanced chatbot (will fallback to basic if ML libs not available)
try:
    from enhanced_chatbot import NeuroBot
except ImportError:
    # Fallback to your original chatbot
    from enhanced_chatbot import NeuroBot
    print("⚠️  Using basic NeuroBot. For ML features, install requirements.txt")

from utils import clear_screen, typing_effect, get_user_input

def main():
    clear_screen()
    bot = NeuroBot()
    bot.welcome()
    
    # Enhanced help message based on capabilities
    if hasattr(bot, 'ml_enhanced') and bot.ml_enhanced:
        help_msg = "Type 'help' for commands, 'insights' for AI analysis, 'trends' for patterns, 'quit' to exit, or just chat!"
    else:
        help_msg = "Type 'help' for commands, 'quit' to exit, or just start chatting!"
    
    print(help_msg)
    print("=" * 60)
    
    while True:
        user_input = get_user_input()
        
        # Handle exit commands
        if user_input.lower() in ['quit', 'exit', 'bye']:
            bot.goodbye()
            break
            
        # Handle basic commands
        elif user_input.lower() == 'help':
            bot.show_help()
            
        elif user_input.lower() == 'mood':
            bot.mood_check()
            
        elif user_input.lower() == 'stats':
            bot.show_stats()
            
        # Handle ML-enhanced commands
        elif user_input.lower() == 'insights':
            if hasattr(bot, 'show_insights'):
                bot.show_insights()
            else:
                typing_effect("🤖 insights feature coming soon! for now, try 'stats'")
                
        elif user_input.lower() == 'trends':
            if hasattr(bot, 'show_trends'):
                bot.show_trends()
            else:
                typing_effect("🤖 trends analysis coming soon! for now, try 'stats'")
                
        # Easter eggs for fun
        elif user_input.lower() in ['debug', 'status', 'version']:
            if hasattr(bot, 'ml_enhanced') and bot.ml_enhanced:
                typing_effect("🚀 NeuroBot ML Enhanced v2.0 - AI-powered emotional wellness")
                typing_effect(f"📊 conversations: {len(bot.conversation_history)}")
                typing_effect("🧠 learning mode: ACTIVE")
            else:
                typing_effect("⚡ NeuroBot Classic v1.0 - reliable emotional support")
                typing_effect(f"📊 conversations: {len(bot.conversation_history)}")
                
        elif user_input.lower() in ['ml', 'ai', 'machine learning']:
            if hasattr(bot, 'ml_enhanced') and bot.ml_enhanced:
                typing_effect("🧠 yep! I'm using AI to:")
                typing_effect("• better understand your emotions")
                typing_effect("• learn what suggestions work for you")
                typing_effect("• find patterns in your mood")
                typing_effect("• give more personalized responses")
            else:
                typing_effect("🤖 I'd love ML powers! install the requirements.txt to unlock my full potential")
                
        # Handle regular conversation
        else:
            bot.respond(user_input)
        
        time.sleep(0.5)

if __name__ == "__main__":
    main()