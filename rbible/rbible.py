#!/usr/bin/env python3
import argparse
import json
import os
import sys
import sqlite3
import urllib.request
import shutil
import pyperclip  # Add this import

# GitHub repository information
GITHUB_REPO_OWNER = "robertoram"
GITHUB_REPO_NAME = "rbible"

# Book mapping for Spanish Bible books with short names
BIBLE_BOOKS = {
    # Old Testament
    "Génesis": {"short": "Gen", "id": 1},
    "Éxodo": {"short": "Exod", "id": 2},
    "Levítico": {"short": "Lev", "id": 3},
    "Números": {"short": "Num", "id": 4},
    "Deuteronomio": {"short": "Deut", "id": 5},
    "Josué": {"short": "Jos", "id": 6},
    "Jueces": {"short": "Jue", "id": 7},
    "Rut": {"short": "Rut", "id": 8},
    "1 Samuel": {"short": "1Sa", "id": 9},
    "2 Samuel": {"short": "2Sa", "id": 10},
    "1 Reyes": {"short": "1Re", "id": 11},
    "2 Reyes": {"short": "2Re", "id": 12},
    "1 Crónicas": {"short": "1Cr", "id": 13},
    "2 Crónicas": {"short": "2Cr", "id": 14},
    "Esdras": {"short": "Esd", "id": 15},
    "Nehemías": {"short": "Neh", "id": 16},
    "Ester": {"short": "Est", "id": 17},
    "Job": {"short": "Job", "id": 18},
    "Salmos": {"short": "Sal", "id": 19},
    "Proverbios": {"short": "Pro", "id": 20},
    "Eclesiastés": {"short": "Ecl", "id": 21},
    "Cantares": {"short": "Can", "id": 22},
    "Isaías": {"short": "Isa", "id": 23},
    "Jeremías": {"short": "Jer", "id": 24},
    "Lamentaciones": {"short": "Lam", "id": 25},
    "Ezequiel": {"short": "Eze", "id": 26},
    "Daniel": {"short": "Dan", "id": 27},
    "Oseas": {"short": "Ose", "id": 28},
    "Joel": {"short": "Joe", "id": 29},
    "Amós": {"short": "Amo", "id": 30},
    "Abdías": {"short": "Abd", "id": 31},
    "Jonás": {"short": "Jon", "id": 32},
    "Miqueas": {"short": "Miq", "id": 33},
    "Nahúm": {"short": "Nah", "id": 34},
    "Habacuc": {"short": "Hab", "id": 35},
    "Sofonías": {"short": "Sof", "id": 36},
    "Hageo": {"short": "Hag", "id": 37},
    "Zacarías": {"short": "Zac", "id": 38},
    "Malaquías": {"short": "Mal", "id": 39},
    # New Testament
    "Mateo": {"short": "Mat", "id": 40},
    "Marcos": {"short": "Mar", "id": 41},
    "Lucas": {"short": "Luc", "id": 42},
    "Juan": {"short": "Jua", "id": 43},
    "Hechos": {"short": "Hec", "id": 44},
    "Romanos": {"short": "Rom", "id": 45},
    "1 Corintios": {"short": "1Co", "id": 46},
    "2 Corintios": {"short": "2Co", "id": 47},
    "Gálatas": {"short": "Gal", "id": 48},
    "Efesios": {"short": "Efe", "id": 49},
    "Filipenses": {"short": "Fil", "id": 50},
    "Colosenses": {"short": "Col", "id": 51},
    "1 Tesalonicenses": {"short": "1Te", "id": 52},
    "2 Tesalonicenses": {"short": "2Te", "id": 53},
    "1 Timoteo": {"short": "1Ti", "id": 54},
    "2 Timoteo": {"short": "2Ti", "id": 55},
    "Tito": {"short": "Tit", "id": 56},
    "Filemón": {"short": "Flm", "id": 57},
    "Hebreos": {"short": "Heb", "id": 58},
    "Santiago": {"short": "San", "id": 59},
    "1 Pedro": {"short": "1Pe", "id": 60},
    "2 Pedro": {"short": "2Pe", "id": 61},
    "1 Juan": {"short": "1Ju", "id": 62},
    "2 Juan": {"short": "2Ju", "id": 63},
    "3 Juan": {"short": "3Ju", "id": 64},
    "Judas": {"short": "Jud", "id": 65},
    "Apocalipsis": {"short": "Apo", "id": 66}
}

