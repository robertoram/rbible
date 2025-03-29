#!/usr/bin/env python3
import unittest
from unittest.mock import patch, MagicMock
import sys

from rbible.verse_operations import (
    parse_reference, get_verse, search_bible, complete_reference
)

class TestVerseOperations(unittest.TestCase):
    def test_parse_reference(self):
        """Test parsing Bible references"""
        # Test simple reference
        book, chapter, verse = parse_reference("Juan 3:16")
        self.assertEqual(book, "Juan")
        self.assertEqual(chapter, 3)
        self.assertEqual(verse, 16)
        
        # Test reference with multi-word book
        book, chapter, verse = parse_reference("1 Corintios 13:4")
        self.assertEqual(book, "1 Corintios")
        self.assertEqual(chapter, 13)
        self.assertEqual(verse, 4)
        
        # Test verse range
        book, chapter, verse = parse_reference("Salmos 23:1-6")
        self.assertEqual(book, "Salmos")
        self.assertEqual(chapter, 23)
        self.assertEqual(verse, (1, 6))
        
        # Test invalid references
        with self.assertRaises(SystemExit):
            parse_reference("Invalid")
        
        with self.assertRaises(SystemExit):
            parse_reference("Juan 3")
        
        with self.assertRaises(SystemExit):
            parse_reference("Juan 3:abc")
    
    @patch('rbible.verse_operations.get_book_id')
    def test_get_verse(self, mock_get_book_id):
        """Test getting verses from the Bible"""
        # Mock get_book_id to return a valid ID
        mock_get_book_id.return_value = 43  # Juan
        
        # Create a mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Test getting a single verse
        mock_cursor.fetchall.return_value = [(3,)]  # Available chapters
        mock_cursor.fetchone.return_value = ("For God so loved the world...",)
        
        verse_text = get_verse(mock_conn, "Juan", 3, 16)
        self.assertEqual(verse_text, "For God so loved the world...")
        
        # Test getting a verse range
        mock_cursor.fetchall.side_effect = [
            [(23,)],  # Available chapters
            [
                (1, "The LORD is my shepherd..."),
                (2, "He makes me lie down..."),
            ]
        ]
        
        verse_text = get_verse(mock_conn, "Salmos", 23, (1, 2))
        self.assertEqual(verse_text, "1. The LORD is my shepherd...\n2. He makes me lie down...")
    
    @patch('rbible.verse_operations.BOOK_BY_ID')
    def test_search_bible(self, mock_book_by_id):
        """Test searching the Bible"""
        # Mock BOOK_BY_ID
        mock_book_by_id.get.return_value = "Juan"
        
        # Create a mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock cursor.fetchall to return search results
        mock_cursor.fetchall.return_value = [
            (43, 3, 16, "For God so loved the world..."),
            (43, 3, 17, "For God did not send his Son into the world...")
        ]
        
        # Test searching
        results = search_bible(mock_conn, "God")
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["reference"], "Juan 3:16")
        self.assertEqual(results[0]["text"], "For God so loved the world...")
    
    @patch('rbible.verse_operations.get_book_id')
    def test_complete_reference(self, mock_get_book_id):
        """Test reference completion suggestions"""
        # Mock get_book_id to return a valid ID
        mock_get_book_id.return_value = 43  # Juan
        
        # Test empty input
        suggestions = complete_reference("")
        self.assertEqual(len(suggestions), 6)  # Should return 6 common books
        
        # Test book name prefix
        suggestions = complete_reference("Ju")
        self.assertTrue(all(book.startswith("Ju") for book in suggestions))
        
        # Test chapter suggestions
        suggestions = complete_reference("Juan 3")
        self.assertTrue(all("Juan 3:" in suggestion for suggestion in suggestions))
        
        # Test verse suggestions
        suggestions = complete_reference("Juan 3:1")
        self.assertTrue(all("Juan 3:1" in suggestion for suggestion in suggestions))

if __name__ == '__main__':
    unittest.main()