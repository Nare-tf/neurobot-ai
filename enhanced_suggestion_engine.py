import random
import json
from collections import defaultdict, Counter
from datetime import datetime, timedelta

class MLSuggestionEngine:
    def __init__(self):
        # Your original suggestions (keeping all the personality!)
        self.suggestions = {
            'stressed': {
                'general': [
                    "try this: breathe in for 4, hold for 4, out for 6. sounds basic but it literally rewires your stress response",
                    "sometimes just a quick 5 min walk helps reset everything. even just around your room counts",
                    "do the 5-4-3-2-1 thing: 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste",
                    "break whatever's stressing you into like 3 smaller steps. just tackle the first one today"
                ],
                'work': [
                    "work stress hits different. can you delegate anything or get an extension?",
                    "try the pomodoro thing: 25 min work, 5 min break. actually works",
                    "remember: done is better than perfect, especially with deadlines"
                ]
            },
            'tired': {
                'general': [
                    "real talk - when did you last drink water? sometimes 'tired' is just dehydrated",
                    "power nap for 15-20 min max. set that alarm or you'll wake up more dead",
                    "sounds weird but light movement actually gives you energy. try some stretches",
                    "how's your actual sleep quality? getting hours ≠ getting rest"
                ]
            },
            'anxious': {
                'general': [
                    "anxiety is usually about stuff we can't control. what's one thing you CAN control rn?",
                    "try this: tense each muscle for 5 seconds then let it go. works surprisingly well",
                    "ground yourself: press your feet into the floor and actually feel it",
                    "reminder: thoughts aren't facts. what evidence supports your worry vs challenges it?"
                ]
            },
            'focused': [
                "yo you're dialed in rn! perfect time for your hardest task",
                "ride this wave - protect the next hour or two for deep work",
                "this is good energy, tackle that thing you've been avoiding",
                "you're sharp af right now. what's the most important thing you can do?"
            ],
            'bored': [
                "boredom is just creativity waiting to happen. what have you always wanted to try?",
                "switch it up completely - do something creative, physical, or social",
                "maybe you need a challenge? what's slightly outside your comfort zone?",
                "use this dead time to start a small habit. what could you do for 5 min daily?"
            ],
            'sad': [
                "it's totally fine to feel sad. emotions are data - what might yours be saying?",
                "sometimes we gotta sit with sadness before we can move through it. that's normal",
                "small self-care hits different: warm drink, good music, text someone who cares",
                "sadness passes easier when you don't fight it. can you be gentle with yourself rn?"
            ],
            'happy': [
                "love this energy! what's got you feeling good?",
                "this is the perfect time to tackle something challenging or help someone else",
                "happiness is contagious - maybe share this vibe with someone?",
                "ride this wave! what positive thing can you do while you're feeling great?"
            ]
        }
        
        self.follow_ups = {
            'stressed': "wanna try one of these rn?",
            'tired': "how's your sleep been lately btw?",
            'anxious': "what's the main thing bugging you?",
            'focused': "what's your top priority rn?",
            'bored': "what sounds good - creative stuff, moving around, or mental challenges?",
            'sad': "wanna talk about what's going on?",
            'happy': "what's making today good?"
        }
        
        # ML Enhancement: Track what works for this user
        self.suggestion_feedback = defaultdict(list)
        self.user_preferences = defaultdict(int)
        self.suggestion_history = []
        
        self.load_feedback_data()
    
    def get_response(self, mood, context=None, mood_analyzer=None):
        """Enhanced suggestion with ML personalization"""
        if mood not in self.suggestions:
            return "I'm here to listen fr. tell me more about what's going on"
        
        # Get base suggestions
        suggestions = self._get_base_suggestions(mood, context)
        
        # ML Enhancement: Personalize based on past interactions
        personalized_suggestion = self._get_personalized_suggestion(mood, suggestions, mood_analyzer)
        
        # Add context from similar conversations
        contextual_insight = self._get_contextual_insight(mood_analyzer) if mood_analyzer else ""
        
        follow_up = self.follow_ups.get(mood, "how's that sound?")
        
        response = personalized_suggestion
        if contextual_insight:
            response += f"\n\n{contextual_insight}"
        response += f"\n\n{follow_up}"
        
        # Store this suggestion for learning
        self._log_suggestion(mood, personalized_suggestion, context)
        
        return response
    
    def _get_base_suggestions(self, mood, context):
        """Get base suggestions like before"""
        if isinstance(self.suggestions[mood], dict):
            if context and context[0] in self.suggestions[mood]:
                return self.suggestions[mood][context[0]]
            else:
                return self.suggestions[mood]['general']
        else:
            return self.suggestions[mood]
    
    def _get_personalized_suggestion(self, mood, suggestions, mood_analyzer):
        """ML-enhanced suggestion selection based on user history"""
        
        # If we have feedback data, use it to pick better suggestions
        if mood in self.user_preferences and len(self.suggestion_history) > 3:
            # Avoid recently used suggestions
            recent_suggestions = [s['text'] for s in self.suggestion_history[-3:]]
            fresh_suggestions = [s for s in suggestions if s not in recent_suggestions]
            
            if fresh_suggestions:
                suggestions = fresh_suggestions
        
        # Pick a suggestion (still random for now, but with smart filtering)
        selected = random.choice(suggestions)
        
        # Add personalization based on patterns
        if mood_analyzer:
            insights = mood_analyzer.get_mood_insights()
            if "usually feeling" in insights and mood in insights:
                personal_touch = random.choice([
                    "btw I noticed this comes up for you sometimes. ",
                    "since this seems to be a thing for you lately, ",
                    "I remember you dealing with this before, so "
                ])
                selected = personal_touch + selected
        
        return selected
    
    def _get_contextual_insight(self, mood_analyzer):
        """Add insights from similar past conversations"""
        if not mood_analyzer:
            return ""
        
        try:
            similar_convos = mood_analyzer.get_similar_conversations("", top_k=1)
            if similar_convos and similar_convos[0]['similarity'] > 0.3:
                past_mood = similar_convos[0]['conversation']['mood']
                if past_mood:
                    insights = [
                        f"this feels similar to when you were {past_mood} before",
                        f"reminds me of that time you mentioned feeling {past_mood}",
                        f"getting similar vibes to your {past_mood} moments"
                    ]
                    return random.choice(insights)
        except:
            pass
        
        return ""
    
    def _log_suggestion(self, mood, suggestion_text, context):
        """Track suggestions for learning"""
        log_entry = {
            'mood': mood,
            'suggestion': suggestion_text,
            'context': context,
            'timestamp': datetime.now().isoformat()
        }
        
        self.suggestion_history.append(log_entry)
        
        # Keep only recent history
        if len(self.suggestion_history) > 50:
            self.suggestion_history.pop(0)
    
    def record_feedback(self, helpful=True):
        """Allow user to give feedback on suggestions"""
        if not self.suggestion_history:
            return "no recent suggestions to rate!"
        
        last_suggestion = self.suggestion_history[-1]
        mood = last_suggestion['mood']
        
        if helpful:
            self.user_preferences[f"{mood}_positive"] += 1
            response = "thanks! I'll remember that worked for you 💪"
        else:
            self.user_preferences[f"{mood}_negative"] += 1
            response = "noted! I'll try different approaches next time"
        
        # Save the feedback
        self.save_feedback_data()
        
        return response
    
    def get_adaptive_suggestions(self, mood):
        """Generate new suggestions based on what's worked before"""
        base_suggestions = self._get_base_suggestions(mood, None)
        
        # If user has given feedback, adapt
        positive_key = f"{mood}_positive"
        if self.user_preferences[positive_key] > 2:
            adaptive_suggestions = [
                f"since the breathing stuff worked before, here's another technique...",
                f"building on what helped you last time...",
                f"this is similar to that thing that worked for you..."
            ]
            
            # Mix adaptive with base suggestions
            return random.choice(adaptive_suggestions + base_suggestions[:2])
        
        return random.choice(base_suggestions)
    
    def get_personalized_suggestion(self, mood):
        """Enhanced personalized responses with learning"""
        # Your original personalized responses
        responses = {
            'stressed': "I can tell you're dealing with pressure rn. let's bring that stress down a bit",
            'tired': "your energy's running low fr. let's see what we can do to help you recharge",
            'anxious': "anxiety is rough ngl. I'm here to help you find some calm",
            'focused': "love that focused energy! let's make sure you use it right",
            'bored': "boredom can actually be good for new ideas. let's explore that",
            'good': "that's what I like to hear! wanna build on that momentum?",
            'down': "I hear you. those low moments suck but they pass. let's work through this",
            'happy': "yo that's awesome! this positive energy is perfect for getting stuff done"
        }
        
        base_response = responses.get(mood, "thanks for sharing that. how can I help?")
        
        # Add learning-based personalization
        if mood in self.user_preferences:
            frequency = sum(1 for entry in self.suggestion_history[-10:] if entry['mood'] == mood)
            if frequency > 3:
                personal_note = random.choice([
                    " I've noticed this mood comes up for you sometimes.",
                    " This seems to be something you deal with regularly.",
                    " I remember helping you with this feeling before."
                ])
                base_response += personal_note
        
        return base_response
    
    def get_mood_trends(self):
        """Analyze user's mood trends for insights"""
        if len(self.suggestion_history) < 5:
            return "need more data to see your patterns!"
        
        recent_moods = [entry['mood'] for entry in self.suggestion_history[-10:]]
        mood_counts = Counter(recent_moods)
        
        if not mood_counts:
            return "not seeing clear patterns yet"
        
        dominant_mood = mood_counts.most_common(1)[0]
        
        insights = []
        if dominant_mood[1] > 3:
            insights.append(f"you've been mostly {dominant_mood[0]} lately")
        
        # Time-based insights
        recent_entries = self.suggestion_history[-7:]  # Last week
        if len(recent_entries) > 2:
            today_moods = [e['mood'] for e in recent_entries if 
                          datetime.now().date() == datetime.fromisoformat(e['timestamp']).date()]
            if today_moods:
                insights.append(f"today you've been {Counter(today_moods).most_common(1)[0][0]}")
        
        return " • ".join(insights) if insights else "your mood patterns are pretty varied!"
    
    def save_feedback_data(self):
        """Save learning data"""
        try:
            data = {
                'user_preferences': dict(self.user_preferences),
                'suggestion_history': self.suggestion_history[-30:],  # Keep last 30
                'timestamp': datetime.now().isoformat()
            }
            
            with open('assets/suggestion_feedback.json', 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Couldn't save feedback: {e}")
    
    def load_feedback_data(self):
        """Load previous learning data"""
        try:
            import os
            if os.path.exists('assets/suggestion_feedback.json'):
                with open('assets/suggestion_feedback.json', 'r') as f:
                    data = json.load(f)
                    
                    self.user_preferences = defaultdict(int, data.get('user_preferences', {}))
                    self.suggestion_history = data.get('suggestion_history', [])
                    
                    if self.suggestion_history:
                        print(f"🧠 Loaded previous learning data ({len(self.suggestion_history)} interactions)")
                        
        except Exception as e:
            print(f"Couldn't load feedback data: {e}")
    
    def __del__(self):
        """Save data when engine is destroyed"""
        self.save_feedback_data()