# Create reverse mappings for lookup by short name and book ID
BOOK_BY_SHORT = {book_data["short"]: book_name for book_name, book_data in BIBLE_BOOKS.items()}
BOOK_BY_ID = {book_data["id"]: book_name for book_name, book_data in BIBLE_BOOKS.items()}

def load_bible_version(version):
    """Load the specified Bible version from SQLite file."""
    possible_paths = [
        # First check the current directory
        os.path.join(os.getcwd(), "bibles", f"{version}.mybible"),
        # Then check the script directory
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "bibles", f"{version}.mybible"),
        # Then check user's home directory
        os.path.join(os.path.expanduser("~"), ".rbible", "bibles", f"{version}.mybible")
    ]
    
    for bible_path in possible_paths:
        if os.path.exists(bible_path):
            try:
                conn = sqlite3.connect(bible_path)
                conn.row_factory = sqlite3.Row
                return conn
            except sqlite3.Error as e:
                print(f"Error: Could not open Bible version file '{version}.mybible'.")
                print(f"SQLite error: {e}")
                sys.exit(1)
    
    # If we get here, the file wasn't found
    print(f"Error: Bible version '{version}' not found.")
    available_versions = get_available_versions()
    if available_versions:
        print(f"Available versions: {', '.join(available_versions)}")
    sys.exit(1)

def get_available_versions():
    """Get list of available Bible versions."""
    versions = set()
    
    # Check multiple locations for Bible files
    possible_dirs = [
        os.path.join(os.getcwd(), "bibles"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "bibles"),
        os.path.join(os.path.expanduser("~"), ".rbible", "bibles")
    ]
    
    for bible_dir in possible_dirs:
        if os.path.exists(bible_dir):
            for file in os.listdir(bible_dir):
                if file.endswith('.mybible'):
                    versions.add(file[:-8])  # Remove .mybible extension
    
    return list(versions)

def get_book_id(book):
    """Get the book ID for a given book name or short code."""
    # Try to match by full name (case-insensitive)
    for full_name, data in BIBLE_BOOKS.items():
        if full_name.lower() == book.lower():
            return data["id"]
    
    # Try to match by short code (case-insensitive)
    for full_name, data in BIBLE_BOOKS.items():
        if data["short"].lower() == book.lower():
            return data["id"]
    
    # Not found
    return None

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
            print("Available books:")
            
            # Sort books by their ID (biblical order)
            sorted_books = sorted(BIBLE_BOOKS.items(), key=lambda x: x[1]["id"])
            
            # Define column settings
            num_columns = 3
            column_width = 25
            
            # Process books in groups for multi-column display
            for i in range(0, len(sorted_books), num_columns):
                row_books = sorted_books[i:i+num_columns]
                row_output = ""
                
                for book_name, book_data in row_books:
                    short_code = book_data["short"]
                    # Format each column entry with fixed width
                    entry = f"{book_name} ({short_code})".ljust(column_width)
                    row_output += entry
                    
                print(row_output)
            
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

def list_books():
    """List all available book names and their short codes in columns."""
    print("Available Bible books:")
    
    # Sort books by their ID (biblical order)
    sorted_books = sorted(BIBLE_BOOKS.items(), key=lambda x: x[1]["id"])
    
    # Define column settings
    num_columns = 3
    column_width = 25
    
    # Process books in groups for multi-column display
    for i in range(0, len(sorted_books), num_columns):
        row_books = sorted_books[i:i+num_columns]
        row_output = ""
        
        for book_name, book_data in row_books:
            short_code = book_data["short"]
            # Format each column entry with fixed width
            entry = f"{book_name} ({short_code})".ljust(column_width)
            row_output += entry
            
        print(row_output)

