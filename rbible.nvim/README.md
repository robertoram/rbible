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

```lua
return {
  dir = "~/Documents/projects/rbible/rbible.nvim",
  lazy = false,
  config = function()
    local rbible = require("rbible")
    rbible.setup({
      setup_keymaps = true,
      enable_reference_detection = true,
      default_version = "RVR60",
      use_markdown = true,
      copy_to_clipboard = true,
      floating_window = {
        width = 0.6,
        height = 0.4,
        border = "rounded",
        title = "rbible",
        title_pos = "center",
      },
    })
  end,
}