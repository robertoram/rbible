# rbible

A command-line Bible verse lookup tool that supports multiple Bible versions, with Neovim integration.

## Features

- Look up Bible verses by reference (e.g., "Juan 3:16")
- Support for verse ranges (e.g., "Juan 3:16-20")
- Multiple Bible versions support
- Download Bible versions from GitHub releases
- List available Bible books and versions
- Favorites management
- Search functionality
- History tracking
- Markdown output formatting
- Parallel verses view
- Neovim plugin with:
  - Automatic Bible reference detection and highlighting
  - Hover preview of verses
  - Quick verse lookup (`<leader>rb`)
  - Parallel verses view (`<leader>rp`)
  - Bible search (`<leader>rs`)
  - Favorites management (`<leader>rf`, `<leader>ra`)
  - History browsing (`<leader>rh`)
  - Reference finder (`<leader>rg`)

## Installation

### CLI Tool
```bash
pip install rbible
```

## Usage
```bash
# Look up a verse
rbible -v "Juan 3:16"

# Look up a verse in a specific Bible version
rbible -b RVR60 -v "Juan 3:16"

# Look up a verse range
rbible -v "Juan 3:16-20"

# List available Bible versions
rbible -l

# List all Bible books
rbible -B

# List Bible versions available for download
rbible -o

# Download a specific Bible version
rbible -d RVR60

# Download all available Bible versions
rbible -d all
```
{
  "davidmh/rbible.nvim",
  config = function()
    require("rbible").setup({
      setup_keymaps = true,
      enable_reference_detection = true
    })
  end
}
```

Usage
```
# Look up a verse
rbible -v "Juan 3:16"

# Look up a verse in a specific Bible version
rbible -b RVR60 -v "Juan 3:16"

# Look up a verse range
rbible -v "Juan 3:16-20"

# List available Bible versions
rbible -l

# List all Bible books
rbible -B

# List Bible versions available for download
rbible -o

# Download a specific Bible version
rbible -d RVR60

# Download all available Bible versions
rbible -d all

# Add a verse to favorites
rbible -f "Juan 3:16" -b RVR60

# List favorites
rbible -F

# Search the Bible
rbible -s "amor"

# Show verse history
rbible -H
```

### Neovim Keymaps
- <leader>rb - Look up a Bible verse
- <leader>rp - Show parallel verses in multiple versions
- <leader>rs - Search the Bible
- <leader>rf - Show and select favorites
- <leader>ra - Add verse to favorites
- <leader>rh - Show verse history
- <leader>rg - Find Bible references in current buffer
The plugin also automatically detects and highlights Bible references in your text, showing verse previews when you hover over them.