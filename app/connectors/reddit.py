import time
from typing import List, Dict, Optional
from loguru import logger
from config import settings

try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False
    logger.warning("PRAW not installed, Reddit connector will not function")


class RedditConnector:
    """Connector for fetching Reddit discussions"""
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        if not PRAW_AVAILABLE:
            raise ImportError("PRAW library is required. Install with: pip install praw")
        
        self.client_id = client_id or settings.reddit_client_id
        self.client_secret = client_secret or settings.reddit_client_secret
        self.user_agent = settings.reddit_user_agent
        
        if not self.client_id or not self.client_secret:
            logger.warning("Reddit credentials not provided. Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env")
        
        try:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            )
            # Test connection
            self.reddit.user.me()
            logger.info("Reddit API connection successful")
        except Exception as e:
            logger.error(f"Failed to connect to Reddit API: {e}")
            self.reddit = None
    
    def fetch_subreddit_posts(self, subreddit: str, limit: int = 500) -> List[Dict]:
        """
        Fetch posts from subreddit (limited to 500 to control token usage)
        
        Args:
            subreddit: Subreddit name (e.g., 'spotify', 'music')
            limit: Maximum number of posts to fetch
            
        Returns:
            List of post dictionaries
        """
        logger.info(f"Fetching posts from r/{subreddit} (limit: {limit})")
        
        if not self.reddit:
            logger.error("Reddit API not connected")
            return []
        
        posts = []
        
        try:
            subreddit_obj = self.reddit.subreddit(subreddit)
            
            for submission in subreddit_obj.new(limit=limit):
                post = self._parse_post(submission)
                if post:
                    posts.append(post)
                
                # Rate limiting
                time.sleep(0.1)
            
            logger.info(f"Successfully fetched {len(posts)} posts from r/{subreddit}")
            
        except Exception as e:
            logger.error(f"Error fetching posts from r/{subreddit}: {e}")
        
        return posts
    
    def fetch_comments(self, post_id: str, limit: int = 100) -> List[Dict]:
        """
        Fetch comments for a specific post
        
        Args:
            post_id: Reddit post ID
            limit: Maximum number of comments to fetch
            
        Returns:
            List of comment dictionaries
        """
        logger.info(f"Fetching comments for post {post_id}")
        
        if not self.reddit:
            logger.error("Reddit API not connected")
            return []
        
        comments = []
        
        try:
            submission = self.reddit.submission(id=post_id)
            submission.comments.replace_more(limit=0)
            
            for comment in submission.comments.list()[:limit]:
                comment_data = self._parse_comment(comment)
                if comment_data:
                    comments.append(comment_data)
            
            logger.info(f"Successfully fetched {len(comments)} comments")
            
        except Exception as e:
            logger.error(f"Error fetching comments for post {post_id}: {e}")
        
        return comments
    
    def fetch_search_results(self, query: str, limit: int = 500) -> List[Dict]:
        """
        Fetch posts matching a search query
        
        Args:
            query: Search query
            limit: Maximum number of results to fetch
            
        Returns:
            List of post dictionaries
        """
        logger.info(f"Searching Reddit for: {query}")
        
        if not self.reddit:
            logger.error("Reddit API not connected")
            return []
        
        posts = []
        
        try:
            for submission in self.reddit.subreddit("all").search(query, limit=limit):
                post = self._parse_post(submission)
                if post:
                    posts.append(post)
                
                time.sleep(0.1)
            
            logger.info(f"Successfully fetched {len(posts)} search results")
            
        except Exception as e:
            logger.error(f"Error searching Reddit: {e}")
        
        return posts
    
    def _parse_post(self, submission) -> Dict:
        """Parse a Reddit submission"""
        try:
            return {
                'id': submission.id,
                'title': submission.title,
                'content': submission.selftext if hasattr(submission, 'selftext') else '',
                'author': str(submission.author) if submission.author else '[deleted]',
                'subreddit': str(submission.subreddit),
                'score': submission.score,
                'num_comments': submission.num_comments,
                'created_utc': submission.created_utc,
                'url': submission.url,
                'source': 'reddit',
                'collected_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"Error parsing post: {e}")
            return {}
    
    def _parse_comment(self, comment) -> Dict:
        """Parse a Reddit comment"""
        try:
            return {
                'id': comment.id,
                'content': comment.body if hasattr(comment, 'body') else '',
                'author': str(comment.author) if comment.author else '[deleted]',
                'score': comment.score,
                'parent_id': comment.parent_id,
                'created_utc': comment.created_utc,
                'source': 'reddit',
                'collected_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"Error parsing comment: {e}")
            return {}
    
    def fetch_spotify_related_content(self, limit: int = 500) -> List[Dict]:
        """
        Fetch Spotify-related content from multiple subreddits
        
        Args:
            limit: Maximum number of posts per subreddit
            
        Returns:
            List of post dictionaries
        """
        logger.info("Fetching Spotify-related content from Reddit")
        
        subreddits = ['spotify', 'music', 'listentothis', 'ifyoulikeblank']
        all_posts = []
        
        for subreddit in subreddits:
            try:
                posts = self.fetch_subreddit_posts(subreddit, limit=limit)
                all_posts.extend(posts)
                time.sleep(1)  # Rate limiting between subreddits
            except Exception as e:
                logger.error(f"Error fetching from r/{subreddit}: {e}")
        
        logger.info(f"Total Spotify-related posts fetched: {len(all_posts)}")
        return all_posts
