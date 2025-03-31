#!/usr/bin/env python3
"""
rbible - Command-line Bible verse lookup tool
"""

import sys
import argparse
import pyperclip

# Fix imports to use relative imports within the package
from rbible.bible_data import (
    get_available_versions, load_bible_version, list_books,
    list_available_online_versions, download_bible
)
from rbible.verse_operations import (
    parse_reference, get_verse, search_bible, get_parallel_verses,
    complete_reference
)
from rbible.user_data import (
    save_to_history, show_history, save_to_favorites,
    show_favorites, remove_favorite
)
from rbible.formatters import format_as_markdown, format_parallel_verses

def main():
    parser = argparse.ArgumentParser(
        description='Command-line Bible verse lookup tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  rbible -v "Juan 3:16"                # Look up a verse
  rbible -v "Juan 3:16" -b LBLA        # Use specific version
  rbible -v "Salmos 23:1-6"            # Look up verse range
  rbible -v "Juan 3:16" -m             # Format as markdown
  rbible -v "Juan 3:16" -p "LBLA,RVR"  # Show in multiple versions
  rbible -s "amor"                     # Search for text
  rbible -f "Juan 3:16|God's love"     # Add to favorites
  rbible -F                            # Show all favorites
  rbible -F 1                          # Show favorite #1
  rbible -r 1                          # Remove favorite #1
  rbible -H                            # Show history
  rbible -l                            # List available versions
  rbible -B                            # List Bible books
  rbible -d LBLA                       # Download a version
'''
    )
    
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
                
                # Print the verse with version - only show the appropriate format based on args.markdown
                if args.markdown:
                    formatted_text = format_as_markdown(favorite['reference'], favorite['text'], version=version)
                    print(f"\n{formatted_text}")
                else:
                    print(f"\n{favorite['reference']}({version})")
                    print(favorite['text'])
                
                # Copy to clipboard if not disabled
                if not args.no_copy:
                    # Choose clipboard format based on markdown flag
                    if args.markdown:
                        clipboard_text = format_as_markdown(favorite['reference'], favorite['text'], version=version)
                    else:
                        clipboard_text = f"{favorite['reference']}({version})\n{favorite['text']}"
                    
                    try:
                        pyperclip.copy(clipboard_text)
                        print(f"\nVerse copied to clipboard!")
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
            if len(all_verses) == 1:
                # Single verse - copy reference and text
                verse_data = all_verses[0]
                if args.markdown:
                    # Use the formatted text directly - it already has the > symbols
                    clipboard_text = verse_data["formatted"]
                else:
                    clipboard_text = f"{verse_data['reference']}({version})\n{verse_data['text']}"
            else:
                # Multiple verses - copy all formatted output
                clipboard_text = "\n\n".join([v["formatted"] for v in all_verses])
            
            try:
                pyperclip.copy(clipboard_text)
                print("\nVerse(s) copied to clipboard!")
            except Exception as e:
                print(f"\nFailed to copy to clipboard: {e}")
    
    bible_conn.close()

if __name__ == "__main__":
    main()