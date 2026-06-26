import time
from typing import List, Dict, Optional
from loguru import logger
from config import settings

try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    logger.warning("tweepy not installed, Twitter connector will not function")


class SocialMediaConnector:
    """Connector for fetching social media conversations"""
    
    def __init__(self, credentials: Optional[Dict] = None):
        self.credentials = credentials or {}
        self.twitter_client = None
        
        # Initialize Twitter client if credentials are available
        if TWEEPY_AVAILABLE:
            self._init_twitter_client()
    
    def _init_twitter_client(self):
        """Initialize Twitter API client"""
        try:
            api_key = self.credentials.get('twitter_api_key') or settings.twitter_api_key
            api_secret = self.credentials.get('twitter_api_secret') or settings.twitter_api_secret
            access_token = self.credentials.get('twitter_access_token') or settings.twitter_access_token
            access_secret = self.credentials.get('twitter_access_secret') or settings.twitter_access_secret
            bearer_token = self.credentials.get('twitter_bearer_token') or settings.twitter_bearer_token
            
            if bearer_token:
                # Use Twitter API v2 with bearer token
                self.twitter_client = tweepy.Client(bearer_token=bearer_token)
                logger.info("Twitter API v2 client initialized")
            elif all([api_key, api_secret, access_token, access_secret]):
                # Use Twitter API v1.1 with OAuth
                auth = tweepy.OAuthHandler(api_key, api_secret)
                auth.set_access_token(access_token, access_secret)
                self.twitter_client = tweepy.API(auth)
                logger.info("Twitter API v1.1 client initialized")
            else:
                logger.warning("Twitter credentials not provided")
                
        except Exception as e:
            logger.error(f"Failed to initialize Twitter client: {e}")
    
    def fetch_mentions(self, query: str = '#spotify', limit: int = 500) -> List[Dict]:
        """
        Fetch Twitter mentions and hashtags (limited to 500 to control token usage)
        
        Args:
            query: Search query (hashtag, mention, or keyword)
            limit: Maximum number of tweets to fetch
            
        Returns:
            List of tweet dictionaries
        """
        logger.info(f"Fetching Twitter mentions for query: {query} (limit: {limit})")
        
        if not self.twitter_client:
            logger.error("Twitter client not initialized")
            return []
        
        tweets = []
        
        try:
            if isinstance(self.twitter_client, tweepy.Client):
                # Twitter API v2
                response = self.twitter_client.search_recent_tweets(
                    query=query,
                    max_results=min(limit, 100),
                    tweet_fields=['created_at', 'author_id', 'public_metrics', 'lang']
                )
                
                if response.data:
                    for tweet in response.data:
                        tweet_data = self._parse_tweet_v2(tweet)
                        if tweet_data:
                            tweets.append(tweet_data)
                            
                            # Fetch user info
                            if tweet.author_id:
                                user_info = self._get_user_info_v2(tweet.author_id)
                                tweet_data['author'] = user_info.get('username', 'Anonymous')
                
            else:
                # Twitter API v1.1
                tweets_data = self.twitter_client.search_tweets(
                    q=query,
                    count=min(limit, 100),
                    tweet_mode='extended'
                )
                
                for tweet in tweets_data:
                    tweet_data = self._parse_tweet_v1(tweet)
                    if tweet_data:
                        tweets.append(tweet_data)
            
            logger.info(f"Successfully fetched {len(tweets)} tweets")
            
        except Exception as e:
            logger.error(f"Error fetching Twitter mentions: {e}")
        
        return tweets
    
    def _parse_tweet_v2(self, tweet) -> Dict:
        """Parse tweet from Twitter API v2"""
        try:
            return {
                'id': tweet.id,
                'content': tweet.text,
                'author': None,  # Will be filled separately
                'created_at': tweet.created_at.isoformat() if tweet.created_at else '',
                'public_metrics': tweet.public_metrics if hasattr(tweet, 'public_metrics') else {},
                'lang': tweet.lang if hasattr(tweet, 'lang') else 'en',
                'source': 'twitter',
                'collected_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"Error parsing tweet v2: {e}")
            return {}
    
    def _parse_tweet_v1(self, tweet) -> Dict:
        """Parse tweet from Twitter API v1.1"""
        try:
            return {
                'id': tweet.id_str,
                'content': tweet.full_text,
                'author': tweet.user.screen_name if tweet.user else 'Anonymous',
                'created_at': tweet.created_at.isoformat() if tweet.created_at else '',
                'retweet_count': tweet.retweet_count,
                'favorite_count': tweet.favorite_count,
                'lang': tweet.lang if hasattr(tweet, 'lang') else 'en',
                'source': 'twitter',
                'collected_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"Error parsing tweet v1: {e}")
            return {}
    
    def _get_user_info_v2(self, user_id: str) -> Dict:
        """Fetch user info using Twitter API v2"""
        try:
            response = self.twitter_client.get_user(id=user_id, user_fields=['username'])
            if response.data:
                return {
                    'id': response.data.id,
                    'username': response.data.username
                }
        except Exception as e:
            logger.error(f"Error fetching user info: {e}")
        return {}
    
    def fetch_facebook_posts(self, page_id: str, limit: int = 500) -> List[Dict]:
        """
        Fetch Facebook posts from a page
        
        Args:
            page_id: Facebook page ID
            limit: Maximum number of posts to fetch
            
        Returns:
            List of post dictionaries
        """
        logger.info(f"Fetching Facebook posts from page: {page_id}")
        
        # Facebook Graph API implementation
        # This requires proper Facebook app credentials
        posts = []
        
        try:
            access_token = settings.facebook_access_token
            if not access_token:
                logger.warning("Facebook access token not provided")
                return []
            
            url = f"https://graph.facebook.com/v18.0/{page_id}/posts"
            params = {
                'access_token': access_token,
                'limit': min(limit, 100),
                'fields': 'id,message,created_time,permalink_url,likes.summary(true),comments.summary(true)'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            for post in data.get('data', []):
                post_data = self._parse_facebook_post(post)
                if post_data:
                    posts.append(post_data)
            
            logger.info(f"Successfully fetched {len(posts)} Facebook posts")
            
        except Exception as e:
            logger.error(f"Error fetching Facebook posts: {e}")
        
        return posts
    
    def _parse_facebook_post(self, post: Dict) -> Dict:
        """Parse Facebook post data"""
        try:
            return {
                'id': post.get('id'),
                'content': post.get('message', ''),
                'created_at': post.get('created_time', ''),
                'url': post.get('permalink_url', ''),
                'likes': post.get('likes', {}).get('summary', {}).get('total_count', 0),
                'comments': post.get('comments', {}).get('summary', {}).get('total_count', 0),
                'source': 'facebook',
                'collected_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"Error parsing Facebook post: {e}")
            return {}
    
    def fetch_instagram_mentions(self, hashtag: str, limit: int = 500) -> List[Dict]:
        """
        Fetch Instagram posts with a hashtag
        
        Args:
            hashtag: Hashtag to search (without #)
            limit: Maximum number of posts to fetch
            
        Returns:
            List of post dictionaries
        """
        logger.info(f"Fetching Instagram posts for hashtag: #{hashtag}")
        
        # Instagram Basic Display API or Graph API
        # This requires proper Instagram app credentials
        posts = []
        
        try:
            access_token = settings.facebook_access_token  # Instagram uses same access token
            if not access_token:
                logger.warning("Instagram access token not provided")
                return []
            
            # Instagram hashtag search requires Business/Creator account
            url = f"https://graph.facebook.com/v18.0/ig_hashtag_id"
            # This is a simplified implementation
            # Actual implementation requires Instagram Business account setup
            
            logger.warning("Instagram hashtag search requires Business account setup")
            
        except Exception as e:
            logger.error(f"Error fetching Instagram posts: {e}")
        
        return posts
    
    def fetch_spotify_social_mentions(self, limit: int = 500) -> List[Dict]:
        """
        Fetch Spotify-related mentions across social media platforms
        
        Args:
            limit: Maximum mentions per platform
            
        Returns:
            List of mention dictionaries
        """
        logger.info("Fetching Spotify-related social media mentions")
        
        all_mentions = []
        
        # Twitter mentions
        queries = ['#spotify', '@Spotify', 'spotify discovery', 'spotify recommendations']
        for query in queries:
            try:
                tweets = self.fetch_mentions(query, limit=limit//len(queries))
                all_mentions.extend(tweets)
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"Error fetching tweets for {query}: {e}")
        
        # Facebook posts (Spotify official page)
        try:
            facebook_posts = self.fetch_facebook_posts('Spotify', limit=limit)
            all_mentions.extend(facebook_posts)
        except Exception as e:
            logger.error(f"Error fetching Facebook posts: {e}")
        
        logger.info(f"Total social media mentions fetched: {len(all_mentions)}")
        return all_mentions
