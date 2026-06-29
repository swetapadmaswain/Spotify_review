import os
import sys
from datetime import datetime
from supabase import create_client

# Add backend directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
backend_dir = os.path.join(repo_root, 'backend')
sys.path.insert(0, backend_dir)

supabase_url = (os.getenv('SUPABASE_URL') or '').strip()
supabase_key = (os.getenv('SUPABASE_SERVICE_ROLE_KEY') or '').strip()

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

    # Fetch all reviews that haven't been analyzed (no limit)
    response = supabase.table('raw_reviews').select('id, review_text').execute()
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

TOPIC_LABELS = {
    'recommendation': 'Music Recommendations',
    'ui_ux': 'User Interface & Experience',
    'performance': 'App Performance & Stability',
    'content': 'Music Content & Catalog',
    'features': 'Features & Functionality',
    'general': 'General Feedback',
}

CATEGORY_MAP = {
    'recommendation': 'product',
    'ui_ux': 'design',
    'performance': 'engineering',
    'content': 'content',
    'features': 'product',
    'general': 'product',
}


def _clear_table(table):
    try:
        supabase.table(table).delete().neq('id', 0).execute()
    except Exception as e:
        print(f"Warning: could not clear {table}: {e}")


def generate_insights():
    """Generate insights from analyzed data into the dedicated insight tables
    that the backend API and dashboard read from."""
    print("Generating insights...")
    from collections import Counter

    # Clear dedicated tables to avoid duplicates on re-run
    for tbl in ['roadmap_items', 'recommendations', 'unmet_needs',
                'root_cause_analysis', 'user_segments', 'pattern_insights']:
        _clear_table(tbl)

    # Pull analyzed data
    sentiment_rows = supabase.table('sentiment_analysis').select('sentiment').execute().data or []
    sentiments = [r['sentiment'] for r in sentiment_rows]
    topic_rows = supabase.table('topic_analysis').select('primary_topic').execute().data or []
    topics = [r['primary_topic'] for r in topic_rows]

    topic_counts = Counter(topics)
    sentiment_counts = Counter(sentiments)
    total_reviews = len(sentiments) or len(topics) or 1
    negative_total = sentiment_counts.get('negative', 0)

    # 1) pattern_insights — one per topic
    for topic, count in topic_counts.most_common():
        label = TOPIC_LABELS.get(topic, topic.title())
        try:
            supabase.table('pattern_insights').insert({
                'pattern_type': 'thematic',
                'pattern_description': f"{label} mentioned in {count} reviews ({round(count / total_reviews * 100)}% of feedback)",
                'frequency': count,
                'confidence': round(min(0.95, 0.5 + count / total_reviews), 2),
                'time_period': 'all_time',
            }).execute()
        except Exception as e:
            print(f"Error inserting pattern_insight ({topic}): {e}")
    print(f"Created {len(topic_counts)} pattern insights")

    # 2) user_segments — derived from topic focus
    for topic, count in topic_counts.most_common(4):
        label = TOPIC_LABELS.get(topic, topic.title())
        try:
            supabase.table('user_segments').insert({
                'segment_name': f"{label} Users",
                'segment_criteria': {'primary_topic': topic},
                'user_count': count,
                'primary_challenges': [label],
                'avg_sentiment': sentiment_counts.most_common(1)[0][0] if sentiment_counts else 'neutral',
            }).execute()
        except Exception as e:
            print(f"Error inserting user_segment ({topic}): {e}")
    print("Created user segments")

    # 3) unmet_needs — based on negative sentiment around topics
    for i, (topic, count) in enumerate(topic_counts.most_common(5)):
        label = TOPIC_LABELS.get(topic, topic.title())
        try:
            supabase.table('unmet_needs').insert({
                'need_description': f"Improve {label.lower()} based on recurring user feedback",
                'need_category': CATEGORY_MAP.get(topic, 'product'),
                'request_count': count,
                'priority_score': round(min(1.0, count / total_reviews + (0.2 if i == 0 else 0)), 2),
                'strategic_impact': 'high' if i == 0 else ('medium' if i < 3 else 'low'),
            }).execute()
        except Exception as e:
            print(f"Error inserting unmet_need ({topic}): {e}")
    print("Created unmet needs")

    # 4) root_cause_analysis — for the most negative/common topic
    if topic_counts:
        top_topic, top_count = topic_counts.most_common(1)[0]
        label = TOPIC_LABELS.get(top_topic, top_topic.title())
        try:
            supabase.table('root_cause_analysis').insert({
                'issue_topic': label,
                'root_causes': {'analysis': f"{label} is the most discussed area with {top_count} mentions. "
                                            f"Negative sentiment appears in {negative_total} reviews overall."},
                'intermediate_factors': {'factors': f"Recurring mentions of {label.lower()} suggest unmet expectations."},
                'surface_symptoms': {'symptoms': f"{top_count} reviews reference {label.lower()}."},
                'confidence': 0.75,
            }).execute()
            print("Created root cause analysis")
        except Exception as e:
            print(f"Error inserting root_cause_analysis: {e}")

    # 5) recommendations + roadmap_items — actionable items per top topic
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    for i, (topic, count) in enumerate(topic_counts.most_common(4)):
        label = TOPIC_LABELS.get(topic, topic.title())
        priority = 'high' if i == 0 else ('medium' if i < 3 else 'low')
        rec_id = None
        try:
            rec = supabase.table('recommendations').insert({
                'title': f"Enhance {label}",
                'description': f"Prioritize improvements to {label.lower()} — referenced in {count} reviews.",
                'category': CATEGORY_MAP.get(topic, 'product'),
                'priority': priority,
                'complexity': 'medium',
                'expected_impact': 'high' if i == 0 else 'medium',
                'success_metrics': [f"Reduction in negative {label.lower()} feedback"],
                'dependencies': [],
            }).execute()
            if rec.data:
                rec_id = rec.data[0]['id']
        except Exception as e:
            print(f"Error inserting recommendation ({topic}): {e}")

        try:
            supabase.table('roadmap_items').insert({
                'title': f"Enhance {label}",
                'description': f"Roadmap item addressing {label.lower()} feedback.",
                'priority': priority,
                'estimated_effort': 'medium',
                'quarter': quarters[i % 4],
                'success_metrics': [f"Improved {label.lower()} satisfaction"],
                'dependencies': [],
                'recommendation_id': rec_id,
            }).execute()
        except Exception as e:
            print(f"Error inserting roadmap_item ({topic}): {e}")
    print("Created recommendations and roadmap items")

    print("Insights generated")

if __name__ == '__main__':
    analyze_reviews()
