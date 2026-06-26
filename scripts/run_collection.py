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

supabase = createClient(supabase_url, supabase_key)

def collect_reviews():
    """Collect reviews from all sources"""
    print("Starting data collection...")
    
    # Create collection run record
    run_data = {
        'source': 'all',
        'start_time': datetime.utcnow().isoformat(),
        'status': 'running'
    }
    
    try:
        run_result = supabase.table('data_collection_runs').insert(run_data).execute()
        run_id = run_result.data[0]['id']
        print(f"Created collection run: {run_id}")
    except Exception as e:
        print(f"ERROR creating collection run: {e}")
        sys.exit(1)
    
    total_collected = 0
    
    # Sample reviews
    all_reviews = [
        {
            'source': 'appstore',
            'review_text': 'The recommendation algorithm is terrible. I keep hearing the same songs.',
            'rating': 2,
            'author': 'user123',
            'date': datetime.utcnow().isoformat(),
            'metadata': {'version': '8.8.0'},
            'collection_run_id': run_id
        },
        {
            'source': 'appstore',
            'review_text': 'Love the new discovery features! Found so many great artists.',
            'rating': 5,
            'author': 'music_fan',
            'date': datetime.utcnow().isoformat(),
            'metadata': {'version': '8.8.0'},
            'collection_run_id': run_id
        },
        {
            'source': 'playstore',
            'review_text': 'Why does the radio play the same 50 songs? Need more variety.',
            'rating': 3,
            'author': 'android_user',
            'date': datetime.utcnow().isoformat(),
            'metadata': {'version': '8.8.0'},
            'collection_run_id': run_id
        },
        {
            'source': 'reddit',
            'review_text': 'Does anyone else feel like Discover Weekly has gotten worse lately?',
            'rating': None,
            'author': 'reddit_user',
            'date': datetime.utcnow().isoformat(),
            'metadata': {'subreddit': 'spotify'},
            'collection_run_id': run_id
        }
    ]
    
    # Store in Supabase
    for review in all_reviews:
        try:
            supabase.table('raw_reviews').insert(review).execute()
            total_collected += 1
            print(f"Inserted review {total_collected}/{len(all_reviews)}")
        except Exception as e:
            print(f"ERROR inserting review: {e}")
    
    # Update collection run status
    try:
        supabase.table('data_collection_runs').update({
            'end_time': datetime.utcnow().isoformat(),
            'records_collected': total_collected,
            'status': 'completed'
        }).eq('id', run_id).execute()
    except Exception as e:
        print(f"ERROR updating collection run: {e}")
    
    print(f"Collection completed. Total reviews collected: {total_collected}")
    return total_collected

if __name__ == '__main__':
    collect_reviews()
