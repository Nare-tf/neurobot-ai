import random
import time
from datetime import datetime

# Import your new ML classes (fallback to original if ML libs not available)
try:
    from ml_mood_analyzer import MLMoodAnalyzer as MoodAnalyzer
    from enhanced_suggestion_engine import MLSuggestionEngine as SuggestionEngine
    ML_ENHANCED = True
    print("🚀 Running ML-Enhanced NeuroBot!")
except ImportError:
    # Fallback to your original classes
    from ml_mood_analyzer import MoodAnalyzer
    from enhanced_suggestion_engine import SuggestionEngine
    ML_ENHANCED = False
    print("⚡ Running Basic NeuroBot (install requirements.txt for ML features)")

from session_tracker import SessionTracker
from utils import typing_effect, print_bot_message, print_separator

class NeuroBot:
    def __init__(self):
        self.name = "NeuroBot"
        self.mood_analyzer = MoodAnalyzer()
        self.suggestion_engine = SuggestionEngine()
        self.session_tracker = SessionTracker()
        self.conversation_history = []
        self.current_mood = None
        self.user_name = None
        self.waiting_for_response = None
        self.ml_enhanced = ML_ENHANCED
        
        # Your original personality (keeping all the vibes!)
        self.responses = {
            'greetings': [
                "hey!",
                "yo what's up!",
                "hi there!",
                "hey! how you doing?",
                "what's good!"
            ],
            'casual_responses': [
                "fr",
                "yeah totally", 
                "I feel you",
                "that's real",
                "makes sense",
                "gotcha",
                "yeah for sure"
            ],
            'internet_slang': {
                'lol': ["lmao that's funny", "haha right?", "lol for real"],
                'lmao': ["😂 facts", "lmaooo", "that's hilarious"],
                'fr': ["fr fr", "no cap", "straight up"],
                'ngl': ["ngl same", "honestly yeah"],
                'tbh': ["tbh you're right", "real talk"],
                'idk': ["yeah idk either sometimes", "fair enough", "that's valid"],
                'bruh': ["bruh moment fr", "I know right?", "bruh..."],
                'cap': ["no cap detected", "that's facts", "straight truth"],
                'bet': ["bet!", "for sure", "100%"],
                'fam': ["fam I got you", "we're good fam"],
                'rn': ["rn is rough", "I hear you rn", "what's happening rn?"],
                'af': ["that's intense af", "I get it"]
            },
            'acknowledgments': [
                "yeah I get that",
                "totally understand", 
                "that makes sense",
                "I hear you",
                "for real",
                "I feel that"
            ],
            'encouragement': [
                "you got this fr 💪",
                "nah you're gonna crush it",
                "honestly you're stronger than you think",
                "keep going, you're doing good",
                "one step at a time fam",
                "you're making moves!"
            ],
            'empathy': [
                "damn that's rough",
                "that sounds hard ngl",
                "appreciate you telling me that",
                "that's gotta be tough", 
                "thanks for being real with me"
            ]
        }
    
    def welcome(self):
        print("\n" + "=" * 60)
        typing_effect("🤖 NeuroBot Lite is starting up", delay=0.05)
        
        if self.ml_enhanced:
            typing_effect("🚀 ML ENHANCED VERSION LOADED!", delay=0.03)
        
        time.sleep(0.5)
        print()
        typing_effect("█████████████████████████████████████████████████", delay=0.02)
        print("\n")
        
        welcome_msg = f"""
        ╔══════════════════════════════════════════════════════╗
        ║                  NeuroBot Lite {'🚀' if self.ml_enhanced else '⚡'}                  ║
        ║                                                      ║
        ║          Your AI companion for emotional wellness    ║
        ║          Focus • Stress Relief • Mental Clarity      ║
        ║                                                      ║
        ║          {'✨ Enhanced with Machine Learning ✨' if self.ml_enhanced else '💫 Classic Experience 💫'}           ║
        ╚══════════════════════════════════════════════════════╝
        """
        print(welcome_msg)
        
        # Get user's name
        name_prompt = "what should I call you? (or just hit enter): "
        name = input(f"🤖 {name_prompt}").strip()
        if name:
            self.user_name = name
            if self.ml_enhanced:
                typing_effect(f"yooo nice to meet you {name}! 🎉 I'm gonna learn your patterns and get better at helping you")
            else:
                typing_effect(f"yooo nice to meet you {name}! 🎉")
        else:
            typing_effect("all good! let's get started")
        
        time.sleep(1)
        typing_effect("I'm here to help with stress, focus, whatever you need.")
        if self.ml_enhanced:
            typing_effect("think of me as your digital homie who actually gets it AND learns from our chats 🌟🧠")
        else:
            typing_effect("think of me as your digital homie who actually gets it 🌟")
    
    def respond(self, user_input):
        user_lower = user_input.lower().strip()
        
        # Handle follow-up responses first
        if self.waiting_for_response:
            response = self._handle_followup(user_input)
            print_bot_message(response)
            self.waiting_for_response = None
            return
        
        # Handle internet slang and casual responses
        slang_response = self._handle_slang(user_lower)
        if slang_response:
            print_bot_message(slang_response)
            return
        
        # Enhanced ML analysis
        detected_mood = self.mood_analyzer.analyze(user_input)
        context = self.mood_analyzer.get_context(user_input)
        
        # Update current mood if detected
        if detected_mood:
            self.current_mood = detected_mood
        
        # Generate ML-enhanced response
        response = self._generate_response(user_input, detected_mood, context)
        
        # Log the interaction
        self.conversation_history.append({
            'user': user_input,
            'bot': response,
            'mood': detected_mood,
            'timestamp': datetime.now()
        })
        
        # Deliver response with typing effect
        print_bot_message(response)
        
        # ML-enhanced targeted help
        if detected_mood and detected_mood != 'neutral':
            self._offer_targeted_help(detected_mood)
    
    def _handle_slang(self, user_input):
        # Your original slang handling (unchanged)
        for slang, responses in self.responses['internet_slang'].items():
            if slang in user_input:
                return random.choice(responses)
        
        if user_input in ['k', 'ok', 'okay', 'cool', 'nice', 'word', 'bet']:
            return random.choice(['cool cool', 'bet', 'word', 'for sure', 'aight'])
        
        if user_input in ['sup', 'yo', 'hey']:
            return random.choice(self.responses['greetings'])
            
        if user_input in ['same', 'mood', 'relatable']:
            return random.choice(['big mood', 'felt that', 'literally same', 'mood fr'])
            
        return None
    
    def _handle_followup(self, user_input):
        user_lower = user_input.lower().strip()
        
        yes_responses = ['yes', 'y', 'yeah', 'yah', 'yea', 'sure', 'ok', 'okay', 'bet', 'fs', 'for sure', 'down', 'lets go', 'yep', 'mhm', 'uh huh']
        no_responses = ['no', 'n', 'nah', 'nope', 'not really', 'im good', 'maybe later', 'not rn']
        
        is_yes = any(response in user_lower for response in yes_responses)
        is_no = any(response in user_lower for response in no_responses)
        
        if self.waiting_for_response == 'technique_offer':
            if is_yes:
                return self._provide_technique()
            elif is_no:
                return random.choice([
                    "no worries! I'm here if you change your mind",
                    "all good, just lmk if you need anything",
                    "bet, just holler if you want help later"
                ])
            else:
                self.waiting_for_response = None
                return self._generate_response(user_input, None, None)
        
        elif self.waiting_for_response == 'feedback_request' and self.ml_enhanced:
            if is_yes:
                feedback_response = self.suggestion_engine.record_feedback(helpful=True)
                return f"{feedback_response} this helps me get better at helping you!"
            elif is_no:
                feedback_response = self.suggestion_engine.record_feedback(helpful=False)
                return f"{feedback_response} I'll switch up my approach"
            else:
                return "no worries about the feedback! what else is on your mind?"
        
        return "hmm not sure what you meant, but we're good!"
    
    def _provide_technique(self):
        technique = self._get_base_technique()
        
        # Add ML enhancement for feedback
        if self.ml_enhanced:
            self.waiting_for_response = 'feedback_request'
            technique += "\n\n(btw let me know if this helps - I'm learning what works best for you!)"
        
        return technique
    
    def _get_base_technique(self):
        # Your original techniques
        if self.current_mood == 'stressed':
            return """aight let's do this quick technique:
            
• breathe in for 4 seconds
• hold it for 4 seconds  
• breathe out for 6 seconds
• repeat like 3-4 times

this literally activates your chill mode, try it rn"""
        
        elif self.current_mood == 'anxious':
            return """ok try this grounding thing:
            
look around and name:
• 5 things you can see
• 4 things you can touch
• 3 things you can hear
• 2 things you can smell
• 1 thing you can taste

helps bring you back to the moment fr"""
        
        elif self.current_mood == 'tired':
            return """quick energy reset:
            
• drink some water rn (like actually do it)
• do 10 jumping jacks or stretch
• step outside or by a window for 2 min
• take 3 deep breaths

sounds basic but it works"""
        
        else:
            return "let me think of something good for your situation... what specifically do you want help with?"
    
    def _generate_response(self, user_input, mood, context):
        user_lower = user_input.lower()
        
        if mood:
            # Use ML-enhanced suggestion engine
            mood_response = self.suggestion_engine.get_response(mood, context, self.mood_analyzer if self.ml_enhanced else None)
            empathy = random.choice(self.responses['empathy'])
            return f"{empathy} {mood_response}"
        
        # Handle greetings
        if any(greeting in user_lower for greeting in ['hi', 'hello', 'hey', 'sup', 'yo']):
            return random.choice(self.responses['greetings'])
        
        # Handle thanks
        if any(word in user_lower for word in ['thank', 'thanks', 'thx', 'ty']):
            return random.choice(["np!", "of course!", "anytime fam", "you got it", "all good"])
        
        # Handle questions
        if '?' in user_input:
            return self._handle_question(user_input)
        
        # Default response with ML enhancement
        acknowledgment = random.choice(self.responses['casual_responses'])
        base_response = f"{acknowledgment}. what's on your mind?"
        
        # Add ML insight if available
        if self.ml_enhanced and hasattr(self.mood_analyzer, 'get_mood_insights'):
            try:
                insights = self.mood_analyzer.get_mood_insights()
                if insights and "usually" in insights and len(self.conversation_history) > 5:
                    ml_insight = random.choice([
                        " (btw I'm starting to pick up on your patterns)",
                        " (I'm getting better at reading your vibes)",
                        " (learning your style as we chat)"
                    ])
                    base_response += ml_insight
            except:
                pass
        
        return base_response
    
    def _handle_question(self, question):
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['how', 'what', 'why', 'when']):
            suggestions = [
                "good question, lemme think...",
                "hmm that's interesting...",
                "yo that's actually deep...",
                "ngl that's a solid question..."
            ]
            base_response = random.choice(suggestions)
            
            # Context-aware responses
            if 'stress' in question_lower:
                response = f"{base_response} stress usually comes from feeling overwhelmed. try breaking stuff into smaller pieces"
            elif 'focus' in question_lower:
                response = f"{base_response} focus gets better with practice. start with like 5-10 min sessions"
            elif 'sleep' in question_lower:
                response = f"{base_response} sleep is everything fr. try putting your phone away before bed"
            else:
                response = f"{base_response} what part of that do you wanna dig into more?"
            
            # Add ML personalization if available
            if self.ml_enhanced and hasattr(self.suggestion_engine, 'get_mood_trends'):
                try:
                    trends = self.suggestion_engine.get_mood_trends()
                    if trends and len(self.conversation_history) > 3:
                        response += f" (btw {trends})"
                except:
                    pass
            
            return response
        
        return "that's def worth thinking about. what do you think?"
    
    def _offer_targeted_help(self, mood):
        time.sleep(0.3)
        
        offers = {
            'stressed': "want me to walk you through a quick stress thing?",
            'anxious': "I got some grounding exercises if you're down",
            'tired': "want some energy tips that actually work?",
            'bored': "I got some ideas to mix things up if you want",
            'focused': "you're locked in! want tips to keep that going?",
            'sad': "want to talk through what's going on?",
            'happy': "love the good vibes! want to build on this energy?"
        }
        
        if mood in offers:
            offer_text = offers[mood]
            
            # Add ML enhancement hint
            if self.ml_enhanced and len(self.conversation_history) > 5:
                ml_hint = random.choice([
                    " (I'm getting better at suggestions btw)",
                    " (personalized based on what I've learned about you)",
                    " (adapting to your style)"
                ])
                offer_text += ml_hint
            
            print(f"💡 {offer_text}")
            self.waiting_for_response = 'technique_offer'
    
    def mood_check(self):
        print_separator()
        typing_effect("let's do a quick vibe check! 📊")
        
        moods = ["😤 stressed", "😴 tired", "🎯 focused", "😰 anxious", "😑 bored", "😊 good", "😞 down"]
        
        print("\nhow you feeling rn?")
        for i, mood in enumerate(moods, 1):
            print(f"  {i}. {mood}")
        
        try:
            choice = input("\nenter number (1-7): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= 7:
                selected_mood = moods[int(choice) - 1].split()[1].lower()
                self.current_mood = selected_mood
                
                response = self.suggestion_engine.get_personalized_suggestion(selected_mood)
                print_bot_message(f"thanks for sharing! {response}")
                
                # Enhanced logging with ML
                self.session_tracker.log_mood_check(selected_mood)
                
                # Show ML insights if available
                if self.ml_enhanced and len(self.conversation_history) > 3:
                    try:
                        insights = self.mood_analyzer.get_mood_insights()
                        if insights:
                            print_bot_message(f"🧠 pattern insight: {insights}")
                    except:
                        pass
                        
            else:
                print_bot_message("no worries! just tell me how you're doing in your own words")
        except ValueError:
            print_bot_message("that's cool! you can describe your mood however you want")
    
    def show_help(self):
        print_separator()
        help_text = f"""
        🤖 NeuroBot Commands:
        
        • 'mood' - quick vibe check
        • 'stats' - see your session info
        • 'help' - this menu
        • 'quit' - peace out
        """
        
        if self.ml_enhanced:
            help_text += """
        🧠 ML Enhanced Features:
        • 'insights' - see your mood patterns
        • 'trends' - analyze your emotional trends
        """
        
        help_text += """
        💬 or just chat naturally! I help with:
        • stress management
        • focus techniques  
        • energy boosting
        • anxiety relief
        • general wellness stuff
        
        just tell me what's up! 🌟
        """
        print(help_text)
    
    def show_stats(self):
        stats = self.session_tracker.get_session_stats()
        print_separator()
        typing_effect("📊 your session stats:")
        
        basic_stats = f"""
        💬 messages: {len(self.conversation_history)}
        🕐 session time: {stats['duration']}
        🎭 moods: {', '.join(stats['moods']) if stats['moods'] else 'none yet'}
        📈 main mood: {stats['most_common_mood'] or 'no clear pattern'}
        """
        
        print(basic_stats)
        
        # Add ML insights
        if self.ml_enhanced:
            try:
                if hasattr(self.mood_analyzer, 'get_mood_insights'):
                    ml_insights = self.mood_analyzer.get_mood_insights()
                    if ml_insights:
                        print(f"🧠 AI insights: {ml_insights}")
                
                if hasattr(self.suggestion_engine, 'get_mood_trends'):
                    trends = self.suggestion_engine.get_mood_trends()
                    if trends:
                        print(f"📈 trend analysis: {trends}")
            except:
                pass
    
    def show_insights(self):
        """New ML feature - show user insights"""
        if not self.ml_enhanced:
            print_bot_message("insights feature needs ML libraries! install requirements.txt")
            return
        
        print_separator()
        typing_effect("🧠 analyzing your patterns...")
        
        try:
            insights = self.mood_analyzer.get_mood_insights()
            trends = self.suggestion_engine.get_mood_trends()
            
            print("\n🔍 Personal Insights:")
            if insights:
                print(f"  • mood patterns: {insights}")
            if trends:
                print(f"  • recent trends: {trends}")
            
            if not insights and not trends:
                print("  • still learning your patterns! chat more for better insights")
                
        except Exception as e:
            print_bot_message("couldn't generate insights rn, but I'm still learning!")
    
    def show_trends(self):
        """New ML feature - detailed trend analysis"""
        if not self.ml_enhanced:
            print_bot_message("trends feature needs ML libraries! install requirements.txt")
            return
        
        print_separator()
        typing_effect("📈 crunching your mood data...")
        
        try:
            trends = self.suggestion_engine.get_mood_trends()
            insights = self.mood_analyzer.get_mood_insights()
            
            print("\n📊 Mood Trend Analysis:")
            if trends:
                print(f"  • {trends}")
            if insights:
                print(f"  • overall patterns: {insights}")
            
            # Suggestions based on trends
            if trends and "stressed" in trends:
                print("  💡 suggestion: might be good to build in more stress management")
            elif trends and "focused" in trends:
                print("  💡 suggestion: you're in a productive phase! use this energy")
            elif trends and "tired" in trends:
                print("  💡 suggestion: maybe focus on sleep and energy management")
                
        except Exception as e:
            print_bot_message("trend analysis isn't ready yet, but I'm collecting data!")
    
    def goodbye(self):
        print_separator()
        farewells = [
            "take care! you got this fr 💪",
            "catch you later! keep being awesome 🌟", 
            "peace out! I'm here whenever 😊",
            "see ya! keep taking care of yourself 🌈"
        ]
        
        name_part = f"{self.user_name}, " if self.user_name else ""
        farewell = random.choice(farewells)
        
        if self.ml_enhanced:
            typing_effect(f"thanks for chatting {name_part}{farewell}")
            typing_effect("I learned a lot about you today! I'll be even better next time 🧠✨")
        else:
            typing_effect(f"thanks for chatting {name_part}{farewell}")
        
        # Save session data
        self.session_tracker.save_session(self.conversation_history)
        typing_effect("\n✅ session saved. have a good one!")