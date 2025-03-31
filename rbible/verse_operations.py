#!/usr/bin/env python3
import sys
import sqlite3
from rbible.bible_data import get_book_id, BOOK_BY_ID

def parse_reference(reference):
    """Parse a Bible reference like 'Juan 3:16' or 'Juan 3:16-20' into book, chapter, verse(s)."""
    parts = reference.split()
    if len(parts) < 2:
        print(f"Error: Invalid reference format. Use 'Book Chapter:Verse' or 'Book Chapter:Verse-Verse' format.")
        sys.exit(1)
    
    book = ' '.join(parts[:-1])
    chapter_verse = parts[-1]
    
    if ':' not in chapter_verse:
        print(f"Error: Invalid chapter:verse format. Use 'Book Chapter:Verse' format.")
        sys.exit(1)
    
    chapter, verse_range = chapter_verse.split(':')
    
    try:
        chapter = int(chapter)
        
        # Check if it's a verse range (e.g., 3:16-20)
        if '-' in verse_range:
            start_verse, end_verse = verse_range.split('-')
            start_verse = int(start_verse)
            end_verse = int(end_verse)
            return book, chapter, (start_verse, end_verse)
        else:
            verse = int(verse_range)
            return book, chapter, verse
    except ValueError:
        print(f"Error: Chapter and verse must be numbers.")
        sys.exit(1)

def get_verse(bible_conn, book, chapter, verse):
    """Get the specified verse or verse range from the Bible database."""
    try:
        # Get book ID
        book_id = get_book_id(book)
        if book_id is None:
            print(f"Error: Book '{book}' not found.")
            from bible_data import list_books
            list_books()
            sys.exit(1)
        
        cursor = bible_conn.cursor()
        
        # Check if chapter exists
        cursor.execute("SELECT DISTINCT Chapter FROM Bible WHERE Book = ? ORDER BY Chapter", (book_id,))
        chapters = [row[0] for row in cursor.fetchall()]
        
        if not chapters:
            print(f"Error: No chapters found for book '{book}'.")
            sys.exit(1)
        
        if chapter not in chapters:
            print(f"Error: Chapter {chapter} not found in {book}.")
            print(f"Available chapters: {', '.join(map(str, chapters))}")
            sys.exit(1)
        
        # Handle verse range
        if isinstance(verse, tuple):
            start_verse, end_verse = verse
            cursor.execute(
                "SELECT Verse, Scripture FROM Bible WHERE Book = ? AND Chapter = ? AND Verse >= ? AND Verse <= ? ORDER BY Verse",
                (book_id, chapter, start_verse, end_verse)
            )
            verses = cursor.fetchall()
            
            if not verses:
                print(f"Error: No verses found in range {start_verse}-{end_verse} in {book} {chapter}.")
                sys.exit(1)
            
            result = []
            for row in verses:
                # Fix: Remove the newline after the verse number
                result.append(f"{row[0]}. {row[1].strip()}")
            
            return "\n".join(result)
        else:
            # Handle single verse
            cursor.execute(
                "SELECT Scripture FROM Bible WHERE Book = ? AND Chapter = ? AND Verse = ?",
                (book_id, chapter, verse)
            )
            row = cursor.fetchone()
            
            if not row:
                # Get available verses to show in error message
                cursor.execute(
                    "SELECT MAX(Verse) FROM Bible WHERE Book = ? AND Chapter = ?",
                    (book_id, chapter)
                )
                max_verse = cursor.fetchone()[0]
                
                print(f"Error: Verse {verse} not found in {book} {chapter}.")
                print(f"Available verses: 1-{max_verse}")
                sys.exit(1)
            
            # Fix: Strip any leading/trailing whitespace
            return row[0].strip()
    except Exception as e:
        print(f"Error retrieving verse: {e}")
        sys.exit(1)
    finally:
        if 'cursor' in locals():
            cursor.close()

