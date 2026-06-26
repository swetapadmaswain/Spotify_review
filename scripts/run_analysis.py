import os
import sys
from datetime import datetime
from supabase import createClient

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

supabase = createClient(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

def analyze_sentiment_simple(text):
    """Simple rule-based sentiment analysis (free)"""
    positive_words = ['good', 'great', 'excellent', 'love', 'amazing', 'best', 'awesome', 'fantastic', 'wonderful', 'perfect']
    negative_words = ['bad', 'terrible', 'hate', 'worst', 'awful', 'poor', 'disappointing', 'frustrating', 'annoying', 'broken']
    
    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return {'label': 'positive', 'score': min(0.9, 0.5 + positive_count * 0.1)}
    elif negative_count > positive_count:
        return {'label': 'negative', 'score': min(0.9, 0.5 + negative_count * 0.1)}
    else:
        return {'label': 'neutral', 'score': 0.5}

def extract_topics_simple(text):
    """Simple topic extraction based on keywords"""
    topic_keywords = {
        'recommendation': ['recommend', 'algorithm', 'discover', 'radio', 'playlist'],
        'ui_ux': ['interface', 'design', 'layout', 'navigation', 'button'],
        'performance': ['slow', 'crash', 'lag', 'freeze', 'loading'],
        'content': ['song', 'artist', 'album', 'music', 'audio'],
        'features': ['feature', 'function', 'option', 'setting', 'tool']
    }
    
    text_lower = text.lower()
    topic_scores = {}
    
    for topic, keywords in topic_keywords.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            topic_scores[topic] = score
    
    if topic_scores:
        primary_topic = max(topic_scores.items(), key=lambda x: x[1])[0]
        return {
            'primary_topic': primary_topic,
            'secondary_topics': list(topic_scores.keys()),
            'relevance_scores': topic_scores
        }
    else:
        return {
            'primary_topic': 'general',
            'secondary_topics': [],
            'relevance_scores': {}
        }

def analyze_reviews():
    """Analyze unprocessed reviews"""
    print("Starting analysis...")
    
    # Fetch unprocessed reviews (no sentiment analysis)
    response = supabase.table('raw_reviews').select('id, review_text').is_('sentiment_analysis', 'null').limit(50).execute()
    reviews = response.data
    
    print(f"Found {len(reviews)} reviews to analyze")
    
    analyzed_count = 0
    
    for review in reviews:
        # Sentiment analysis
        sentiment = analyze_sentiment_simple(review['review_text'])
        
        supabase.table('sentiment_analysis').insert({
            'review_id': review['id'],
            'sentiment': sentiment['label'],
            'confidence': sentiment['score'],
            'emotion': sentiment['label'],
            'intensity': 'medium' if sentiment['score'] > 0.6 else 'low'
        }).execute()
        
        # Topic analysis
        topics = extract_topics_simple(review['review_text'])
        
        supabase.table('topic_analysis').insert({
            'review_id': review['id'],
            'primary_topic': topics['primary_topic'],
            'secondary_topics': topics['secondary_topics'],
            'relevance_scores': topics['relevance_scores']
        }).execute()
        
        analyzed_count += 1
    
    # Generate insights from analysis
    generate_insights()
    
    print(f"Analysis completed. Analyzed {analyzed_count} reviews")
    return analyzed_count

def generate_insights():
    """Generate insights from analyzed data"""
    print("Generating insights...")
    
    # Get sentiment distribution
    sentiment_response = supabase.table('sentiment_analysis').select('sentiment').execute()
    sentiments = [row['sentiment'] for row in sentiment_response.data]
    
    # Get top topics
    topic_response = supabase.table('topic_analysis').select('primary_topic').execute()
    topics = [row['primary_topic'] for row in topic_response.data]
    
    # Count topics
    from collections import Counter
    topic_counts = Counter(topics)
    
    # Create pattern insights
    if topic_counts:
        top_topic = topic_counts.most_common(1)[0]
        supabase.table('insights').insert({
            'insight_type': 'pattern',
            'title': f"Most common topic: {top_topic[0]}",
            'description': f"Users frequently mention {top_topic[0]} in their feedback ({top_topic[1]} mentions)",
            'data': {'topic': top_topic[0], 'count': top_topic[1]},
            'confidence': 0.8
        }).execute()
    
    # Create sentiment insight
    if sentiments:
        negative_count = sentiments.count('negative')
        if negative_count > len(sentiments) * 0.3:
            supabase.table('insights').insert({
                'insight_type': 'root_cause',
                'title': 'High negative sentiment detected',
                'description': f'{negative_count} out of {len(sentiments)} reviews show negative sentiment',
                'data': {'negative_count': negative_count, 'total': len(sentiments)},
                'confidence': 0.75
            }).execute()
    
    print("Insights generated")

if __name__ == '__main__':
    analyze_reviews()