def list_available_online_versions():
    """List Bible versions available for download from GitHub releases."""
    # URL for the index.json file in the GitHub release
    url = f"https://github.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/releases/download/v1.0.0/index.json"
    
    try:
        print("Checking available online versions...")
        # Create a context that doesn't verify certificates
        import ssl
        context = ssl._create_unverified_context()
        
        with urllib.request.urlopen(url, context=context) as response:
            data = json.loads(response.read().decode())
            
        if 'versions' in data and data['versions']:
            print("Available versions for download:")
            for version in data['versions']:
                print(f"  {version['code']} - {version['name']}")
            return data['versions']
        else:
            print("No versions available for download.")
            return []
    except Exception as e:
        print(f"Error checking online versions: {e}")
        return []

def download_bible(version):
    """Download a Bible version from GitHub releases."""
    # If version is 'all', download all available versions
    if version.lower() == 'all':
        print("Downloading all available Bible versions...")
        versions_data = list_available_online_versions()
        if not versions_data:
            print("No versions available to download.")
            return False
        
        success = True
        for version_info in versions_data:
            version_code = version_info['code']
            # Call this function recursively for each version
            if not download_bible(version_code):
                success = False
        
        return success
    
    # Construct the URL for the Bible file
    url = f"https://github.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/releases/download/v1.0.0/{version}.mybible"
    
    # Ensure the destination directory exists
    user_bible_dir = os.path.join(os.path.expanduser("~"), ".rbible", "bibles")
    os.makedirs(user_bible_dir, exist_ok=True)
    
    dest_file = os.path.join(user_bible_dir, f"{version}.mybible")
    
    try:
        print(f"Downloading Bible version '{version}'...")
        # Create a context that doesn't verify certificates
        import ssl
        context = ssl._create_unverified_context()
        
        # Open the URL with the SSL context
        with urllib.request.urlopen(url, context=context) as response:
            # Read the content
            data = response.read()
            
            # Write to the destination file
            with open(dest_file, 'wb') as out_file:
                out_file.write(data)
        
        print(f"Successfully downloaded '{version}' to {user_bible_dir}")
        return True
    except Exception as e:
        print(f"Error downloading Bible version: {e}")
        return False

# Constants for history and favorites
HISTORY_FILE = os.path.join(os.path.expanduser("~"), ".rbible", "history.json")
FAVORITES_FILE = os.path.join(os.path.expanduser("~"), ".rbible", "favorites.json")
MAX_HISTORY_ITEMS = 50  # Maximum number of items to keep in history

def save_to_history(reference, text, version):
    """Save a verse reference to history."""
    history = load_history()
    
    # Add new entry at the beginning
    new_entry = {
        "reference": reference,
        "text": text,
        "version": version,
        "timestamp": import_time_module().time()  # Current timestamp
    }
    
    # Remove this reference if it already exists to avoid duplicates
    history = [h for h in history if h["reference"] != reference]
    
    # Add new entry at the beginning
    history.insert(0, new_entry)
    
    # Trim history to maximum size
    if len(history) > MAX_HISTORY_ITEMS:
        history = history[:MAX_HISTORY_ITEMS]
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    
    # Save to file
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def load_history():
    """Load verse history."""
    if not os.path.exists(HISTORY_FILE):
        return []
    
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load history: {e}")
        return []

def show_history(count=10):
    """Show recent verse history."""
    history = load_history()
    
    if not history:
        print("No verse history found.")
        return
    
    print(f"Recent verses (showing {min(count, len(history))} of {len(history)}):")
    for i, entry in enumerate(history[:count]):
        ref = entry["reference"]
        version = entry.get("version", "unknown")
        timestamp = entry.get("timestamp", 0)
        
        # Format timestamp if available
        time_str = ""
        if timestamp:
            time_module = import_time_module()
            time_str = time_module.strftime("%Y-%m-%d %H:%M", time_module.localtime(timestamp))
            
        print(f"{i+1}. {ref} ({version}) {time_str}")

def import_time_module():
    """Import time module on demand to avoid circular imports."""
    import time
    return time

def save_to_favorites(reference, text, version, name=None):
    """Save a verse reference to favorites with optional name."""
    favorites = load_favorites()
    
    # Create new entry
    new_entry = {
        "reference": reference,
        "text": text,
        "version": version,
        "name": name or reference,  # Use reference as name if none provided
        "added": import_time_module().time()  # Current timestamp
    }
    
    # Check if this reference already exists
    for i, fav in enumerate(favorites):
        if fav["reference"] == reference:
            # Update existing entry
            favorites[i] = new_entry
            break
    else:
        # Add new entry if not found
        favorites.append(new_entry)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(FAVORITES_FILE), exist_ok=True)
    
    # Save to file
    with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)
    
    print(f"Added to favorites: {reference}")

