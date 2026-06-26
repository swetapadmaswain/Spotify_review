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

# Import Play Store connector (only working connector)
try:
    from app.connectors.play_store import PlayStoreConnector
except ImportError as e:
    print(f"ERROR importing Play Store connector: {e}")
    sys.exit(1)

def collect_reviews():
    """Collect reviews from Play Store (only working connector)"""
    print("Starting data collection from Play Store...")
    
    # Create collection run record
    run_data = {
        'source': 'playstore',
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
    all_reviews = []
    
    # Collect from Play Store (Spotify package: com.spotify.music) - 10,000 reviews
    print("Collecting from Play Store (10,000 reviews)...")
    try:
        play_store = PlayStoreConnector(package_name='com.spotify.music')
        play_reviews = play_store.fetch_reviews(sort='newest', count=10000)
        print(f"Collected {len(play_reviews)} reviews from Play Store")
        
        for review in play_reviews:
            all_reviews.append({
                'source': 'playstore',
                'review_text': review.get('content', ''),
                'rating': review.get('rating'),
                'author': review.get('author', 'Anonymous'),
                'date': datetime.utcnow().isoformat(),
                'metadata': {'version': review.get('version', 'Unknown')},
                'collection_run_id': run_id
            })
    except Exception as e:
        print(f"ERROR collecting from Play Store: {e}")
    
    # Store in Supabase
    print(f"Storing {len(all_reviews)} reviews in Supabase...")
    for review in all_reviews:
        try:
            supabase.table('raw_reviews').insert(review).execute()
            total_collected += 1
            if total_collected % 100 == 0:
                print(f"Inserted {total_collected}/{len(all_reviews)} reviews...")
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
