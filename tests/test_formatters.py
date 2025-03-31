#!/usr/bin/env python3
import unittest

from rbible.formatters import format_as_markdown, format_parallel_verses

class TestFormatters(unittest.TestCase):
    def test_format_as_markdown(self):
        """Test formatting verse as markdown"""
        # Test with reference
        formatted = format_as_markdown("Juan 3:16", "For God so loved the world...")
        self.assertEqual(formatted, "> **Juan 3:16**\n>\n> For God so loved the world...")
        
        # Test with reference and version
        formatted = format_as_markdown("Juan 3:16", "For God so loved the world...", version="RVR")
        self.assertEqual(formatted, "> **Juan 3:16(RVR)**\n>\n> For God so loved the world...")
        
        # Test without reference
        formatted = format_as_markdown("Juan 3:16", "For God so loved the world...", include_reference=False)
        self.assertEqual(formatted, "> For God so loved the world...")
        
        # Test with multiline text
        formatted = format_as_markdown("Juan 3:16", "For God so loved the world...\nThat he gave his only Son...")
        self.assertEqual(formatted, "> **Juan 3:16**\n>\n> For God so loved the world...\n> That he gave his only Son...")
    
    def test_format_parallel_verses(self):
        """Test formatting parallel verses"""
        # Create some test data
        parallel_results = [
            {"version": "RVR", "reference": "Juan 3:16", "text": "For God so loved the world..."},
            {"version": "LBLA", "reference": "Juan 3:16", "text": "Porque de tal manera amó Dios al mundo..."}
        ]
        
        # Test normal formatting
        formatted = format_parallel_verses(parallel_results)
        self.assertTrue("Juan 3:16" in formatted)
        self.assertTrue("[RVR]" in formatted)
        self.assertTrue("[LBLA]" in formatted)
        
        # Test markdown formatting
        formatted = format_parallel_verses(parallel_results, markdown=True)
        self.assertTrue("> **Juan 3:16**" in formatted)
        self.assertTrue("> *RVR*:" in formatted)
        self.assertTrue("> *LBLA*:" in formatted)
        
        # Test with error
        parallel_results.append({"version": "NIV", "reference": "Juan 3:16", "error": "Version not found"})
        formatted = format_parallel_verses(parallel_results, markdown=True)
        self.assertTrue("> *NIV*: Error" in formatted)

if __name__ == '__main__':
    unittest.main()