def load_favorites():
    """Load favorite verses."""
    if not os.path.exists(FAVORITES_FILE):
        return []
    
    try:
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load favorites: {e}")
        return []

def show_favorites(index=None):
    """Show favorite verses or get a specific favorite by index."""
    favorites = load_favorites()
    
    if not favorites:
        print("No favorites found.")
        return None
    
    # If an index is provided, return that specific favorite
    if index is not None:
        try:
            # Convert to zero-based index
            idx = int(index) - 1
            if 0 <= idx < len(favorites):
                return favorites[idx]
            else:
                print(f"Error: Favorite index {index} out of range (1-{len(favorites)}).")
                return None
        except ValueError:
            print(f"Error: Invalid favorite index '{index}'.")
            return None
    
    # Otherwise, display all favorites
    print(f"Favorite verses ({len(favorites)}):")
    for i, entry in enumerate(favorites):
        ref = entry["reference"]
        name = entry.get("name", ref)
        version = entry.get("version", "unknown")
        
        # Show name if different from reference
        if name != ref:
            print(f"{i+1}. {name} - {ref} ({version})")
        else:
            print(f"{i+1}. {ref} ({version})")
    
    return None

def remove_favorite(index_or_reference):
    """Remove a verse from favorites by index or reference."""
    favorites = load_favorites()
    
    if not favorites:
        print("No favorites found.")
        return False
    
    # Try to interpret as index (1-based)
    try:
        index = int(index_or_reference) - 1
        if 0 <= index < len(favorites):
            removed = favorites.pop(index)
            print(f"Removed from favorites: {removed['reference']}")
            
            # Save updated favorites
            with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
                json.dump(favorites, f, ensure_ascii=False, indent=2)
            return True
    except ValueError:
        # Not an integer, try as reference
        pass
    
    # Try to find by reference
    for i, fav in enumerate(favorites):
        if fav["reference"].lower() == index_or_reference.lower():
            removed = favorites.pop(i)
            print(f"Removed from favorites: {removed['reference']}")
            
            # Save updated favorites
            with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
                json.dump(favorites, f, ensure_ascii=False, indent=2)
            return True
    
    print(f"No favorite found with index or reference: {index_or_reference}")
    return False

def format_as_markdown(reference, text, include_reference=True, version=None):
    """Format verse text as markdown."""
    if include_reference:
        # Add version to reference if provided
        ref_display = reference
        if version:
            ref_display = f"{reference}({version})"
            
        # Add blockquote to both reference and verse text
        quoted_text = "\n".join([f"> {line}" for line in text.split("\n")])
        return f"> **{ref_display}**\n>\n{quoted_text}"
    else:
        # Add blockquote to the verse text without reference
        quoted_text = "\n".join([f"> {line}" for line in text.split("\n")])
        return quoted_text

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

def complete_reference(partial_ref):
    """Provide tab completion suggestions for Bible references."""
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

