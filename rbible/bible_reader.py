import sqlite3
import os

def get_verse(version, book, chapter, verse):
    """Get a verse from a specific Bible version."""
    bible_path = get_bible_path(version)
    
    try:
        conn = sqlite3.connect(bible_path)
        cursor = conn.cursor()
        
        # First try with books table
        cursor.execute("""
            SELECT book_number 
            FROM books 
            WHERE short_name LIKE ? OR long_name LIKE ?
        """, (f"%{book}%", f"%{book}%"))
        
        book_result = cursor.fetchone()
        if not book_result:
            raise ValueError(f"Book '{book}' not found")
        
        book_number = book_result[0]
        
        # Then try with verses table
        cursor.execute("""
            SELECT text 
            FROM verses 
            WHERE book_number = ? AND chapter = ? AND verse = ?
        """, (book_number, chapter, verse))
        
        verse_result = cursor.fetchone()
        if not verse_result:
            raise ValueError(f"Verse not found: {book} {chapter}:{verse}")
        
        return verse_result[0]
        
    except sqlite3.Error as e:
        # If first attempt fails, try alternative table names
        try:
            cursor.execute("""
                SELECT text 
                FROM Bible 
                WHERE book = ? AND chapter = ? AND verse = ?
            """, (book, chapter, verse))
            
            verse_result = cursor.fetchone()
            if verse_result:
                return verse_result[0]
            
        except sqlite3.Error:
            pass
        
        raise Exception(f"Error retrieving verse: {e}")
    finally:
        if conn:
            conn.close()