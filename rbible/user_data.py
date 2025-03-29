#!/usr/bin/env python3
import os
import json

# Constants for history and favorites
HISTORY_FILE = os.path.join(os.path.expanduser("~"), ".rbible", "history.json")
FAVORITES_FILE = os.path.join(os.path.expanduser("~"), ".rbible", "favorites.json")
MAX_HISTORY_ITEMS = 50  # Maximum number of items to keep in history

def import_time_module():
    """Import time module on demand to avoid circular imports."""
    import time
    return time

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