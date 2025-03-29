#!/usr/bin/env python3
import unittest
import os
import tempfile
import sqlite3
from unittest.mock import patch, MagicMock

from rbible.bible_data import (
    get_book_id, BIBLE_BOOKS, BOOK_BY_SHORT, BOOK_BY_ID,
    get_available_versions, load_bible_version
)

class TestBibleData(unittest.TestCase):
    def test_book_mappings(self):
        """Test that book mappings are correctly set up"""
        # Test BIBLE_BOOKS structure
        self.assertEqual(len(BIBLE_BOOKS), 66)  # 66 books in the Bible
        self.assertEqual(BIBLE_BOOKS["Génesis"]["id"], 1)
        self.assertEqual(BIBLE_BOOKS["Apocalipsis"]["id"], 66)
        
        # Test BOOK_BY_SHORT mapping
        self.assertEqual(BOOK_BY_SHORT["Gen"], "Génesis")
        self.assertEqual(BOOK_BY_SHORT["Apo"], "Apocalipsis")
        
        # Test BOOK_BY_ID mapping
        self.assertEqual(BOOK_BY_ID[1], "Génesis")
        self.assertEqual(BOOK_BY_ID[66], "Apocalipsis")
    
    def test_get_book_id(self):
        """Test getting book ID from name or short code"""
        # Test with full name
        self.assertEqual(get_book_id("Génesis"), 1)
        self.assertEqual(get_book_id("Apocalipsis"), 66)
        
        # Test with short code
        self.assertEqual(get_book_id("Gen"), 1)
        self.assertEqual(get_book_id("Apo"), 66)
        
        # Test case insensitivity
        self.assertEqual(get_book_id("génesis"), 1)
        self.assertEqual(get_book_id("GEN"), 1)
        
        # Test non-existent book
        self.assertIsNone(get_book_id("NonExistentBook"))
    
    @patch('os.path.exists')
    @patch('os.listdir')
    def test_get_available_versions(self, mock_listdir, mock_exists):
        """Test getting available Bible versions"""
        # Mock os.path.exists to return True for the first directory
        mock_exists.side_effect = lambda path: path.endswith('bibles')
        
        # Mock os.listdir to return some Bible files
        mock_listdir.return_value = ['RVR.mybible', 'LBLA.mybible', 'not_a_bible.txt']
        
        # Test getting available versions
        versions = get_available_versions()
        self.assertEqual(set(versions), {'RVR', 'LBLA'})
    
    @patch('sqlite3.connect')
    @patch('os.path.exists')
    def test_load_bible_version(self, mock_exists, mock_connect):
        """Test loading a Bible version"""
        # Mock os.path.exists to return True for a specific path
        mock_exists.side_effect = lambda path: 'RVR.mybible' in path
        
        # Mock sqlite3.connect to return a connection
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        # Test loading a Bible version
        conn = load_bible_version('RVR')
        self.assertEqual(conn, mock_conn)
        
        # Verify that sqlite3.connect was called with the correct path
        mock_connect.assert_called_once()
        self.assertTrue('RVR.mybible' in mock_connect.call_args[0][0])

if __name__ == '__main__':
    unittest.main()