def search_bible(bible_conn, query, limit=20):
    """Search the Bible for verses containing the query text."""
    try:
        cursor = bible_conn.cursor()
        
        # Use SQLite FTS if available, otherwise fall back to LIKE
        try:
            # Try using FTS (Full Text Search)
            cursor.execute(
                "SELECT Book, Chapter, Verse, Scripture FROM Bible WHERE Scripture MATCH ? LIMIT ?",
                (query, limit)
            )
        except sqlite3.OperationalError:
            # Fall back to LIKE search
            cursor.execute(
                "SELECT Book, Chapter, Verse, Scripture FROM Bible WHERE Scripture LIKE ? LIMIT ?",
                (f"%{query}%", limit)
            )
        
        results = cursor.fetchall()
        
        if not results:
            print(f"No verses found containing '{query}'.")
            return []
        
        formatted_results = []
        for row in results:
            book_id, chapter, verse, text = row
            book_name = BOOK_BY_ID.get(book_id, f"Book {book_id}")
            reference = f"{book_name} {chapter}:{verse}"
            
            # Highlight the search term in the text
            highlighted_text = text.replace(query, f"\033[1m{query}\033[0m")
            
            formatted_results.append({
                "reference": reference,
                "text": text.strip(),
                "highlighted": highlighted_text.strip()
            })
        
        return formatted_results
    
    except Exception as e:
        print(f"Error searching Bible: {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()

def get_parallel_verses(verse_ref, versions):
    """Get the same verse in multiple translations."""
    # Fix the imports to use the rbible package prefix
    from rbible.bible_data import load_bible_version
    from rbible.user_data import save_to_history
    
    results = []
    
    try:
        book, chapter, verse = parse_reference(verse_ref)
        
        for version in versions:
            try:
                bible_conn = load_bible_version(version)
                verse_text = get_verse(bible_conn, book, chapter, verse)
                
                # Format the reference string
                if isinstance(verse, tuple):
                    start_verse, end_verse = verse
                    verse_str = f"{start_verse}-{end_verse}"
                else:
                    verse_str = str(verse)
                
                ref_str = f"{book} {chapter}:{verse_str}"
                
                results.append({
                    "version": version,
                    "reference": ref_str,
                    "text": verse_text
                })
                
                # Save to history
                save_to_history(ref_str, verse_text, version)
                
            except Exception as e:
                results.append({
                    "version": version,
                    "reference": verse_ref,
                    "error": str(e)
                })
            finally:
                if 'bible_conn' in locals():
                    bible_conn.close()
    
    except Exception as e:
        print(f"Error parsing reference: {e}")
    
    return results

def complete_reference(partial_ref):
    """Provide tab completion suggestions for Bible references."""
    from rbible.bible_data import BIBLE_BOOKS, BOOK_BY_SHORT, get_book_id
    
    suggestions = []
    
    # If empty, suggest some common books
    if not partial_ref:
        return ["Génesis", "Salmos", "Proverbios", "Mateo", "Juan", "Romanos"]
    
    # Split into parts
    parts = partial_ref.split()
    
    # If only one part, it's likely a book name
    if len(parts) == 1:
        book_part = parts[0].lower()
        
        # Suggest books that start with the given prefix
        for book_name in BIBLE_BOOKS.keys():
            if book_name.lower().startswith(book_part):
                suggestions.append(book_name)
        
        # Also check short codes
        for short_code, book_name in BOOK_BY_SHORT.items():
            if short_code.lower().startswith(book_part):
                suggestions.append(book_name)
    
    # If we have a book and possibly chapter
    elif len(parts) == 2 and ':' not in parts[1]:
        book = ' '.join(parts[:-1])
        chapter_prefix = parts[-1]
        
        # Get book ID
        book_id = get_book_id(book)
        if book_id is not None:
            # This would require database access to get available chapters
            # For simplicity, suggest some common chapter numbers
            for i in range(1, 11):
                if str(i).startswith(chapter_prefix):
                    suggestions.append(f"{book} {i}:1")
    
    # If we have book, chapter, and possibly verse
    elif len(parts) >= 2 and ':' in parts[-1]:
        book = ' '.join(parts[:-1])
        chapter_verse = parts[-1]
        
        if ':' in chapter_verse:
            chapter, verse_prefix = chapter_verse.split(':')
            
            # For simplicity, suggest some verse numbers
            for i in range(1, 31):
                if str(i).startswith(verse_prefix):
                    suggestions.append(f"{book} {chapter}:{i}")
    
    return suggestions

def format_as_markdown(reference, text, version=None):
    """Format verse text as markdown with proper quote formatting."""
    # Create the header with reference and version
    if version:
        header = f"> **{reference}({version})**"
    else:
        header = f"> **{reference}**"
    
    # Format the text with proper markdown quote formatting
    # Split the text into lines and add > to each line
    lines = text.split('\n')
    formatted_lines = []
    
    # Add the header
    formatted_lines.append(header)
    formatted_lines.append(">")  # Empty line after header
    
    # Add each line of the verse text with > prefix
    for line in lines:
        formatted_lines.append(f"> {line}")
    
    # Join all lines with newlines
    return '\n'.join(formatted_lines)

def format_parallel_verses(results, use_markdown=False):
    """Format parallel verses for display."""
    if not results:
        return "No verses found."
    
    output_lines = []
    
    for result in results:
        version = result.get("version", "Unknown")
        reference = result.get("reference", "Unknown")
        
        if "error" in result:
            output_lines.append(f"## {version}")
            output_lines.append(f"Error: {result['error']}")
        else:
            if use_markdown:
                # For markdown, format with proper headers and quote formatting
                output_lines.append(f"## {version}")
                output_lines.append(f"> **{reference}({version})**")
                output_lines.append(">")  # Empty line
                
                # Add each line of text with > prefix
                for line in result["text"].split('\n'):
                    output_lines.append(f"> {line}")
            else:
                output_lines.append(f"{reference} ({version})")
                output_lines.append(result["text"])
        
        output_lines.append("")  # Empty line between versions
    
    return '\n'.join(output_lines)