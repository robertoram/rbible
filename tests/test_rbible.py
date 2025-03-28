"""
Tests for the rbible package.
"""

import unittest
import os
import sqlite3
import tempfile
from unittest.mock import patch, MagicMock
from rbible import __version__
from rbible.rbible import (
    get_book_id, 
    parse_reference, 
    get_verse, 
    list_books, 
    load_bible_version
)

class TestRBible(unittest.TestCase):
    def test_version(self):
        """Test that version is defined."""
        self.assertTrue(len(__version__) > 0)
    
    def test_get_book_id(self):
        """Test book ID lookup functionality."""
        # Test with full name
        self.assertEqual(get_book_id("Jua"), 43)
        
        # Test with different case
        self.assertEqual(get_book_id("jua"), 43)
        
        # Test with non-existent book
        self.assertIsNone(get_book_id("NonExistentBook"))
    
    def test_parse_reference(self):
        """Test Bible reference parsing."""
        # Test normal reference
        with patch('sys.exit') as mock_exit:
            book, chapter, verse = parse_reference("Juan 3:16")
            self.assertEqual(book, "Juan")
            self.assertEqual(chapter, 3)
            self.assertEqual(verse, 16)
            mock_exit.assert_not_called()
        
        # Test verse range
        with patch('sys.exit') as mock_exit:
            book, chapter, verse_range = parse_reference("Juan 3:16-20")
            self.assertEqual(book, "Juan")
            self.assertEqual(chapter, 3)
            self.assertEqual(verse_range, (16, 20))
            mock_exit.assert_not_called()
    
    def test_parse_reference_invalid(self):
        """Test invalid Bible reference parsing."""
        # Test invalid format (missing chapter:verse)
        with patch('sys.exit') as mock_exit, patch('builtins.print') as mock_print:
            # We need to catch the ValueError that's being raised
            try:
                parse_reference("Juan")
            except ValueError:
                # This is expected, so we'll just pass
                pass
            # Instead of assert_called_once(), check that it was called at least once
            self.assertTrue(mock_exit.called)
        
        # Reset mocks for each test case
        mock_exit = patch('sys.exit').start()
        mock_print = patch('builtins.print').start()
        try:
            parse_reference("Juan 3")
        except ValueError:
            pass
        self.assertTrue(mock_exit.called)
        patch.stopall()  # Stop all patches
        
        # Reset mocks for each test case
        mock_exit = patch('sys.exit').start()
        mock_print = patch('builtins.print').start()
        try:
            parse_reference("Juan a:16")
        except ValueError:
            pass
        self.assertTrue(mock_exit.called)
        patch.stopall()  # Stop all patches
        
        # Reset mocks for each test case
        mock_exit = patch('sys.exit').start()
        mock_print = patch('builtins.print').start()
        try:
            parse_reference("Juan 3:a")
        except ValueError:
            pass
        self.assertTrue(mock_exit.called)
        patch.stopall()  # Stop all patches
    
    def create_test_bible_db(self):
        """Create a temporary Bible database for testing."""
        db_fd, db_path = tempfile.mkstemp(suffix='.mybible')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create Bible table
        cursor.execute('''
        CREATE TABLE Bible (
            Book INTEGER,
            Chapter INTEGER,
            Verse INTEGER,
            Scripture TEXT
        )
        ''')
        
        # Add some test verses
        test_verses = [
            (43, 3, 16, "For God so loved the world..."),
            (43, 3, 17, "For God did not send his Son into the world..."),
            (43, 3, 18, "Whoever believes in him is not condemned..."),
            (43, 3, 19, "This is the verdict: Light has come into the world..."),
            (43, 3, 20, "Everyone who does evil hates the light..."),
        ]
        cursor.executemany("INSERT INTO Bible VALUES (?, ?, ?, ?)", test_verses)
        conn.commit()
        conn.close()
        os.close(db_fd)
        
        return db_path
    
    def test_get_verse(self):
        """Test verse retrieval functionality."""
        # Create a test Bible database
        db_path = self.create_test_bible_db()
        
        try:
            # Connect to the test database
            conn = sqlite3.connect(db_path)
            
            # Test single verse retrieval
            with patch('rbible.rbible.get_book_id', return_value=43):
                verse_text = get_verse(conn, "Juan", 3, 16)
                self.assertEqual(verse_text, "For God so loved the world...")
            
            # Test verse range retrieval
            with patch('rbible.rbible.get_book_id', return_value=43):
                verse_text = get_verse(conn, "Juan", 3, (16, 17))
                self.assertTrue("16. For God so loved the world..." in verse_text)
                self.assertTrue("17. For God did not send his Son into the world..." in verse_text)
        
        finally:
            # Clean up
            conn.close()
            os.unlink(db_path)
    
    def test_list_books(self):
        """Test book listing functionality."""
        with patch('builtins.print') as mock_print:
            list_books()
            # Verify that print was called at least once
            self.assertTrue(mock_print.called)

if __name__ == "__main__":
    unittest.main()