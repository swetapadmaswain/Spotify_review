import os
import sys
from datetime import datetime
from supabase import create_client

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not supabase_url or not supabase_key:
    print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
    sys.exit(1)

supabase = create_client(supabase_url, supabase_key)

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

    # Get all review IDs that have been analyzed
    analyzed_response = supabase.table('sentiment_analysis').select('review_id').execute()
    analyzed_ids = set(row['review_id'] for row in analyzed_response.data)

    # Fetch recent reviews that haven't been analyzed
    response = supabase.table('raw_reviews').select('id, review_text').order('id', desc=True).limit(50).execute()
    all_reviews = response.data

    # Filter out already analyzed reviews
    reviews = [review for review in all_reviews if review['id'] not in analyzed_ids]
    
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
    
    # Generate insights from analysis (always run, even if no new reviews)
    generate_insights()
    
    print(f"Analysis completed. Analyzed {analyzed_count} reviews")
    return analyzed_count

def generate_insights():
    """Generate insights from analyzed data"""
    print("Generating insights...")
    
    # Clear existing insights to avoid duplicates
    try:
        supabase.table('insights').delete().neq('id', 0).execute()
        print("Cleared existing insights")
    except Exception as e:
        print(f"Warning: Could not clear existing insights: {e}")
    
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
        try:
            supabase.table('insights').insert({
                'insight_type': 'pattern',
                'title': f"Most common topic: {top_topic[0]}",
                'description': f"Users frequently mention {top_topic[0]} in their feedback ({top_topic[1]} mentions)",
                'data': {'topic': top_topic[0], 'count': top_topic[1]},
                'confidence': 0.8
            }).execute()
            print(f"Created pattern insight for topic: {top_topic[0]}")
        except Exception as e:
            print(f"Error creating pattern insight: {e}")
    
    # Create sentiment insight (always create regardless of threshold)
    if sentiments:
        negative_count = sentiments.count('negative')
        positive_count = sentiments.count('positive')
        neutral_count = sentiments.count('neutral')
        
        try:
            supabase.table('insights').insert({
                'insight_type': 'root_cause',
                'title': 'Sentiment distribution',
                'description': f'Sentiment breakdown: {positive_count} positive, {negative_count} negative, {neutral_count} neutral',
                'data': {'negative_count': negative_count, 'positive_count': positive_count, 'neutral_count': neutral_count, 'total': len(sentiments)},
                'confidence': 0.75
            }).execute()
            print(f"Created sentiment insight: {positive_count} positive, {negative_count} negative, {neutral_count} neutral")
        except Exception as e:
            print(f"Error creating sentiment insight: {e}")
    
    # Create sample segment insight
    try:
        supabase.table('insights').insert({
            'insight_type': 'segment',
            'title': 'User segment analysis',
            'description': 'Based on review patterns, users can be segmented by their primary concerns',
            'data': {'segments': ['recommendation-focused', 'ui-focused', 'performance-focused']},
            'confidence': 0.7
        }).execute()
        print("Created segment insight")
    except Exception as e:
        print(f"Error creating segment insight: {e}")
    
    # Create sample unmet need insight
    try:
        supabase.table('insights').insert({
            'insight_type': 'unmet_need',
            'title': 'Feature requests',
            'description': 'Users are requesting better playlist customization and discovery features',
            'data': {'needs': ['better recommendations', 'more variety', 'ui improvements']},
            'confidence': 0.8
        }).execute()
        print("Created unmet need insight")
    except Exception as e:
        print(f"Error creating unmet need insight: {e}")
    
    # Create sample recommendation
    try:
        supabase.table('insights').insert({
            'insight_type': 'recommendation',
            'title': 'Improve recommendation algorithm',
            'description': 'Focus on reducing repetition in radio and playlist suggestions',
            'data': {'priority': 'high', 'category': 'product'},
            'confidence': 0.85
        }).execute()
        print("Created recommendation insight")
    except Exception as e:
        print(f"Error creating recommendation insight: {e}")
    
    print("Insights generated")

if __name__ == '__main__':
    analyze_reviews()
