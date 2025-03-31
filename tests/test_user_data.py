#!/usr/bin/env python3
import unittest
import os
import json
import tempfile
from unittest.mock import patch, mock_open

from rbible.user_data import (
    save_to_history, load_history, show_history,
    save_to_favorites, load_favorites, show_favorites, remove_favorite
)

class TestUserData(unittest.TestCase):
    @patch('os.makedirs')
    @patch('json.dump')
    @patch('builtins.open', new_callable=mock_open)
    @patch('rbible.user_data.load_history')
    @patch('rbible.user_data.import_time_module')
    def test_save_to_history(self, mock_time, mock_load_history, mock_file, mock_json_dump, mock_makedirs):
        """Test saving verse to history"""
        # Mock time.time() to return a fixed timestamp
        mock_time_module = unittest.mock.MagicMock()
        mock_time_module.time.return_value = 1234567890
        mock_time.return_value = mock_time_module
        
        # Mock load_history to return an empty list
        mock_load_history.return_value = []
        
        # Test saving to history
        save_to_history("Juan 3:16", "For God so loved the world...", "RVR")
        
        # Verify that makedirs was called
        mock_makedirs.assert_called_once()
        
        # Verify that open was called with the correct file path
        mock_file.assert_called_once()
        
        # Verify that json.dump was called with the correct data
        args, _ = mock_json_dump.call_args
        data = args[0]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["reference"], "Juan 3:16")
        self.assertEqual(data[0]["text"], "For God so loved the world...")
        self.assertEqual(data[0]["version"], "RVR")
        self.assertEqual(data[0]["timestamp"], 1234567890)
    
    @patch('os.path.exists')
    @patch('json.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_history(self, mock_file, mock_json_load, mock_exists):
        """Test loading verse history"""
        # Mock os.path.exists to return True
        mock_exists.return_value = True
        
        # Mock json.load to return some history data
        history_data = [
            {"reference": "Juan 3:16", "text": "For God so loved...", "version": "RVR", "timestamp": 1234567890}
        ]
        mock_json_load.return_value = history_data
        
        # Test loading history
        history = load_history()
        
        # Verify that the correct data was returned
        self.assertEqual(history, history_data)
    
    @patch('rbible.user_data.load_favorites')
    @patch('json.dump')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('rbible.user_data.import_time_module')
    def test_save_to_favorites(self, mock_time, mock_makedirs, mock_file, mock_json_dump, mock_load_favorites):
        """Test saving verse to favorites"""
        # Mock time.time() to return a fixed timestamp
        mock_time_module = unittest.mock.MagicMock()
        mock_time_module.time.return_value = 1234567890
        mock_time.return_value = mock_time_module
        
        # Mock load_favorites to return an empty list
        mock_load_favorites.return_value = []
        
        # Test saving to favorites
        save_to_favorites("Juan 3:16", "For God so loved the world...", "RVR", "God's Love")
        
        # Verify that makedirs was called
        mock_makedirs.assert_called_once()
        
        # Verify that open was called with the correct file path
        mock_file.assert_called_once()
        
        # Verify that json.dump was called with the correct data
        args, _ = mock_json_dump.call_args
        data = args[0]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["reference"], "Juan 3:16")
        self.assertEqual(data[0]["text"], "For God so loved the world...")
        self.assertEqual(data[0]["version"], "RVR")
        self.assertEqual(data[0]["name"], "God's Love")
        self.assertEqual(data[0]["added"], 1234567890)
    
    @patch('rbible.user_data.load_favorites')
    def test_show_favorites(self, mock_load_favorites):
        """Test showing favorites"""
        # Mock load_favorites to return some favorites
        favorites = [
            {"reference": "Juan 3:16", "text": "For God so loved...", "version": "RVR", "name": "God's Love"},
            {"reference": "Salmos 23:1", "text": "The LORD is my shepherd...", "version": "LBLA", "name": "Comfort"}
        ]
        mock_load_favorites.return_value = favorites
        
        # Test showing all favorites
        with patch('builtins.print') as mock_print:
            show_favorites()
            # Verify that print was called with the correct information
            mock_print.assert_any_call("Favorite verses (2):")
        
        # Test getting a specific favorite
        favorite = show_favorites("1")
        self.assertEqual(favorite, favorites[0])
        
        # Test invalid index
        with patch('builtins.print') as mock_print:
            favorite = show_favorites("3")
            self.assertIsNone(favorite)
            mock_print.assert_called_with("Error: Favorite index 3 out of range (1-2).")

if __name__ == '__main__':
    unittest.main()