def main():
    parser = argparse.ArgumentParser(description='Command-line Bible verse lookup tool')
    parser.add_argument('-b', '--bible', help='Bible version to use')
    parser.add_argument('-v', '--verse', action='append', help='Bible verse reference (e.g., "Juan 3:16" or "Juan 3:16-20"). Can be specified multiple times.')
    parser.add_argument('-l', '--list', action='store_true', help='List available Bible versions')
    parser.add_argument('-B', '--books', action='store_true', help='List all Bible books and their short codes')
    parser.add_argument('-d', '--download', help='Download a Bible version (use "all" to download all available versions)', nargs='?', const='all')
    parser.add_argument('-o', '--online', action='store_true', help='List Bible versions available for download')
    parser.add_argument('-n', '--no-copy', action='store_true', help='Do not copy verse to clipboard')
    parser.add_argument('-m', '--markdown', action='store_true', help='Format output as markdown')
    parser.add_argument('-s', '--search', help='Search for verses containing the specified text')
    parser.add_argument('-H', '--history', action='store_true', help='Show recently viewed verses')
    parser.add_argument('--history-count', type=int, default=10, help='Number of history items to show')
    parser.add_argument('-f', '--favorite', help='Add a verse to favorites with optional name (format: "reference|name")')
    parser.add_argument('-F', '--favorites', nargs='?', const=True, help='Show favorite verses or get a specific favorite by index')
    parser.add_argument('-r', '--remove-favorite', help='Remove a verse from favorites by index or reference')
    parser.add_argument('-c', '--complete', help='Get completion suggestions for a partial reference')
    parser.add_argument('-p', '--parallel', help='Show verse in multiple translations (comma-separated versions)')
    
    args = parser.parse_args()
    
    # Handle non-verse lookup actions first
    if args.online:
        list_available_online_versions()
        sys.exit(0)
    
    if args.download:
        success = download_bible(args.download)
        sys.exit(0 if success else 1)
    
    if args.books:
        list_books()
        sys.exit(0)
    
    if args.list:
        versions = get_available_versions()
        if versions:
            print("Available Bible versions:")
            for version in sorted(versions):
                print(f"  {version}")
        else:
            print("No Bible versions found. Please add Bible SQLite files to the 'bibles' directory.")
        sys.exit(0)
    
    if args.history:
        show_history(args.history_count)
        sys.exit(0)
    
    # In the favorites section of main()
    if args.favorites:
        # If a specific index is provided
        if args.favorites is not True:  # True is the default value when no argument is provided
            favorite = show_favorites(args.favorites)
            if favorite:
                # Get the version
                version = favorite.get('version', 'unknown')
                
                # Print the verse with version
                if args.markdown:
                    formatted_text = format_as_markdown(favorite['reference'], favorite['text'], version=version)
                    print(f"\n{formatted_text}")
                else:
                    print(f"\n{favorite['reference']}({version})")
                    print(favorite['text'])
                
                # Copy to clipboard if not disabled
                if not args.no_copy:
                    clipboard_text = f"{favorite['reference']}({version})\n{favorite['text']}"
                    try:
                        pyperclip.copy(clipboard_text)
                        print("\nVerse copied to clipboard!")
                    except Exception as e:
                        print(f"\nFailed to copy to clipboard: {e}")
        else:
            # Just show all favorites
            show_favorites()
        sys.exit(0)
    
    if args.remove_favorite:
        remove_favorite(args.remove_favorite)
        sys.exit(0)
    
    if args.complete:
        suggestions = complete_reference(args.complete)
        for suggestion in suggestions:
            print(suggestion)
        sys.exit(0)
    
    # Select the first available version if none specified
    version = args.bible
    if not version:
        available_versions = get_available_versions()
        if not available_versions:
            print("No Bible versions found. Please add Bible SQLite files to the 'bibles' directory or download them with -d option.")
            sys.exit(1)
        version = available_versions[0]
    
    bible_conn = load_bible_version(version)
    
    # Handle search
    if args.search:
        results = search_bible(bible_conn, args.search)
        if results:
            print(f"Found {len(results)} verses containing '{args.search}':")
            for i, result in enumerate(results):
                print(f"\n{i+1}. {result['reference']}")
                print(result['highlighted'])
        bible_conn.close()
        sys.exit(0)
    
    # Handle favorite addition
    if args.favorite:
        # Change the separator from ':' to '|' to avoid conflict with verse references
        parts = args.favorite.split('|', 1)
        reference = parts[0]
        name = parts[1] if len(parts) > 1 else None
        
        try:
            book, chapter, verse = parse_reference(reference)
            verse_text = get_verse(bible_conn, book, chapter, verse)
            
            # Format the reference string
            if isinstance(verse, tuple):
                start_verse, end_verse = verse
                verse_str = f"{start_verse}-{end_verse}"
            else:
                verse_str = str(verse)
            
            ref_str = f"{book} {chapter}:{verse_str}"
            save_to_favorites(ref_str, verse_text, version, name)
        except Exception as e:
            print(f"Error adding favorite: {e}")
        
        bible_conn.close()
        sys.exit(0)
    
    # If no verse was provided, show help
    if not args.verse:
        parser.print_help()
        sys.exit(1)
    
    # Handle parallel verses first if specified
    if args.parallel and args.verse:
        if len(args.verse) > 1:
            print("Warning: Only the first verse reference will be used for parallel view.")
        
        verse_ref = args.verse[0]
        versions = args.parallel.split(',')
        
        # Validate versions
        available_versions = get_available_versions()
        invalid_versions = [v for v in versions if v not in available_versions]
        if invalid_versions:
            print(f"Warning: The following versions were not found: {', '.join(invalid_versions)}")
            print(f"Available versions: {', '.join(available_versions)}")
            # Filter out invalid versions
            versions = [v for v in versions if v in available_versions]
            
            if not versions:
                print("No valid versions specified.")
                sys.exit(1)
        
        parallel_results = get_parallel_verses(verse_ref, versions)
        formatted_output = format_parallel_verses(parallel_results, args.markdown)
        
        print(formatted_output)
        
        # Copy to clipboard if not disabled
        if not args.no_copy:
            try:
                pyperclip.copy(formatted_output)
                print("\nParallel verses copied to clipboard!")
            except Exception as e:
                print(f"\nFailed to copy to clipboard: {e}")
        
        bible_conn.close()
        sys.exit(0)
    
    # Update in main() function where verses are formatted
    # Process multiple verses if provided (only if not in parallel mode)
    all_verses = []
    for verse_ref in args.verse:
        book, chapter, verse = parse_reference(verse_ref)
        verse_text = get_verse(bible_conn, book, chapter, verse)
        
        # Format the reference string
        if isinstance(verse, tuple):
            start_verse, end_verse = verse
            verse_str = f"{start_verse}-{end_verse}"
        else:
            verse_str = str(verse)
        
        ref_str = f"{book} {chapter}:{verse_str}"
        
        # Format according to preference
        if args.markdown:
            formatted_text = format_as_markdown(ref_str, verse_text, version=version)
        else:
            formatted_text = f"\n{ref_str}({version})\n{verse_text}"
        
        all_verses.append({
            "reference": ref_str,
            "text": verse_text,
            "formatted": formatted_text
        })
        
        # Save to history
        save_to_history(ref_str, verse_text, version)
    
    # Display all verses
    for verse_data in all_verses:
        print(verse_data["formatted"])
    
    # Copy to clipboard if not disabled
    if not args.no_copy:
        # Format the text for clipboard
        if len(all_verses) == 1:
            # Single verse
            clipboard_text = all_verses[0]["formatted"]
        else:
            # Multiple verses
            if args.markdown:
                clipboard_text = "\n\n".join(v["formatted"] for v in all_verses)
            else:
                clipboard_text = "\n\n".join(v["formatted"] for v in all_verses)
        
        try:
            pyperclip.copy(clipboard_text)
            print("\nVerse(s) copied to clipboard!")
        except Exception as e:
            print(f"\nFailed to copy to clipboard: {e}")
    
    bible_conn.close()

if __name__ == "__main__":
    main()


def get_parallel_verses(verse_ref, versions):
    """Get the same verse in multiple translations."""
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

def format_parallel_verses(parallel_results, markdown=False):
    """Format parallel verses for display."""
    if not parallel_results:
        return "No results found."
    
    # Get the reference from the first successful result
    reference = next((r["reference"] for r in parallel_results if "error" not in r), "Unknown reference")
    
    if markdown:
        # Don't include version in main title for parallel view since we show multiple versions
        output = [f"> **{reference}**\n>"]
        
        for result in parallel_results:
            version = result["version"]
            if "error" in result:
                output.append(f"> *{version}*: Error - {result['error']}")
            else:
                # Add blockquote to each line of the verse text
                verse_text = result["text"]
                quoted_text = "\n".join([f"> {line}" for line in verse_text.split("\n")])
                output.append(f"> *{version}*:\n{quoted_text}")
        
        return "\n\n".join(output)
    else:
        output = [f"\n{reference}"]
        
        for result in parallel_results:
            version = result["version"]
            if "error" in result:
                output.append(f"\n[{version}] Error: {result['error']}")
            else:
                output.append(f"\n[{version}] {result['text']}")
        
        return "\n".join(output)