local M = {}

function M.setup(opts)
  opts = opts or {}
  -- Configuración por defecto
  local config = {
    setup_keymaps = opts.setup_keymaps or false,
    enable_reference_detection = opts.enable_reference_detection or false
  }
  
  -- Configurar keymaps si está habilitado
  if config.setup_keymaps then
    vim.keymap.set('n', '<leader>rb', ':RBible ', { desc = 'Look up Bible verse' })
    vim.keymap.set('n', '<leader>rp', ':RBibleParallel ', { desc = 'Show parallel verses' })
    vim.keymap.set('n', '<leader>rs', ':RBibleSearch ', { desc = 'Search Bible' })
    vim.keymap.set('n', '<leader>rf', ':RBibleFavorites<CR>', { desc = 'Show favorites' })
    vim.keymap.set('n', '<leader>ra', ':RBibleAddFavorite ', { desc = 'Add to favorites' })
    vim.keymap.set('n', '<leader>rh', ':RBibleHistory<CR>', { desc = 'Show history' })
    vim.keymap.set('n', '<leader>rg', ':RBibleFindReferences<CR>', { desc = 'Find references' })
  end
end

-- Update the add_to_favorites function to handle comma-separated input
-- Update the add_to_favorites function to properly escape special characters
function M.add_to_favorites(reference, name)
  -- Print debug info
  vim.notify("Reference: '" .. reference .. "'", vim.log.levels.DEBUG)
  vim.notify("Name: '" .. name .. "'", vim.log.levels.DEBUG)
  
  -- Check if the reference includes a book name
  if not reference:match("%a+%s+%d+:%d+") then
    -- Try to extract chapter and verse
    local chapter, verse = reference:match("(%d+):(%d+)")
    
    if chapter and verse then
      -- Ask user for the book name
      vim.ui.input({prompt = "Book name is missing. Enter book name: "}, function(book)
        if book and book ~= "" then
          -- Reconstruct the reference with the book name
          local full_reference = book .. " " .. reference
          -- Call this function again with the complete reference
          M.add_to_favorites(full_reference, name)
        else
          vim.notify("Book name is required", vim.log.levels.ERROR)
        end
      end)
      return
    else
      vim.notify("Invalid reference format. Should be 'Book Chapter:Verse'", vim.log.levels.ERROR)
      return
    end
  end
  
  -- Escape the pipe character and quotes for shell safety
  local escaped_arg = reference .. "|" .. name
  escaped_arg = escaped_arg:gsub('"', '\\"')
  
  -- Use single quotes around the entire argument to preserve special characters
  local cmd = "rbible -f '" .. escaped_arg .. "'"
  
  -- Debug output to see what's being executed
  vim.notify("Executing: " .. cmd, vim.log.levels.DEBUG)
  
  -- Execute the command
  local output = vim.fn.system(cmd)
  
  -- Show the result
  if vim.v.shell_error ~= 0 then
    vim.notify("Error adding favorite: " .. output, vim.log.levels.ERROR)
  else
    vim.notify("Added to favorites: " .. reference, vim.log.levels.INFO)
  end
end

return M