# rbible

A command-line Bible verse lookup tool that supports multiple Bible versions.

## Features

- Look up Bible verses by reference (e.g., "Juan 3:16")
- Support for verse ranges (e.g., "Juan 3:16-20")
- Multiple Bible versions support
- Download Bible versions from GitHub releases
- List available Bible books and versions

## Installation

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
