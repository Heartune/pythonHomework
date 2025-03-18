"""
Scheduler module for the Library Management System web scraping.
"""

import threading
import time
import schedule
import json
import os
import logging
from datetime import datetime
from .book_scraper import BookScraper
from ..logger import get_logger

logger = get_logger(__name__)

class ScraperScheduler:
    """Class for scheduling web scraping tasks."""
    
    def __init__(self, data_dir=None):
        """
        Initialize the scraper scheduler.
        
        Args:
            data_dir (str, optional): Directory to store scraped data.
        """
        # Set up data directory
        if data_dir:
            self.data_dir = data_dir
        else:
            self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'scraped')
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize book scraper
        self.book_scraper = BookScraper()
        
        # Initialize scheduler thread
        self.scheduler_thread = None
        self.is_running = False
        
        # Initialize tasks list
        self.tasks = []
        
        # Load existing tasks
        self._load_tasks()
    
    def _load_tasks(self):
        """Load existing tasks from file."""
        tasks_file = os.path.join(self.data_dir, 'scheduled_tasks.json')
        if os.path.exists(tasks_file):
            try:
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
                logger.info(f"Loaded {len(self.tasks)} scheduled tasks")
            except Exception as e:
                logger.error(f"Error loading scheduled tasks: {e}")
                self.tasks = []
    
    def _save_tasks(self):
        """Save tasks to file."""
        tasks_file = os.path.join(self.data_dir, 'scheduled_tasks.json')
        try:
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(self.tasks)} scheduled tasks")
        except Exception as e:
            logger.error(f"Error saving scheduled tasks: {e}")
    
    def _run_scheduler(self):
        """Run the scheduler in a separate thread."""
        logger.info("Starting scheduler thread")
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)
        logger.info("Scheduler thread stopped")
    
    def start(self):
        """Start the scheduler."""
        if not self.is_running:
            self.is_running = True
            
            # Clear existing schedule
            schedule.clear()
            
            # Add tasks to schedule
            for task in self.tasks:
                self._schedule_task(task)
            
            # Start scheduler thread
            self.scheduler_thread = threading.Thread(target=self._run_scheduler)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
            
            logger.info("Scheduler started")
            return True
        else:
            logger.warning("Scheduler is already running")
            return False
    
    def stop(self):
        """Stop the scheduler."""
        if self.is_running:
            self.is_running = False
            
            # Wait for scheduler thread to stop
            if self.scheduler_thread:
                self.scheduler_thread.join(timeout=5)
            
            # Clear schedule
            schedule.clear()
            
            logger.info("Scheduler stopped")
            return True
        else:
            logger.warning("Scheduler is not running")
            return False
    
    def _schedule_task(self, task):
        """
        Schedule a task.
        
        Args:
            task (dict): Task configuration.
        """
        task_id = task.get('id')
        task_type = task.get('type')
        schedule_type = task.get('schedule_type')
        schedule_value = task.get('schedule_value')
        
        if not all([task_id, task_type, schedule_type, schedule_value]):
            logger.error(f"Invalid task configuration: {task}")
            return False
        
        # Create job function
        job_func = lambda: self._execute_task(task)
        
        # Schedule job based on schedule type
        job = None
        if schedule_type == 'interval':
            # Schedule at regular intervals (in minutes)
            minutes = int(schedule_value)
            job = schedule.every(minutes).minutes.do(job_func)
        elif schedule_type == 'daily':
            # Schedule daily at specific time
            job = schedule.every().day.at(schedule_value).do(job_func)
        elif schedule_type == 'weekly':
            # Schedule weekly on specific day at specific time
            day, time = schedule_value.split(' ')
            job = getattr(schedule.every(), day.lower()).at(time).do(job_func)
        
        if job:
            logger.info(f"Scheduled task {task_id}: {task_type} ({schedule_type}: {schedule_value})")
            return True
        else:
            logger.error(f"Failed to schedule task {task_id}")
            return False
    
    def _execute_task(self, task):
        """
        Execute a scheduled task.
        
        Args:
            task (dict): Task configuration.
        """
        task_id = task.get('id')
        task_type = task.get('type')
        params = task.get('params', {})
        
        logger.info(f"Executing task {task_id}: {task_type}")
        
        try:
            # Execute task based on type
            if task_type == 'search_books':
                query = params.get('query')
                limit = params.get('limit', 10)
                sources = params.get('sources', ['openlibrary', 'google'])
                
                if not query:
                    logger.error(f"Missing query parameter for task {task_id}")
                    return False
                
                # Search books
                books = self.book_scraper.search_books(query, limit, sources)
                
                # Save results
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = os.path.join(self.data_dir, f"search_{query.replace(' ', '_')}_{timestamp}.json")
                self.book_scraper.export_to_json(books, output_file)
                
                # Update task last run time
                task['last_run'] = datetime.now().isoformat()
                self._save_tasks()
                
                return True
            
            elif task_type == 'get_book_details':
                isbn = params.get('isbn')
                sources = params.get('sources', ['openlibrary', 'google'])
                
                if not isbn:
                    logger.error(f"Missing ISBN parameter for task {task_id}")
                    return False
                
                # Get book details
                book_details = self.book_scraper.get_book_details(isbn, sources)
                
                if book_details:
                    # Save results
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    output_file = os.path.join(self.data_dir, f"book_{isbn}_{timestamp}.json")
                    self.book_scraper.export_to_json([book_details], output_file)
                    
                    # Update task last run time
                    task['last_run'] = datetime.now().isoformat()
                    self._save_tasks()
                    
                    return True
                else:
                    logger.warning(f"No book details found for ISBN {isbn}")
                    return False
            
            elif task_type == 'import_to_database':
                file_path = params.get('file_path')
                file_type = params.get('file_type', 'json')
                
                if not file_path or not os.path.exists(file_path):
                    logger.error(f"Invalid file path for task {task_id}: {file_path}")
                    return False
                
                # Import data
                if file_type.lower() == 'json':
                    books = self.book_scraper.import_from_json(file_path)
                elif file_type.lower() == 'csv':
                    books = self.book_scraper.import_from_csv(file_path)
                else:
                    logger.error(f"Unsupported file type for task {task_id}: {file_type}")
                    return False
                
                # TODO: Import books to database
                # This would require integration with the database module
                
                # Update task last run time
                task['last_run'] = datetime.now().isoformat()
                self._save_tasks()
                
                return True
            
            else:
                logger.error(f"Unsupported task type for task {task_id}: {task_type}")
                return False
        
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {e}")
            return False
    
    def add_task(self, task_type, schedule_type, schedule_value, params=None):
        """
        Add a new scheduled task.
        
        Args:
            task_type (str): Type of task ('search_books', 'get_book_details', 'import_to_database').
            schedule_type (str): Type of schedule ('interval', 'daily', 'weekly').
            schedule_value (str): Value for the schedule type.
            params (dict, optional): Parameters for the task.
            
        Returns:
            str: Task ID if successful, None otherwise.
        """
        try:
            # Validate task type
            if task_type not in ['search_books', 'get_book_details', 'import_to_database']:
                logger.error(f"Unsupported task type: {task_type}")
                return None
            
            # Validate schedule type
            if schedule_type not in ['interval', 'daily', 'weekly']:
                logger.error(f"Unsupported schedule type: {schedule_type}")
                return None
            
            # Validate schedule value
            if schedule_type == 'interval':
                try:
                    minutes = int(schedule_value)
                    if minutes < 1:
                        raise ValueError("Interval must be at least 1 minute")
                except ValueError:
                    logger.error(f"Invalid interval value: {schedule_value}")
                    return None
            elif schedule_type == 'daily':
                # Validate time format (HH:MM)
                if not self._validate_time_format(schedule_value):
                    logger.error(f"Invalid time format for daily schedule: {schedule_value}")
                    return None
            elif schedule_type == 'weekly':
                # Validate day and time format (DAY HH:MM)
                parts = schedule_value.split(' ')
                if len(parts) != 2 or parts[0].lower() not in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'] or not self._validate_time_format(parts[1]):
                    logger.error(f"Invalid day and time format for weekly schedule: {schedule_value}")
                    return None
            
            # Generate task ID
            task_id = f"{task_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Create task
            task = {
                'id': task_id,
                'type': task_type,
                'schedule_type': schedule_type,
                'schedule_value': schedule_value,
                'params': params or {},
                'created': datetime.now().isoformat(),
                'last_run': None
            }
            
            # Add task to list
            self.tasks.append(task)
            
            # Save tasks
            self._save_tasks()
            
            # Schedule task if scheduler is running
            if self.is_running:
                self._schedule_task(task)
            
            logger.info(f"Added task {task_id}: {task_type} ({schedule_type}: {schedule_value})")
            return task_id
        
        except Exception as e:
            logger.error(f"Error adding task: {e}")
            return None
    
    def remove_task(self, task_id):
        """
        Remove a scheduled task.
        
        Args:
            task_id (str): ID of the task to remove.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Find task
            task_index = None
            for i, task in enumerate(self.tasks):
                if task.get('id') == task_id:
                    task_index = i
                    break
            
            if task_index is None:
                logger.error(f"Task not found: {task_id}")
                return False
            
            # Remove task from list
            self.tasks.pop(task_index)
            
            # Save tasks
            self._save_tasks()
            
            # Clear and reschedule tasks if scheduler is running
            if self.is_running:
                schedule.clear()
                for task in self.tasks:
                    self._schedule_task(task)
            
            logger.info(f"Removed task {task_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error removing task: {e}")
            return False
    
    def get_tasks(self):
        """
        Get all scheduled tasks.
        
        Returns:
            list: List of task dictionaries.
        """
        return self.tasks
    
    def get_task(self, task_id):
        """
        Get a specific scheduled task.
        
        Args:
            task_id (str): ID of the task to get.
            
        Returns:
            dict: Task dictionary if found, None otherwise.
        """
        for task in self.tasks:
            if task.get('id') == task_id:
                return task
        return None
    
    def run_task_now(self, task_id):
        """
        Run a scheduled task immediately.
        
        Args:
            task_id (str): ID of the task to run.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        task = self.get_task(task_id)
        if task:
            return self._execute_task(task)
        else:
            logger.error(f"Task not found: {task_id}")
            return False
    
    def _validate_time_format(self, time_str):
        """
        Validate time format (HH:MM).
        
        Args:
            time_str (str): Time string to validate.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        try:
            hours, minutes = time_str.split(':')
            hours = int(hours)
            minutes = int(minutes)
            return 0 <= hours < 24 and 0 <= minutes < 60
        except:
            return False
