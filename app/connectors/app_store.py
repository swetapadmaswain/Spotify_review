import requests
import time
from typing import List, Dict, Optional
from loguru import logger
from config import settings


class AppStoreConnector:
    """Connector for fetching App Store reviews"""
    
    def __init__(self, app_id: Optional[str] = None, api_key: Optional[str] = None):
        self.app_id = app_id or settings.app_store_app_id
        self.api_key = api_key or settings.app_store_api_key
        self.base_url = "https://api.appstoreconnect.apple.com/v1"
        self.reviews_url = f"https://itunes.apple.com/rss/customerreviews/page/1/id/{self.app_id}/sortby=mostrecent/json"
        
    def fetch_reviews(self, limit: int = 500, offset: int = 0) -> List[Dict]:
        """
        Fetch reviews from App Store RSS feed (limited to 500 to control token usage)
        
        Args:
            limit: Maximum number of reviews to fetch
            offset: Starting offset for pagination
            
        Returns:
            List of review dictionaries
        """
        logger.info(f"Fetching App Store reviews (limit: {limit}, offset: {offset})")
        
        reviews = []
        page = 1
        
        while len(reviews) < limit:
            try:
                # Use RSS feed for public reviews (no API key required)
                url = f"https://itunes.apple.com/rss/customerreviews/page/{page}/id/{self.app_id}/sortby=mostrecent/json"
                
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                entries = data.get('feed', {}).get('entry', [])
                
                if not entries:
                    logger.info(f"No more reviews found on page {page}")
                    break
                
                for entry in entries:
                    if len(reviews) >= limit:
                        break
                    
                    review = self._parse_review(entry)
                    if review:
                        reviews.append(review)
                
                page += 1
                
                # Rate limiting - respect Apple's terms
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching App Store reviews: {e}")
                break
        
        logger.info(f"Successfully fetched {len(reviews)} App Store reviews")
        return reviews
    
    def _parse_review(self, entry: Dict) -> Optional[Dict]:
        """Parse a single review entry from RSS feed"""
        try:
            author = entry.get('author', {})
            rating = entry.get('im:rating', {})
            content = entry.get('content', {})
            
            return {
                'id': entry.get('id'),
                'title': entry.get('title'),
                'content': content.get('label', '') if isinstance(content, dict) else str(content),
                'author': author.get('name', {}).get('label', 'Anonymous') if isinstance(author, dict) else str(author),
                'rating': int(rating.get('label', 0)) if isinstance(rating, dict) else 0,
                'version': entry.get('im:version', {}).get('label', 'Unknown') if isinstance(entry.get('im:version'), dict) else 'Unknown',
                'source': 'appstore',
                'collected_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"Error parsing review: {e}")
            return None
    
    def fetch_ratings(self) -> Dict:
        """
        Fetch rating distributions from App Store
        
        Returns:
            Dictionary with rating statistics
        """
        logger.info("Fetching App Store ratings")
        
        try:
            url = f"https://itunes.apple.com/lookup?id={self.app_id}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            app_info = data.get('results', [{}])[0]
            
            ratings = {
                'average_rating': app_info.get('averageUserRating', 0),
                'rating_count': app_info.get('userRatingCount', 0),
                'current_version_rating': app_info.get('averageUserRatingForCurrentVersion', 0),
                'current_version_count': app_info.get('userRatingCountForCurrentVersion', 0)
            }
            
            logger.info(f"Successfully fetched App Store ratings: {ratings}")
            return ratings
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching App Store ratings: {e}")
            return {}
