import requests
import time
from typing import List, Dict, Optional
from loguru import logger
from bs4 import BeautifulSoup


class ForumConnector:
    """Connector for scraping Spotify Community Forums"""
    
    def __init__(self, base_url: str = "https://community.spotify.com"):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def scrape_threads(self, category: str = 'discovery', limit: int = 500) -> List[Dict]:
        """
        Scrape forum threads from a category (limited to 500 to control token usage)
        
        Args:
            category: Forum category to scrape
            limit: Maximum number of threads to fetch
            
        Returns:
            List of thread dictionaries
        """
        logger.info(f"Scraping forum threads from category: {category} (limit: {limit})")
        
        threads = []
        
        # Spotify Community Forum URLs for different categories
        category_urls = {
            'discovery': f'{self.base_url}/t5/Discovery/ct-p/discovery',
            'help': f'{self.base_url}/t5/Help/ct-p/help',
            'ideas': f'{self.base_url}/t5/Ideas/ct-p/ideas',
            'mobile': f'{self.base_url}/t5/Mobile/ct-p/mobile',
            'desktop': f'{self.base_url}/t5/Desktop/ct-p/desktop'
        }
        
        url = category_urls.get(category, f'{self.base_url}/t5/Discovery/ct-p/discovery')
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find thread elements (adjust selectors based on actual forum structure)
            thread_elements = soup.find_all('li', class_='message-thread')
            
            for element in thread_elements[:limit]:
                try:
                    thread = self._parse_thread_element(element)
                    if thread:
                        threads.append(thread)
                        # Fetch comments for this thread
                        comments = self.scrape_thread_comments(thread['url'])
                        thread['comments'] = comments
                except Exception as e:
                    logger.error(f"Error parsing thread element: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(threads)} forum threads")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error scraping forum threads: {e}")
        
        return threads
    
    def scrape_thread_comments(self, thread_url: str, limit: int = 100) -> List[Dict]:
        """
        Scrape comments from a specific thread
        
        Args:
            thread_url: URL of the thread
            limit: Maximum number of comments to fetch
            
        Returns:
            List of comment dictionaries
        """
        logger.info(f"Scraping comments from thread: {thread_url}")
        
        comments = []
        
        try:
            response = requests.get(thread_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find comment elements
            comment_elements = soup.find_all('div', class_='message-body')
            
            for element in comment_elements[:limit]:
                try:
                    comment = self._parse_comment_element(element)
                    if comment:
                        comments.append(comment)
                except Exception as e:
                    logger.error(f"Error parsing comment element: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(comments)} comments")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error scraping thread comments: {e}")
        
        return comments
    
    def _parse_thread_element(self, element) -> Optional[Dict]:
        """Parse a thread element from HTML"""
        try:
            title_link = element.find('a', class_='message-subject')
            author = element.find('span', class_='user-name')
            date = element.find('span', class_='date')
            
            if not title_link:
                return None
            
            return {
                'id': element.get('data-message-id', ''),
                'title': title_link.get_text(strip=True),
                'url': self.base_url + title_link.get('href', ''),
                'author': author.get_text(strip=True) if author else 'Anonymous',
                'date': date.get_text(strip=True) if date else '',
                'source': 'forum',
                'collected_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"Error parsing thread element: {e}")
            return None
    
    def _parse_comment_element(self, element) -> Optional[Dict]:
        """Parse a comment element from HTML"""
        try:
            author = element.find('span', class_='user-name')
            content = element.find('div', class_='message-text')
            
            return {
                'id': element.get('data-message-id', ''),
                'content': content.get_text(strip=True) if content else '',
                'author': author.get_text(strip=True) if author else 'Anonymous',
                'source': 'forum',
                'collected_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"Error parsing comment element: {e}")
            return None
    
    def search_forum(self, query: str, limit: int = 500) -> List[Dict]:
        """
        Search the forum for specific terms
        
        Args:
            query: Search query
            limit: Maximum number of results to fetch
            
        Returns:
            List of thread dictionaries
        """
        logger.info(f"Searching forum for: {query}")
        
        threads = []
        
        try:
            search_url = f'{self.base_url}/t5/forums/searchpage/tab/message/page/q/{query}'
            response = requests.get(search_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            thread_elements = soup.find_all('li', class_='message-thread')
            
            for element in thread_elements[:limit]:
                try:
                    thread = self._parse_thread_element(element)
                    if thread:
                        threads.append(thread)
                except Exception as e:
                    logger.error(f"Error parsing search result: {e}")
                    continue
            
            logger.info(f"Found {len(threads)} threads matching query")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching forum: {e}")
        
        return threads
    
    def scrape_multiple_categories(self, categories: List[str], limit_per_category: int = 100) -> List[Dict]:
        """
        Scrape multiple forum categories
        
        Args:
            categories: List of category names to scrape
            limit_per_category: Maximum threads per category
            
        Returns:
            List of thread dictionaries
        """
        logger.info(f"Scraping {len(categories)} forum categories")
        
        all_threads = []
        
        for category in categories:
            try:
                threads = self.scrape_threads(category, limit=limit_per_category)
                all_threads.extend(threads)
                time.sleep(1)  # Rate limiting between categories
            except Exception as e:
                logger.error(f"Error scraping category {category}: {e}")
        
        logger.info(f"Total threads scraped: {len(all_threads)}")
        return all_threads
