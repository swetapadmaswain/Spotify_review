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

# Import connectors
try:
    from app.connectors.app_store import AppStoreConnector
    from app.connectors.play_store import PlayStoreConnector
    from app.connectors.forum import ForumConnector
except ImportError as e:
    print(f"ERROR importing connectors: {e}")
    sys.exit(1)

def collect_reviews():
    """Collect reviews from all sources using real APIs"""
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
    all_reviews = []
    
    # Collect from App Store (Spotify app ID: 324684580)
    print("Collecting from App Store...")
    try:
        app_store = AppStoreConnector(app_id='324684580')
        app_reviews = app_store.fetch_reviews(limit=50)
        print(f"Collected {len(app_reviews)} reviews from App Store")
        
        for review in app_reviews:
            all_reviews.append({
                'source': 'appstore',
                'review_text': review.get('content', ''),
                'rating': review.get('rating'),
                'author': review.get('author', 'Anonymous'),
                'date': datetime.utcnow().isoformat(),
                'metadata': {'version': review.get('version', 'Unknown'), 'title': review.get('title', '')},
                'collection_run_id': run_id
            })
    except Exception as e:
        print(f"ERROR collecting from App Store: {e}")
    
    # Collect from Play Store (Spotify package: com.spotify.music)
    print("Collecting from Play Store...")
    try:
        play_store = PlayStoreConnector(package_name='com.spotify.music')
        play_reviews = play_store.fetch_reviews(sort='newest', count=50)
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
    
    # Collect from Spotify Community Forums
    print("Collecting from Spotify Community Forums...")
    try:
        forum = ForumConnector()
        forum_threads = forum.scrape_threads(category='discovery', limit=30)
        print(f"Collected {len(forum_threads)} threads from forums")
        
        for thread in forum_threads:
            all_reviews.append({
                'source': 'forum',
                'review_text': thread.get('title', '') + ' ' + thread.get('comments', ''),
                'rating': None,
                'author': thread.get('author', 'Anonymous'),
                'date': datetime.utcnow().isoformat(),
                'metadata': {'url': thread.get('url', ''), 'category': 'discovery'},
                'collection_run_id': run_id
            })
    except Exception as e:
        print(f"ERROR collecting from forums: {e}")
    
    # Store in Supabase
    print(f"Storing {len(all_reviews)} reviews in Supabase...")
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
