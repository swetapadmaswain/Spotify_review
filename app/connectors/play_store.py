import requests
import time
from typing import List, Dict, Optional
from loguru import logger
from config import settings
try:
    from google_play_scraper import app, reviews
except ImportError:
    logger.warning("google-play-scraper not installed, using fallback method")


class PlayStoreConnector:
    """Connector for fetching Play Store reviews"""
    
    def __init__(self, package_name: Optional[str] = None):
        self.package_name = package_name or settings.play_store_package_name
        
    def fetch_reviews(self, sort: str = 'newest', count: int = 500) -> List[Dict]:
        """
        Fetch reviews from Play Store (limited to 500 to control token usage)
        
        Args:
            sort: Sorting method ('newest', 'rating', 'relevance')
            count: Maximum number of reviews to fetch
            
        Returns:
            List of review dictionaries
        """
        logger.info(f"Fetching Play Store reviews (package: {self.package_name}, count: {count})")
        
        reviews = []
        
        try:
            # Try using google-play-scraper
            from google_play_scraper import Sort
            
            sort_map = {
                'newest': Sort.NEWEST,
                'rating': Sort.RATING,
                'relevance': Sort.RELEVANCE
            }
            
            sort_option = sort_map.get(sort, Sort.NEWEST)
            
            # Fetch reviews in batches
            continuation_token = None
            while len(reviews) < count:
                batch_count = min(count - len(reviews), 100)
                
                result, continuation_token = reviews(
                    self.package_name,
                    lang='en',
                    country='us',
                    sort=sort_option,
                    count=batch_count,
                    continuation_token=continuation_token
                )
                
                for review in result:
                    parsed_review = self._parse_review(review)
                    if parsed_review:
                        reviews.append(parsed_review)
                
                if not continuation_token:
                    break
                
                # Rate limiting
                time.sleep(0.5)
                
        except ImportError:
            logger.warning("google-play-scraper not available, using web scraping fallback")
            reviews = self._fetch_reviews_fallback(count)
        except Exception as e:
            logger.error(f"Error fetching Play Store reviews: {e}")
        
        logger.info(f"Successfully fetched {len(reviews)} Play Store reviews")
        return reviews
    
    def _parse_review(self, review: Dict) -> Dict:
        """Parse a single review from google-play-scraper"""
        return {
            'id': review.get('reviewId'),
            'title': review.get('title', ''),
            'content': review.get('content', ''),
            'author': review.get('userName', 'Anonymous'),
            'rating': review.get('score', 0),
            'version': review.get('reviewCreatedVersion', 'Unknown'),
            'at': review.get('at'),
            'source': 'playstore',
            'collected_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _fetch_reviews_fallback(self, count: int = 500) -> List[Dict]:
        """Fallback method using web scraping"""
        logger.info("Using web scraping fallback for Play Store reviews")
        
        reviews = []
        url = f"https://play.google.com/store/apps/details?id={self.package_name}&showAllReviews=true"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            
            # Parse HTML and extract reviews
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            review_elements = soup.find_all('div', class_='d15Mdf')
            
            for element in review_elements[:count]:
                try:
                    review = self._parse_html_review(element)
                    if review:
                        reviews.append(review)
                except Exception as e:
                    logger.error(f"Error parsing HTML review: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in fallback method: {e}")
        
        return reviews
    
    def _parse_html_review(self, element) -> Optional[Dict]:
        """Parse review from HTML element"""
        try:
            author = element.find('span', class_='X43Kjb')
            rating = element.find('div', role='img')
            content = element.find('span', class_='js793A')
            
            return {
                'id': None,
                'title': '',
                'content': content.get_text() if content else '',
                'author': author.get_text() if author else 'Anonymous',
                'rating': self._extract_rating(rating) if rating else 0,
                'version': 'Unknown',
                'source': 'playstore',
                'collected_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"Error parsing HTML review element: {e}")
            return None
    
    def _extract_rating(self, rating_element) -> int:
        """Extract rating from aria-label"""
        try:
            aria_label = rating_element.get('aria-label', '')
            # Extract number from "Rated 5 stars out of five"
            import re
            match = re.search(r'Rated (\d+)', aria_label)
            return int(match.group(1)) if match else 0
        except:
            return 0
    
    def fetch_app_info(self) -> Dict:
        """Fetch app information from Play Store"""
        logger.info(f"Fetching Play Store app info for {self.package_name}")
        
        try:
            from google_play_scraper import app
            info = app(self.package_name)
            
            return {
                'title': info.get('title'),
                'description': info.get('description'),
                'rating': info.get('score'),
                'reviews': info.get('reviews'),
                'installs': info.get('installs'),
                'version': info.get('version'),
                'updated': info.get('updated')
            }
        except Exception as e:
            logger.error(f"Error fetching app info: {e}")
            return {}
