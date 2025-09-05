import random
import time
import json
import os
from datetime import datetime
from textblob import TextBlob

# Try to import ML libraries
try:
    from transformers import pipeline, GPT2LMHeadModel, GPT2Tokenizer
    import torch
    ML_AVAILABLE = True
    print("🧠 AI conversation engine loading...")
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  For full AI features, install: pip install transformers torch")

from utils import typing_effect, print_bot_message, print_separator

class ConversationalNeuroBot:
    def __init__(self):
        self.name = "NeuroBot"
        self.user_name = None
        self.conversation_history = []
        self.session_start = datetime.now()
        self.personality_context = ""
        self.user_context = {}
        
        # Initialize AI models
        self.setup_ai_models()
        
        # Load conversation history
        self.load_conversation_history()
        
        # Set up personality context
        self.setup_personality()
    
    def setup_ai_models(self):
        """Initialize AI conversation models"""
        if not ML_AVAILABLE:
            self.ai_model = None
            self.tokenizer = None
            return
        
        try:
            # Use a lightweight conversational model
            model_name = "microsoft/DialoGPT-small"  # Fast, good for conversation
            
            print("🤖 Loading AI conversation model...")
            self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
            self.ai_model = GPT2LMHeadModel.from_pretrained(model_name)
            
            # Add padding token
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
            print("✅ AI conversation engine ready!")
            
        except Exception as e:
            print(f"⚠️  Couldn't load full AI model: {e}")
            print("🔄 Falling back to rule-based responses...")
            self.ai_model = None
            self.tokenizer = None
    
    def setup_personality(self):
        """Define the bot's personality and mental health focus"""
        self.personality_context = """
        I'm NeuroBot, a caring AI companion focused on mental health and emotional wellness. 
        I communicate casually like a supportive friend - using modern language, being genuine, and avoiding clinical jargon.
        My core traits:
        - Empathetic and non-judgmental
        - Practical and solution-oriented
        - Uses casual, friendly language (like 'fr', 'ngl', 'tbh' naturally)
        - Focuses on mental health, stress relief, anxiety management, depression support
        - Offers real techniques and genuine support
        - Remembers what users tell me and builds on our conversations
        - Never gives medical advice, but provides emotional support and coping strategies
        """
    
    def generate_ai_response(self, user_input, conversation_context=""):
        """Generate response using AI model"""
        if not self.ai_model or not ML_AVAILABLE:
            return self.generate_fallback_response(user_input)
        
        try:
            # Build context for the AI
            context = f"{self.personality_context}\n\nConversation context: {conversation_context}\n"
            context += f"User: {user_input}\nNeuroBot:"
            
            # Tokenize and generate
            inputs = self.tokenizer.encode(context, return_tensors='pt', truncation=True, max_length=512)
            
            # Generate response
            with torch.no_grad():
                outputs = self.ai_model.generate(
                    inputs, 
                    max_length=inputs.shape[1] + 50,  # Keep responses reasonable
                    num_return_sequences=1,
                    temperature=0.8,  # Creative but not too random
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    no_repeat_ngram_size=3  # Avoid repetition
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract just the bot's response
            bot_response = response[len(context):].strip()
            
            # Clean up the response
            bot_response = self.clean_ai_response(bot_response, user_input)
            
            return bot_response
            
        except Exception as e:
            print(f"AI generation error: {e}")
            return self.generate_fallback_response(user_input)
    
    def clean_ai_response(self, response, user_input):
        """Clean and enhance AI response"""
        if not response or len(response) < 5:
            return self.generate_fallback_response(user_input)
        
        # Remove unwanted patterns
        response = response.split('\n')[0]  # Take first line only
        response = response.replace('User:', '').replace('NeuroBot:', '').strip()
        
        # Add mental health focus if missing
        if len(response) < 20:  # Too short, enhance it
            sentiment = TextBlob(user_input).sentiment.polarity
            
            if sentiment < -0.3:  # Negative sentiment
                response += " I hear that you're going through something tough right now."
            elif sentiment > 0.3:  # Positive sentiment  
                response += " That sounds really positive!"
            else:
                response += " Tell me more about what's on your mind."
        
        # Ensure it ends properly
        if not response.endswith(('.', '!', '?')):
            response += "."
        
        return response
    
    def generate_fallback_response(self, user_input):
        """Generate response without AI model using smart text analysis"""
        sentiment = TextBlob(user_input).sentiment
        user_lower = user_input.lower()
        
        # Analyze what user is talking about
        mental_health_topics = {
            'anxiety': ['anxious', 'anxiety', 'panic', 'worry', 'nervous', 'scared'],
            'depression': ['depressed', 'sad', 'down', 'hopeless', 'empty', 'worthless'],
            'stress': ['stressed', 'pressure', 'overwhelmed', 'deadline', 'busy'],
            'sleep': ['sleep', 'insomnia', 'tired', 'exhausted', 'rest'],
            'work': ['work', 'job', 'boss', 'career', 'workplace'],
            'relationships': ['relationship', 'friend', 'family', 'dating', 'breakup'],
            'self_care': ['self care', 'help myself', 'what should i do'],
        }
        
        detected_topic = None
        for topic, keywords in mental_health_topics.items():
            if any(keyword in user_lower for keyword in keywords):
                detected_topic = topic
                break
        
        # Generate contextual responses based on topic and sentiment
        if detected_topic == 'anxiety':
            if sentiment.polarity < -0.2:
                return "Anxiety can feel overwhelming, but you're not alone in this. Have you tried grounding techniques? Sometimes focusing on what you can control right now helps."
            else:
                return "I hear you talking about anxiety. What's been triggering it lately? Sometimes just naming what's making us anxious can help."
        
        elif detected_topic == 'depression':
            return "Depression is really tough to deal with. Thank you for sharing that with me. What's one small thing that usually brings you even a tiny bit of comfort?"
        
        elif detected_topic == 'stress':
            return "Stress can really pile up. What's been the biggest source of pressure for you lately? Sometimes breaking things down helps make them feel more manageable."
        
        elif detected_topic == 'sleep':
            return "Sleep issues can affect everything else. How has your sleep been impacting your days? There are some techniques that might help, depending on what's keeping you up."
        
        elif detected_topic == 'work':
            return "Work stress is so common but that doesn't make it easier. What's been the most challenging part about work lately?"
        
        elif detected_topic == 'relationships':
            return "Relationships can be complicated. Want to talk about what's been going on? Sometimes it helps to get an outside perspective."
        
        # Sentiment-based responses when no specific topic detected
        elif sentiment.polarity < -0.3:
            return "I can sense you're going through something difficult right now. What's been weighing on your mind? I'm here to listen."
        
        elif sentiment.polarity > 0.3:
            return "It sounds like things are going well for you! What's been bringing you joy lately?"
        
        else:
            # Neutral/unclear - ask open-ended question
            responses = [
                "What's been on your mind lately?",
                "How have you been feeling recently?",
                "Tell me more about what's going on with you.",
                "What's happening in your world right now?",
                "How are you really doing today?"
            ]
            return random.choice(responses)
    
    def build_conversation_context(self):
        """Build context from recent conversation"""
        if len(self.conversation_history) < 2:
            return ""
        
        # Get last few exchanges
        recent_context = ""
        for entry in self.conversation_history[-3:]:
            recent_context += f"User: {entry['user']}\nBot: {entry['bot']}\n"
        
        return recent_context
    
    def respond(self, user_input):
        """Main response method"""
        if not user_input.strip():
            return
        
        # Build conversation context
        context = self.build_conversation_context()
        
        # Generate AI response
        response = self.generate_ai_response(user_input, context)
        
        # Log the interaction
        self.conversation_history.append({
            'user': user_input,
            'bot': response,
            'timestamp': datetime.now().isoformat(),
            'sentiment': TextBlob(user_input).sentiment._asdict()
        })
        
        # Save conversation
        self.save_conversation_history()
        
        # Deliver response
        print_bot_message(response)
        
        # Occasionally offer deeper support
        if len(self.conversation_history) % 5 == 0:
            self.offer_deeper_support()
    
    def offer_deeper_support(self):
        """Occasionally check if user wants more support"""
        time.sleep(0.5)
        
        support_offers = [
            "Is there anything specific you'd like help working through?",
            "Would it be helpful to talk about coping strategies?",
            "Want to explore what might help you feel better?",
            "Is there something deeper you'd like to discuss?"
        ]
        
        offer = random.choice(support_offers)
        print(f"💡 {offer}")
    
    def welcome(self):
        """Welcome message"""
        print("\n" + "=" * 60)
        typing_effect("🧠 NeuroBot AI starting up...", delay=0.04)
        
        if ML_AVAILABLE and self.ai_model:
            typing_effect("🤖 Full AI conversation mode activated!", delay=0.03)
        else:
            typing_effect("🤖 Smart conversation mode activated!", delay=0.03)
        
        time.sleep(0.5)
        print()
        
        welcome_msg = """
        ╔══════════════════════════════════════════════════════╗
        ║                    NeuroBot AI                       ║
        ║                                                      ║
        ║            Real AI Mental Health Companion           ║
        ║         Genuine Conversation • Real Understanding    ║
        ║                                                      ║
        ║           🧠 Powered by Conversational AI 🧠         ║
        ╚══════════════════════════════════════════════════════╝
        """
        print(welcome_msg)
        
        # Get user's name
        name = input("🤖 What should I call you? (or just press enter): ").strip()
        if name:
            self.user_name = name
            self.user_context['name'] = name
            typing_effect(f"Hey {name}! I'm NeuroBot. I'm here to have real conversations about mental health, life, whatever's on your mind.")
        else:
            typing_effect("Hey there! I'm NeuroBot. I'm here to have genuine conversations about mental health and life.")
        
        time.sleep(1)
        typing_effect("I'm not just programmed responses - I actually try to understand and respond thoughtfully to what you're going through.")
        typing_effect("What's on your mind today? 💭")
    
    def save_conversation_history(self):
        """Save conversation for continuity"""
        try:
            if not os.path.exists('assets'):
                os.makedirs('assets')
            
            # Keep last 50 conversations
            history_to_save = self.conversation_history[-50:] if len(self.conversation_history) > 50 else self.conversation_history
            
            data = {
                'conversations': history_to_save,
                'user_context': self.user_context,
                'session_start': self.session_start.isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            
            with open('assets/conversation_ai.json', 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Couldn't save conversation: {e}")
    
    def load_conversation_history(self):
        """Load previous conversations for context"""
        try:
            if os.path.exists('assets/conversation_ai.json'):
                with open('assets/conversation_ai.json', 'r') as f:
                    data = json.load(f)
                    
                self.conversation_history = data.get('conversations', [])
                self.user_context = data.get('user_context', {})
                
                if self.conversation_history:
                    print(f"📚 Loaded {len(self.conversation_history)} previous messages")
                    
                if 'name' in self.user_context:
                    self.user_name = self.user_context['name']
                    
        except Exception as e:
            print(f"Couldn't load conversation history: {e}")
    
    def show_conversation_stats(self):
        """Show conversation insights"""
        if not self.conversation_history:
            typing_effect("No conversation history yet!")
            return
        
        print_separator()
        typing_effect("🧠 Conversation Insights:")
        
        # Analyze sentiment trends
        sentiments = [msg.get('sentiment', {}).get('polarity', 0) for msg in self.conversation_history]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        total_messages = len(self.conversation_history)
        session_duration = datetime.now() - self.session_start
        
        print(f"""
        💬 Total messages: {total_messages}
        🕐 Session time: {str(session_duration).split('.')[0]}
        😊 Overall mood: {'Positive' if avg_sentiment > 0.1 else 'Negative' if avg_sentiment < -0.1 else 'Neutral'}
        🧠 AI understanding: {'Deep' if total_messages > 10 else 'Building'}
        """)
        
        # Recent topics discussed
        recent_messages = [msg['user'].lower() for msg in self.conversation_history[-5:]]
        common_words = []
        for msg in recent_messages:
            words = [w for w in msg.split() if len(w) > 4]  # Meaningful words
            common_words.extend(words)
        
        if common_words:
            from collections import Counter
            top_topics = Counter(common_words).most_common(3)
            topics_str = ", ".join([word for word, count in top_topics])
            print(f"🎯 Recent topics: {topics_str}")
    
    def goodbye(self):
        """Goodbye with continuity"""
        print_separator()
        
        name_part = f"{self.user_name}, " if self.user_name else ""
        
        typing_effect(f"Thanks for the conversation, {name_part}it was really meaningful.")
        typing_effect("I'll remember what we talked about for next time.")
        typing_effect("Take care of yourself, and feel free to come back whenever you need to chat. 🌟")
        
        # Save final conversation state
        self.save_conversation_history()
        typing_effect("\n✅ Conversation saved. See you later!")


def main():
    """Main function to run conversational NeuroBot"""
    from utils import clear_screen, get_user_input
    
    clear_screen()
    bot = ConversationalNeuroBot()
    bot.welcome()
    
    print("\nJust start chatting naturally! Type 'quit' to exit or 'stats' to see insights.")
    print("=" * 60)
    
    while True:
        try:
            user_input = get_user_input()
            
            if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                bot.goodbye()
                break
            elif user_input.lower() in ['stats', 'insights']:
                bot.show_conversation_stats()
            else:
                bot.respond(user_input)
                
        except KeyboardInterrupt:
            print("\n")
            bot.goodbye()
            break

if __name__ == "__main__":
    main()