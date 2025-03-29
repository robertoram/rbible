# rbible.nvim

A Neovim plugin for the rbible command-line Bible verse lookup tool.

## Features

- Look up Bible verses directly from Neovim
- Display verses in a floating window with markdown formatting
- Search the Bible for specific text
- View parallel translations of the same verse
- Access your favorite verses

## Installation

### Using [packer.nvim](https://github.com/wbthomason/packer.nvim)

```lua
use {
  'your-username/rbible.nvim',
  config = function()
    require('rbible').setup({
      -- Optional configuration
    })
  end
}