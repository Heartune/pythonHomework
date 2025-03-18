"""
Book scraper module for the Library Management System.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import random
import pandas as pd
from datetime import datetime
import os
import logging
from ..logger import get_logger

logger = get_logger(__name__)

class BookScraper:
    """Class for scraping book information from various sources."""
    
    def __init__(self, cache_dir=None):
        """
        Initialize the book scraper.
        
        Args:
            cache_dir (str, optional): Directory to cache scraped data.
        """
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        # Set up cache directory
        if cache_dir:
            self.cache_dir = cache_dir
        else:
            self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'cache')
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_with_retry(self, url, max_retries=3, delay=1):
        """
        Get URL content with retry logic.
        
        Args:
            url (str): URL to fetch.
            max_retries (int): Maximum number of retries.
            delay (int): Delay between retries in seconds.
            
        Returns:
            requests.Response: Response object.
        """
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    sleep_time = delay * (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"Retrying in {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"Failed to fetch {url} after {max_retries} attempts")
                    raise
    
    def search_books_openlibrary(self, query, limit=10):
        """
        Search for books on OpenLibrary.
        
        Args:
            query (str): Search query.
            limit (int): Maximum number of results to return.
            
        Returns:
            list: List of book dictionaries.
        """
        try:
            # Check cache first
            cache_file = os.path.join(self.cache_dir, f"openlibrary_search_{query.replace(' ', '_')}.json")
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    if datetime.now().timestamp() - cache_data['timestamp'] < 86400:  # 24 hours
                        logger.info(f"Using cached data for query: {query}")
                        return cache_data['books'][:limit]
            
            # Construct the API URL
            url = f"https://openlibrary.org/search.json?q={query.replace(' ', '+')}&limit={limit}"
            
            # Make the request
            response = self._get_with_retry(url)
            data = response.json()
            
            # Process the results
            books = []
            for doc in data.get('docs', [])[:limit]:
                book = {
                    'title': doc.get('title', 'Unknown Title'),
                    'author': doc.get('author_name', ['Unknown Author'])[0] if doc.get('author_name') else 'Unknown Author',
                    'isbn': doc.get('isbn', [''])[0] if doc.get('isbn') else '',
                    'publisher': doc.get('publisher', ['Unknown Publisher'])[0] if doc.get('publisher') else 'Unknown Publisher',
                    'publication_year': doc.get('first_publish_year', None),
                    'category': doc.get('subject', ['Uncategorized'])[0] if doc.get('subject') else 'Uncategorized',
                    'description': f"Language: {', '.join(doc.get('language', ['Unknown']))}",
                    'cover_url': f"https://covers.openlibrary.org/b/id/{doc.get('cover_i', 0)}-M.jpg" if doc.get('cover_i') else None
                }
                books.append(book)
            
            # Cache the results
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().timestamp(),
                    'books': books
                }, f, ensure_ascii=False, indent=2)
            
            return books
        except Exception as e:
            logger.error(f"Error searching OpenLibrary: {e}")
            return []
    
    def get_book_details_openlibrary(self, isbn):
        """
        Get detailed book information from OpenLibrary by ISBN.
        
        Args:
            isbn (str): ISBN of the book.
            
        Returns:
            dict: Book details.
        """
        try:
            # Check cache first
            cache_file = os.path.join(self.cache_dir, f"openlibrary_book_{isbn}.json")
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    if datetime.now().timestamp() - cache_data['timestamp'] < 604800:  # 7 days
                        logger.info(f"Using cached data for ISBN: {isbn}")
                        return cache_data['book']
            
            # Construct the API URL
            url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
            
            # Make the request
            response = self._get_with_retry(url)
            data = response.json()
            
            # Process the result
            book_data = data.get(f"ISBN:{isbn}", {})
            if not book_data:
                logger.warning(f"No data found for ISBN: {isbn}")
                return None
            
            # Extract book details
            book = {
                'title': book_data.get('title', 'Unknown Title'),
                'author': book_data.get('authors', [{'name': 'Unknown Author'}])[0]['name'] if book_data.get('authors') else 'Unknown Author',
                'isbn': isbn,
                'publisher': book_data.get('publishers', [{'name': 'Unknown Publisher'}])[0]['name'] if book_data.get('publishers') else 'Unknown Publisher',
                'publication_year': book_data.get('publish_date', '').split()[-1] if book_data.get('publish_date') else None,
                'category': book_data.get('subjects', [{'name': 'Uncategorized'}])[0]['name'] if book_data.get('subjects') else 'Uncategorized',
                'description': book_data.get('notes', {}).get('value', '') if book_data.get('notes') else '',
                'cover_url': book_data.get('cover', {}).get('medium', '') if book_data.get('cover') else None,
                'number_of_pages': book_data.get('number_of_pages'),
                'weight': book_data.get('weight'),
                'dimensions': book_data.get('dimensions')
            }
            
            # Cache the result
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().timestamp(),
                    'book': book
                }, f, ensure_ascii=False, indent=2)
            
            return book
        except Exception as e:
            logger.error(f"Error getting book details from OpenLibrary: {e}")
            return None
    
    def search_books_google(self, query, limit=10):
        """
        Search for books on Google Books.
        
        Args:
            query (str): Search query.
            limit (int): Maximum number of results to return.
            
        Returns:
            list: List of book dictionaries.
        """
        try:
            # Check cache first
            cache_file = os.path.join(self.cache_dir, f"google_search_{query.replace(' ', '_')}.json")
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    if datetime.now().timestamp() - cache_data['timestamp'] < 86400:  # 24 hours
                        logger.info(f"Using cached data for query: {query}")
                        return cache_data['books'][:limit]
            
            # Construct the API URL
            url = f"https://www.googleapis.com/books/v1/volumes?q={query.replace(' ', '+')}&maxResults={limit}"
            
            # Make the request
            response = self._get_with_retry(url)
            data = response.json()
            
            # Process the results
            books = []
            for item in data.get('items', [])[:limit]:
                volume_info = item.get('volumeInfo', {})
                
                # Extract ISBNs if available
                isbn = ''
                if 'industryIdentifiers' in volume_info:
                    for identifier in volume_info['industryIdentifiers']:
                        if identifier.get('type') in ['ISBN_13', 'ISBN_10']:
                            isbn = identifier.get('identifier', '')
                            break
                
                book = {
                    'title': volume_info.get('title', 'Unknown Title'),
                    'author': volume_info.get('authors', ['Unknown Author'])[0] if volume_info.get('authors') else 'Unknown Author',
                    'isbn': isbn,
                    'publisher': volume_info.get('publisher', 'Unknown Publisher'),
                    'publication_year': volume_info.get('publishedDate', '').split('-')[0] if volume_info.get('publishedDate') else None,
                    'category': volume_info.get('categories', ['Uncategorized'])[0] if volume_info.get('categories') else 'Uncategorized',
                    'description': volume_info.get('description', ''),
                    'cover_url': volume_info.get('imageLinks', {}).get('thumbnail') if volume_info.get('imageLinks') else None,
                    'page_count': volume_info.get('pageCount'),
                    'language': volume_info.get('language')
                }
                books.append(book)
            
            # Cache the results
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().timestamp(),
                    'books': books
                }, f, ensure_ascii=False, indent=2)
            
            return books
        except Exception as e:
            logger.error(f"Error searching Google Books: {e}")
            return []
    
    def get_book_details_google(self, isbn):
        """
        Get detailed book information from Google Books by ISBN.
        
        Args:
            isbn (str): ISBN of the book.
            
        Returns:
            dict: Book details.
        """
        try:
            # Check cache first
            cache_file = os.path.join(self.cache_dir, f"google_book_{isbn}.json")
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    if datetime.now().timestamp() - cache_data['timestamp'] < 604800:  # 7 days
                        logger.info(f"Using cached data for ISBN: {isbn}")
                        return cache_data['book']
            
            # Construct the API URL
            url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
            
            # Make the request
            response = self._get_with_retry(url)
            data = response.json()
            
            # Process the result
            if data.get('totalItems', 0) == 0 or not data.get('items'):
                logger.warning(f"No data found for ISBN: {isbn}")
                return None
            
            volume_info = data['items'][0].get('volumeInfo', {})
            
            # Extract book details
            book = {
                'title': volume_info.get('title', 'Unknown Title'),
                'author': volume_info.get('authors', ['Unknown Author'])[0] if volume_info.get('authors') else 'Unknown Author',
                'isbn': isbn,
                'publisher': volume_info.get('publisher', 'Unknown Publisher'),
                'publication_year': volume_info.get('publishedDate', '').split('-')[0] if volume_info.get('publishedDate') else None,
                'category': volume_info.get('categories', ['Uncategorized'])[0] if volume_info.get('categories') else 'Uncategorized',
                'description': volume_info.get('description', ''),
                'cover_url': volume_info.get('imageLinks', {}).get('thumbnail') if volume_info.get('imageLinks') else None,
                'page_count': volume_info.get('pageCount'),
                'language': volume_info.get('language'),
                'average_rating': volume_info.get('averageRating'),
                'ratings_count': volume_info.get('ratingsCount')
            }
            
            # Cache the result
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().timestamp(),
                    'book': book
                }, f, ensure_ascii=False, indent=2)
            
            return book
        except Exception as e:
            logger.error(f"Error getting book details from Google Books: {e}")
            return None
    
    def search_books(self, query, limit=10, sources=None):
        """
        Search for books across multiple sources.
        
        Args:
            query (str): Search query.
            limit (int): Maximum number of results to return per source.
            sources (list, optional): List of sources to search. Defaults to ['openlibrary', 'google'].
            
        Returns:
            list: Combined list of book dictionaries.
        """
        if sources is None:
            sources = ['openlibrary', 'google']
        
        all_books = []
        
        if 'openlibrary' in sources:
            openlibrary_books = self.search_books_openlibrary(query, limit)
            for book in openlibrary_books:
                book['source'] = 'openlibrary'
                all_books.append(book)
        
        if 'google' in sources:
            google_books = self.search_books_google(query, limit)
            for book in google_books:
                book['source'] = 'google'
                all_books.append(book)
        
        # Remove duplicates based on ISBN
        unique_books = []
        seen_isbns = set()
        
        for book in all_books:
            isbn = book.get('isbn', '')
            if isbn and isbn in seen_isbns:
                continue
            if isbn:
                seen_isbns.add(isbn)
            unique_books.append(book)
        
        return unique_books
    
    def get_book_details(self, isbn, sources=None):
        """
        Get detailed book information by ISBN from multiple sources.
        
        Args:
            isbn (str): ISBN of the book.
            sources (list, optional): List of sources to check. Defaults to ['openlibrary', 'google'].
            
        Returns:
            dict: Combined book details.
        """
        if sources is None:
            sources = ['openlibrary', 'google']
        
        book_details = {}
        
        if 'openlibrary' in sources:
            openlibrary_details = self.get_book_details_openlibrary(isbn)
            if openlibrary_details:
                book_details.update(openlibrary_details)
                book_details['source'] = 'openlibrary'
        
        if 'google' in sources and (not book_details or book_details.get('description', '') == ''):
            google_details = self.get_book_details_google(isbn)
            if google_details:
                # If we already have some details, only update missing fields
                if book_details:
                    for key, value in google_details.items():
                        if key not in book_details or not book_details[key]:
                            book_details[key] = value
                    book_details['source'] = 'openlibrary,google'
                else:
                    book_details = google_details
                    book_details['source'] = 'google'
        
        return book_details if book_details else None
    
    def export_to_csv(self, books, output_file):
        """
        Export book data to CSV.
        
        Args:
            books (list): List of book dictionaries.
            output_file (str): Output file path.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            df = pd.DataFrame(books)
            df.to_csv(output_file, index=False, encoding='utf-8')
            logger.info(f"Exported {len(books)} books to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False
    
    def export_to_json(self, books, output_file):
        """
        Export book data to JSON.
        
        Args:
            books (list): List of book dictionaries.
            output_file (str): Output file path.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(books, f, ensure_ascii=False, indent=2)
            logger.info(f"Exported {len(books)} books to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return False
    
    def import_from_csv(self, input_file):
        """
        Import book data from CSV.
        
        Args:
            input_file (str): Input file path.
            
        Returns:
            list: List of book dictionaries.
        """
        try:
            df = pd.read_csv(input_file, encoding='utf-8')
            books = df.to_dict('records')
            logger.info(f"Imported {len(books)} books from {input_file}")
            return books
        except Exception as e:
            logger.error(f"Error importing from CSV: {e}")
            return []
    
    def import_from_json(self, input_file):
        """
        Import book data from JSON.
        
        Args:
            input_file (str): Input file path.
            
        Returns:
            list: List of book dictionaries.
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                books = json.load(f)
            logger.info(f"Imported {len(books)} books from {input_file}")
            return books
        except Exception as e:
            logger.error(f"Error importing from JSON: {e}")
            return []
