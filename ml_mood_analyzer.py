import re
import numpy as np
from collections import Counter, defaultdict
from textblob import TextBlob
import pickle
import os
from datetime import datetime
import json

# Try to import ML libraries, fallback to basic if not available
try:
    from transformers import pipeline
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    ML_AVAILABLE = True
    print("🚀 ML libraries loaded! NeuroBot is now super powered!")
except ImportError:
    ML_AVAILABLE = False
    print("⚠️  ML libraries not found. Install requirements.txt for enhanced features!")

class MLMoodAnalyzer:
    def __init__(self):
        # Keep your original keywords as fallback
        self.mood_keywords = {
            'stressed': ['stress', 'stressed', 'overwhelmed', 'pressure', 'deadline', 'anxious', 'worried', 'panic'],
            'tired': ['tired', 'exhausted', 'sleepy', 'fatigue', 'drained', 'worn out', 'energy'],
            'focused': ['focused', 'concentrate', 'productive', 'flow', 'zone', 'clear', 'sharp'],
            'anxious': ['nervous', 'worried', 'scared', 'fear', 'anxiety', 'panic', 'restless'],
            'bored': ['bored', 'boring', 'unmotivated', 'stuck', 'monotonous', 'dull'],
            'sad': ['sad', 'down', 'depressed', 'low', 'upset', 'disappointed', 'hurt'],
            'happy': ['happy', 'good', 'great', 'awesome', 'excited', 'joy', 'pleased']
        }
        
        # Initialize ML components
        self.emotion_classifier = None
        self.conversation_vectorizer = None
        self.conversation_history = []
        self.user_patterns = defaultdict(list)
        
        # Setup ML models
        self._setup_ml_models()
        
        # Load any existing user data
        self._load_user_patterns()
    
    def _setup_ml_models(self):
        """Initialize ML models if libraries are available"""
        if not ML_AVAILABLE:
            return
            
        try:
            # Load a pre-trained emotion classifier
            # This is a lightweight model that runs on CPU
            self.emotion_classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                device=-1  # Use CPU
            )
            
            # Setup conversation similarity analyzer
            self.conversation_vectorizer = TfidfVectorizer(
                max_features=100,  # Keep it lightweight
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            print("✅ Advanced emotion AI loaded!")
            
        except Exception as e:
            print(f"⚠️  Using basic mood detection (couldn't load advanced AI: {e})")
            self.emotion_classifier = None
    
    def analyze(self, text):
        """Enhanced mood analysis using ML + your original logic"""
        # Get sentiment polarity first
        blob = TextBlob(text)
        sentiment = blob.sentiment
        
        detected_mood = None
        confidence = 0.0
        
        # Try ML emotion detection first
        if self.emotion_classifier and ML_AVAILABLE:
            try:
                ml_result = self.emotion_classifier(text)[0]
                ml_emotion = ml_result['label'].lower()
                ml_confidence = ml_result['score']
                
                # Map ML emotions to your mood categories
                emotion_mapping = {
                    'joy': 'happy',
                    'sadness': 'sad', 
                    'anger': 'stressed',
                    'fear': 'anxious',
                    'surprise': 'focused',
                    'disgust': 'bored'
                }
                
                if ml_emotion in emotion_mapping and ml_confidence > 0.6:
                    detected_mood = emotion_mapping[ml_emotion]
                    confidence = ml_confidence
                    
            except Exception as e:
                print(f"ML detection failed: {e}")
        
        # Fallback to your original keyword method + sentiment
        if not detected_mood:
            detected_mood, confidence = self._keyword_analysis(text)
            
            # Enhance with sentiment
            if sentiment.polarity < -0.3 and not detected_mood:
                detected_mood = 'sad'
                confidence = abs(sentiment.polarity)
            elif sentiment.polarity > 0.3 and not detected_mood:
                detected_mood = 'happy'  
                confidence = sentiment.polarity
        
        # Store this interaction for learning
        self._store_interaction(text, detected_mood, confidence)
        
        return detected_mood
    
    def _keyword_analysis(self, text):
        """Your original keyword analysis, now with confidence scores"""
        text_lower = text.lower()
        mood_scores = {}
        
        for mood, keywords in self.mood_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                mood_scores[mood] = score
        
        if mood_scores:
            best_mood = max(mood_scores, key=mood_scores.get)
            max_score = mood_scores[best_mood]
            confidence = min(max_score / 3.0, 1.0)  # Normalize to 0-1
            return best_mood, confidence
        
        return None, 0.0
    
    def _store_interaction(self, text, mood, confidence):
        """Store interactions for pattern learning"""
        interaction = {
            'text': text,
            'mood': mood,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'sentiment': TextBlob(text).sentiment._asdict()
        }
        
        self.conversation_history.append(interaction)
        
        # Keep only last 100 interactions to manage memory
        if len(self.conversation_history) > 100:
            self.conversation_history.pop(0)
    
    def get_similar_conversations(self, current_text, top_k=3):
        """Find similar past conversations for better context"""
        if not ML_AVAILABLE or len(self.conversation_history) < 2:
            return []
        
        try:
            # Get all past conversation texts
            past_texts = [conv['text'] for conv in self.conversation_history[:-1]]
            all_texts = past_texts + [current_text]
            
            # Vectorize conversations
            if not hasattr(self, '_fitted_vectorizer') or self._fitted_vectorizer is None:
                vectors = self.conversation_vectorizer.fit_transform(all_texts)
                self._fitted_vectorizer = True
            else:
                vectors = self.conversation_vectorizer.transform(all_texts)
            
            # Find most similar conversations
            current_vector = vectors[-1]
            past_vectors = vectors[:-1]
            
            similarities = cosine_similarity(current_vector, past_vectors)[0]
            
            # Get top similar conversations
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            similar_convos = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Only reasonably similar ones
                    similar_convos.append({
                        'conversation': self.conversation_history[idx],
                        'similarity': similarities[idx]
                    })
            
            return similar_convos
            
        except Exception as e:
            print(f"Similarity search failed: {e}")
            return []
    
    def get_mood_insights(self):
        """Get insights about user's mood patterns"""
        if len(self.conversation_history) < 5:
            return "need more conversations to see patterns!"
        
        moods = [conv['mood'] for conv in self.conversation_history if conv['mood']]
        mood_counts = Counter(moods)
        
        insights = []
        
        if mood_counts:
            most_common = mood_counts.most_common(1)[0]
            insights.append(f"you're usually feeling {most_common[0]} ({most_common[1]} times)")
            
            # Time-based patterns
            recent_moods = [conv['mood'] for conv in self.conversation_history[-10:] if conv['mood']]
            if recent_moods:
                recent_dominant = Counter(recent_moods).most_common(1)[0][0]
                insights.append(f"lately you've been mostly {recent_dominant}")
        
        return " • ".join(insights) if insights else "still learning your patterns!"
    
    def _save_user_patterns(self):
        """Save user patterns for next session"""
        try:
            data = {
                'conversation_history': self.conversation_history[-50:],  # Keep last 50
                'timestamp': datetime.now().isoformat()
            }
            
            with open('assets/user_patterns.json', 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Couldn't save patterns: {e}")
    
    def _load_user_patterns(self):
        """Load user patterns from previous sessions"""
        try:
            if os.path.exists('assets/user_patterns.json'):
                with open('assets/user_patterns.json', 'r') as f:
                    data = json.load(f)
                    self.conversation_history = data.get('conversation_history', [])
                    print(f"📚 Loaded {len(self.conversation_history)} previous interactions")
                    
        except Exception as e:
            print(f"Couldn't load patterns: {e}")
    
    def get_context(self, text):
        """Enhanced context detection with ML insights"""
        # Your original context detection
        contexts = []
        
        if any(word in text.lower() for word in ['work', 'job', 'boss', 'colleague']):
            contexts.append('work')
        if any(word in text.lower() for word in ['school', 'study', 'exam', 'homework']):
            contexts.append('academic')
        if any(word in text.lower() for word in ['relationship', 'friend', 'family']):
            contexts.append('social')
        if any(word in text.lower() for word in ['health', 'sick', 'doctor']):
            contexts.append('health')
        
        # Add ML-based context insights
        similar_convos = self.get_similar_conversations(text, top_k=2)
        if similar_convos:
            contexts.append('similar_to_past')
            
        return contexts
    
    def __del__(self):
        """Save patterns when analyzer is destroyed"""
        self._save_user_patterns()