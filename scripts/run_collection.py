import os
import sys
from datetime import datetime
from supabase import create_client

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

supabase = createClient(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

def collect_reviews():
    """Collect reviews from all sources"""
    print("Starting data collection...")
    
    # Create collection run record
    run_data = {
        'source': 'all',
        'start_time': datetime.utcnow().isoformat(),
        'status': 'running'
    }
    
    run_result = supabase.table('data_collection_runs').insert(run_data).execute()
    run_id = run_result.data[0]['id']
    
    total_collected = 0
    sources = []
    
    # For now, we'll create sample data since actual connectors need API keys
    # In production, replace this with actual connector calls
    
    # Sample App Store reviews
    sample_appstore = [
        {
            'source': 'appstore',
            'review_text': 'The recommendation algorithm is terrible. I keep hearing the same songs.',
            'rating': 2,
            'author': 'user123',
            'date': datetime.utcnow().isoformat(),
            'metadata': {'version': '8.8.0'}
        },
        {
            'source': 'appstore',
            'review_text': 'Love the new discovery features! Found so many great artists.',
            'rating': 5,
            'author': 'music_fan',
            'date': datetime.utcnow().isoformat(),
            'metadata': {'version': '8.8.0'}
        }
    ]
    
    # Sample Play Store reviews
    sample_playstore = [
        {
            'source': 'playstore',
            'review_text': 'Why does the radio play the same 50 songs? Need more variety.',
            'rating': 3,
            'author': 'android_user',
            'date': datetime.utcnow().isoformat(),
            'metadata': {'version': '8.8.0'}
        }
    ]
    
    # Sample Reddit posts
    sample_reddit = [
        {
            'source': 'reddit',
            'review_text': 'Does anyone else feel like Discover Weekly has gotten worse lately?',
            'rating': None,
            'author': 'reddit_user',
            'date': datetime.utcnow().isoformat(),
            'metadata': {'subreddit': 'spotify'}
        }
    ]
    
    all_reviews = sample_appstore + sample_playstore + sample_reddit
    
    # Store in Supabase
    for review in all_reviews:
        review['collection_run_id'] = run_id
        supabase.table('raw_reviews').insert(review).execute()
        total_collected += 1
    
    # Update collection run status
    supabase.table('data_collection_runs').update({
        'end_time': datetime.utcnow().isoformat(),
        'records_collected': total_collected,
        'status': 'completed'
    }).eq('id', run_id).execute()
    
    print(f"Collection completed. Total reviews collected: {total_collected}")
    return total_collected

if __name__ == '__main__':
    collect_reviews()
