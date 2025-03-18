"""
Unit tests for data analysis module.
"""

import unittest
import os
import sys
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from utils.data_analysis import (
    clean_data, analyze_book_popularity, analyze_user_activity,
    predict_book_demand, analyze_borrowing_patterns, analyze_overdue_trends,
    analyze_category_distribution, analyze_user_preferences
)

class TestDataAnalysis(unittest.TestCase):
    """Test case for data analysis module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample book data
        self.book_data = pd.DataFrame({
            'book_id': [1, 2, 3, 4, 5],
            'title': ['Python Basics', 'Data Science', 'Machine Learning', 'Web Development', 'Database Design'],
            'author': ['John Smith', 'Jane Doe', 'Bob Johnson', 'Alice Brown', 'Charlie Davis'],
            'category': ['Programming', 'Data Science', 'Data Science', 'Programming', 'Database'],
            'publication_year': [2018, 2020, 2021, 2019, 2022],
            'quantity': [5, 3, 2, 4, 3],
            'available': [2, 1, 0, 3, 2]
        })
        
        # Sample transaction data
        self.transaction_data = pd.DataFrame({
            'transaction_id': [1, 2, 3, 4, 5, 6, 7, 8],
            'user_id': [1, 2, 1, 3, 2, 1, 3, 4],
            'book_id': [1, 2, 3, 4, 1, 2, 5, 3],
            'borrow_date': pd.to_datetime(['2023-01-01', '2023-01-05', '2023-01-10', 
                                          '2023-02-01', '2023-02-10', '2023-02-15',
                                          '2023-03-01', '2023-03-10']),
            'due_date': pd.to_datetime(['2023-01-15', '2023-01-19', '2023-01-24', 
                                       '2023-02-15', '2023-02-24', '2023-03-01',
                                       '2023-03-15', '2023-03-24']),
            'return_date': pd.to_datetime(['2023-01-14', '2023-01-20', '2023-01-23', 
                                          '2023-02-14', '2023-02-23', '2023-03-02',
                                          None, None]),
            'status': ['returned', 'overdue', 'returned', 'returned', 'returned', 'overdue', 'borrowed', 'borrowed']
        })
        
        # Sample user data
        self.user_data = pd.DataFrame({
            'user_id': [1, 2, 3, 4],
            'username': ['user1', 'user2', 'user3', 'user4'],
            'full_name': ['User One', 'User Two', 'User Three', 'User Four'],
            'role': ['admin', 'user', 'user', 'user'],
            'email': ['user1@example.com', 'user2@example.com', 'user3@example.com', 'user4@example.com']
        })
        
        # Sample data with missing values
        self.dirty_data = pd.DataFrame({
            'book_id': [1, 2, 3, 4, 5],
            'title': ['Python Basics', 'Data Science', None, 'Web Development', 'Database Design'],
            'author': ['John Smith', None, 'Bob Johnson', 'Alice Brown', 'Charlie Davis'],
            'category': ['Programming', 'Data Science', 'Data Science', None, 'Database'],
            'publication_year': [2018, 2020, None, 2019, 2022],
            'quantity': [5, 3, 2, 4, 3],
            'available': [2, 1, 0, 3, 2]
        })
    
    def test_clean_data(self):
        """Test data cleaning function."""
        # Clean the dirty data
        cleaned_data = clean_data(self.dirty_data)
        
        # Verify no missing values
        self.assertFalse(cleaned_data.isnull().any().any())
        
        # Verify correct imputation
        self.assertEqual(cleaned_data.loc[2, 'title'], 'Unknown Title')
        self.assertEqual(cleaned_data.loc[1, 'author'], 'Unknown Author')
        self.assertEqual(cleaned_data.loc[3, 'category'], 'Uncategorized')
        self.assertEqual(cleaned_data.loc[2, 'publication_year'], 2020)  # Median value
    
    def test_analyze_book_popularity(self):
        """Test book popularity analysis."""
        # Analyze book popularity
        popularity = analyze_book_popularity(self.transaction_data, self.book_data)
        
        # Verify results
        self.assertIsInstance(popularity, pd.DataFrame)
        self.assertIn('book_id', popularity.columns)
        self.assertIn('title', popularity.columns)
        self.assertIn('borrow_count', popularity.columns)
        
        # Verify correct counts
        book1_count = popularity[popularity['book_id'] == 1]['borrow_count'].values[0]
        book2_count = popularity[popularity['book_id'] == 2]['borrow_count'].values[0]
        book3_count = popularity[popularity['book_id'] == 3]['borrow_count'].values[0]
        
        self.assertEqual(book1_count, 2)
        self.assertEqual(book2_count, 2)
        self.assertEqual(book3_count, 2)
    
    def test_analyze_user_activity(self):
        """Test user activity analysis."""
        # Analyze user activity
        activity = analyze_user_activity(self.transaction_data, self.user_data)
        
        # Verify results
        self.assertIsInstance(activity, pd.DataFrame)
        self.assertIn('user_id', activity.columns)
        self.assertIn('username', activity.columns)
        self.assertIn('borrow_count', activity.columns)
        
        # Verify correct counts
        user1_count = activity[activity['user_id'] == 1]['borrow_count'].values[0]
        user2_count = activity[activity['user_id'] == 2]['borrow_count'].values[0]
        user3_count = activity[activity['user_id'] == 3]['borrow_count'].values[0]
        
        self.assertEqual(user1_count, 3)
        self.assertEqual(user2_count, 2)
        self.assertEqual(user3_count, 2)
    
    def test_predict_book_demand(self):
        """Test book demand prediction."""
        # Predict book demand
        predictions = predict_book_demand(self.transaction_data, self.book_data)
        
        # Verify results
        self.assertIsInstance(predictions, pd.DataFrame)
        self.assertIn('book_id', predictions.columns)
        self.assertIn('title', predictions.columns)
        self.assertIn('predicted_demand', predictions.columns)
        
        # Verify all books are included
        self.assertEqual(len(predictions), len(self.book_data))
        
        # Verify predictions are reasonable (between 0 and 10)
        self.assertTrue((predictions['predicted_demand'] >= 0).all())
        self.assertTrue((predictions['predicted_demand'] <= 10).all())
    
    def test_analyze_borrowing_patterns(self):
        """Test borrowing patterns analysis."""
        # Analyze borrowing patterns
        patterns = analyze_borrowing_patterns(self.transaction_data)
        
        # Verify results
        self.assertIsInstance(patterns, dict)
        self.assertIn('monthly_counts', patterns)
        self.assertIn('day_of_week_counts', patterns)
        
        # Verify monthly counts
        monthly_counts = patterns['monthly_counts']
        self.assertIsInstance(monthly_counts, pd.Series)
        self.assertEqual(len(monthly_counts), 3)  # 3 months in the data
        
        # Verify day of week counts
        day_counts = patterns['day_of_week_counts']
        self.assertIsInstance(day_counts, pd.Series)
        self.assertLessEqual(len(day_counts), 7)  # At most 7 days of the week
    
    def test_analyze_overdue_trends(self):
        """Test overdue trends analysis."""
        # Analyze overdue trends
        trends = analyze_overdue_trends(self.transaction_data, self.book_data)
        
        # Verify results
        self.assertIsInstance(trends, dict)
        self.assertIn('overdue_rate', trends)
        self.assertIn('avg_days_overdue', trends)
        self.assertIn('category_overdue_rates', trends)
        
        # Verify overdue rate
        self.assertIsInstance(trends['overdue_rate'], float)
        self.assertGreaterEqual(trends['overdue_rate'], 0.0)
        self.assertLessEqual(trends['overdue_rate'], 1.0)
        
        # Verify average days overdue
        self.assertIsInstance(trends['avg_days_overdue'], float)
        self.assertGreaterEqual(trends['avg_days_overdue'], 0.0)
        
        # Verify category overdue rates
        category_rates = trends['category_overdue_rates']
        self.assertIsInstance(category_rates, pd.Series)
    
    def test_analyze_category_distribution(self):
        """Test category distribution analysis."""
        # Analyze category distribution
        distribution = analyze_category_distribution(self.book_data)
        
        # Verify results
        self.assertIsInstance(distribution, pd.Series)
        
        # Verify correct counts
        programming_count = distribution.get('Programming', 0)
        data_science_count = distribution.get('Data Science', 0)
        database_count = distribution.get('Database', 0)
        
        self.assertEqual(programming_count, 2)
        self.assertEqual(data_science_count, 2)
        self.assertEqual(database_count, 1)
    
    def test_analyze_user_preferences(self):
        """Test user preferences analysis."""
        # Analyze user preferences
        preferences = analyze_user_preferences(self.transaction_data, self.book_data, self.user_data)
        
        # Verify results
        self.assertIsInstance(preferences, dict)
        self.assertIn('user_category_preferences', preferences)
        self.assertIn('user_author_preferences', preferences)
        
        # Verify user category preferences
        user_categories = preferences['user_category_preferences']
        self.assertIsInstance(user_categories, dict)
        
        # Verify user author preferences
        user_authors = preferences['user_author_preferences']
        self.assertIsInstance(user_authors, dict)
        
        # Verify user 1 preferences
        if 1 in user_categories:
            user1_categories = user_categories[1]
            self.assertIsInstance(user1_categories, pd.Series)

if __name__ == '__main__':
    unittest.main()
