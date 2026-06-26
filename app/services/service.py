import re
import hashlib
from typing import List, Dict, Optional, Set
from loguru import logger
from difflib import SequenceMatcher


class DataQualityService:
    """Service for validating and cleaning data"""
    
    def __init__(self):
        self.required_fields = {
            'appstore': ['id', 'content', 'author', 'rating'],
            'playstore': ['id', 'content', 'author', 'rating'],
            'reddit': ['id', 'content', 'author'],
            'forum': ['id', 'content', 'author'],
            'twitter': ['id', 'content'],
            'facebook': ['id', 'content']
        }
    
    def validate_batch(self, data: List[Dict], source: str) -> Dict:
        """
        Validate a batch of data
        
        Args:
            data: List of data records
            source: Data source identifier
            
        Returns:
            Dictionary with validation results
        """
        logger.info(f"Validating {len(data)} records from {source}")
        
        results = {
            'total': len(data),
            'valid': 0,
            'invalid': 0,
            'errors': []
        }
        
        required = self.required_fields.get(source, [])
        
        for i, record in enumerate(data):
            errors = self._validate_record(record, required)
            
            if errors:
                results['invalid'] += 1
                results['errors'].append({
                    'index': i,
                    'errors': errors
                })
            else:
                results['valid'] += 1
        
        logger.info(f"Validation complete: {results['valid']} valid, {results['invalid']} invalid")
        return results
    
    def _validate_record(self, record: Dict, required_fields: List[str]) -> List[str]:
        """Validate a single record"""
        errors = []
        
        # Check required fields
        for field in required_fields:
            if field not in record or record[field] is None:
                errors.append(f"Missing required field: {field}")
            elif field == 'content' and not isinstance(record[field], str):
                errors.append(f"Field 'content' must be a string")
            elif field == 'content' and len(str(record[field])) < 10:
                errors.append(f"Field 'content' too short (minimum 10 characters)")
        
        # Validate data types
        if 'rating' in record and record['rating'] is not None:
            try:
                rating = int(record['rating'])
                if not 1 <= rating <= 5:
                    errors.append(f"Rating must be between 1 and 5, got {rating}")
            except (ValueError, TypeError):
                errors.append(f"Rating must be an integer")
        
        # Validate text encoding
        for field in ['title', 'content', 'author']:
            if field in record and record[field]:
                try:
                    str(record[field]).encode('utf-8')
                except UnicodeEncodeError:
                    errors.append(f"Field '{field}' contains invalid characters")
        
        return errors
    
    def clean_data(self, data: List[Dict], source: str) -> List[Dict]:
        """
        Clean and normalize data
        
        Args:
            data: List of data records
            source: Data source identifier
            
        Returns:
            List of cleaned records
        """
        logger.info(f"Cleaning {len(data)} records from {source}")
        
        cleaned_data = []
        
        for record in data:
            try:
                cleaned_record = self._clean_record(record, source)
                cleaned_record['source'] = source
                cleaned_data.append(cleaned_record)
            except Exception as e:
                logger.error(f"Error cleaning record: {e}")
                continue
        
        logger.info(f"Cleaned {len(cleaned_data)} records")
        return cleaned_data
    
    def _clean_record(self, record: Dict, source: str) -> Dict:
        """Clean a single record"""
        cleaned = record.copy()
        
        # Remove HTML tags
        for field in ['title', 'content']:
            if field in cleaned_record:
                cleaned[field] = self._remove_html_tags(str(cleaned[field]))
        
        # Normalize whitespace
        for field in ['title', 'content', 'author']:
            if field in cleaned_record:
                cleaned[field] = self._normalize_whitespace(str(cleaned[field]))
        
        # Handle missing values
        for field in ['title', 'author', 'version']:
            if field not in cleaned_record or not cleaned_record[field]:
                cleaned_record[field] = 'Unknown'
        
        # Normalize author names
        if 'author' in cleaned_record:
            cleaned_record['author'] = self._normalize_author(cleaned_record['author'])
        
        # Ensure source is set
        if 'source' not in cleaned_record:
            cleaned_record['source'] = source
        
        return cleaned_record
    
    def _remove_html_tags(self, text: str) -> str:
        """Remove HTML tags from text"""
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text"""
        return ' '.join(text.split())
    
    def _normalize_author(self, author: str) -> str:
        """Normalize author name"""
        if not author or author.lower() in ['anonymous', '[deleted]', 'unknown']:
            return 'Anonymous'
        return author.strip()


class DeduplicationService:
    """Service for detecting and removing duplicate records"""
    
    def __init__(self):
        self.hash_store: Dict[str, Set] = {}
        self.similarity_threshold = 0.9
    
    def is_duplicate(self, text: str, threshold: float = 0.9) -> bool:
        """
        Check if text is a duplicate using similarity hashing
        
        Args:
            text: Text to check
            threshold: Similarity threshold (0-1)
            
        Returns:
            True if duplicate, False otherwise
        """
        text_hash = self._compute_hash(text)
        
        # Check exact hash match
        if text_hash in self.hash_store:
            return True
        
        # Check for similar content
        for existing_hash in self.hash_store:
            similarity = self._compute_similarity(text_hash, existing_hash)
            if similarity >= threshold:
                return True
        
        return False
    
    def _compute_hash(self, text: str) -> str:
        """Compute a hash for the text"""
        # Normalize text before hashing
        normalized = ' '.join(text.lower().split())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _compute_similarity(self, hash1: str, hash2: str) -> float:
        """Compute similarity between two hashes"""
        # Simple hash comparison - in production, use MinHash or SimHash
        return 1.0 if hash1 == hash2 else 0.0
    
    def remove_duplicates(self, data: List[Dict], content_field: str = 'content') -> List[Dict]:
        """
        Remove duplicate records from a list
        
        Args:
            data: List of data records
            content_field: Field to use for duplicate detection
            
        Returns:
            List of deduplicated records
        """
        logger.info(f"Removing duplicates from {len(data)} records")
        
        seen_hashes = set()
        unique_data = []
        
        for record in data:
            content = record.get(content_field, '')
            if not content:
                continue
            
            content_hash = self._compute_hash(content)
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_data.append(record)
        
        removed = len(data) - len(unique_data)
        logger.info(f"Removed {removed} duplicate records")
        
        return unique_data
    
    def find_near_duplicates(self, data: List[Dict], content_field: str = 'content', 
                           threshold: float = 0.9) -> List[tuple]:
        """
        Find near-duplicate records using similarity comparison
        
        Args:
            data: List of data records
            content_field: Field to compare
            threshold: Similarity threshold
            
        Returns:
            List of tuples (index1, index2, similarity)
        """
        logger.info(f"Finding near-duplicates in {len(data)} records")
        
        duplicates = []
        
        for i in range(len(data)):
            for j in range(i + 1, len(data)):
                content1 = data[i].get(content_field, '')
                content2 = data[j].get(content_field, '')
                
                if not content1 or not content2:
                    continue
                
                similarity = SequenceMatcher(None, content1, content2).ratio()
                
                if similarity >= threshold:
                    duplicates.append((i, j, similarity))
        
        logger.info(f"Found {len(duplicates)} near-duplicate pairs")
        return duplicates
    
    def add_to_hash_store(self, source: str, text_hash: str):
        """Add a hash to the store for a specific source"""
        if source not in self.hash_store:
            self.hash_store[source] = set()
        self.hash_store[source].add(text_hash)
