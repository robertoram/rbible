#!/usr/bin/env python3
import os
import sqlite3
import json
import urllib.request
import sys

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