local M = {}

-- Configuration with defaults
M.config = {
  default_version = nil,
  use_markdown = true,
  copy_to_clipboard = true,
  enable_reference_detection = true,
  floating_window = {
    width = 0.6,
    height = 0.4,
    border = "rounded",
    title = "rbible",
    title_pos = "center"
  }
}

-- Setup function to be called by the user
function M.setup_keymaps()
  require("rbible.keymaps").setup()
end

function M.setup(opts)
  M.config = vim.tbl_deep_extend("force", M.config, opts or {})
  
  -- Setup keymaps if enabled
  if opts and opts.setup_keymaps then
    M.setup_keymaps()
  end

  -- Initialize reference detector if enabled
  if M.config.enable_reference_detection then
    require("rbible.reference_detector").setup()
  end
end

-- Create a floating window
-- Change the local function to be part of the module
function M.create_floating_window(content)
  local width = math.floor(vim.o.columns * M.config.floating_window.width)
  local height = math.floor(vim.o.lines * M.config.floating_window.height)
  
  -- Calculate position
  local row = math.floor((vim.o.lines - height) / 2)
  local col = math.floor((vim.o.columns - width) / 2)
  
  -- Create buffer
  local buf = vim.api.nvim_create_buf(false, true)
  
  -- Set buffer content
  vim.api.nvim_buf_set_lines(buf, 0, -1, false, vim.split(content, "\n"))
  
  -- Set buffer options
  vim.api.nvim_buf_set_option(buf, "modifiable", false)
  vim.api.nvim_buf_set_option(buf, "bufhidden", "wipe")
  
  -- Window options
  local opts = {
    relative = "editor",
    width = width,
    height = height,
    row = row,
    col = col,
    style = "minimal",
    border = M.config.floating_window.border,
    title = M.config.floating_window.title,
    title_pos = M.config.floating_window.title_pos
  }
  
  -- Create window
  local win = vim.api.nvim_open_win(buf, true, opts)
  
  -- Set window options
  vim.api.nvim_win_set_option(win, "wrap", true)
  vim.api.nvim_win_set_option(win, "conceallevel", 2)
  vim.api.nvim_win_set_option(win, "concealcursor", "n")
  
  -- Set filetype for syntax highlighting
  if M.config.use_markdown then
    vim.api.nvim_buf_set_option(buf, "filetype", "markdown")
  end
  
  -- Close on q or Escape
  vim.api.nvim_buf_set_keymap(buf, "n", "q", ":close<CR>", {silent = true, noremap = true})
  vim.api.nvim_buf_set_keymap(buf, "n", "<Esc>", ":close<CR>", {silent = true, noremap = true})
  
  return buf, win
end

-- Create a floating window with title containing reference and version
function M.create_floating_window_with_title(content, reference, version)
  -- Save original title
  local original_title = M.config.floating_window.title
  
  -- Set custom title if reference and version are provided
  if reference and version then
    M.config.floating_window.title = reference .. " (" .. version .. ")"
  end
  
  -- Create the window
  local buf, win = M.create_floating_window(content)
  
  -- Restore original title
  M.config.floating_window.title = original_title
  
  return buf, win
end

-- Function to look up a Bible verse
  function M.lookup_verse(reference, opts)
    opts = opts or {}
    local version = opts.version or M.config.default_version
    local use_markdown = opts.markdown ~= nil and opts.markdown or M.config.use_markdown
    local copy = opts.copy ~= nil and opts.copy or M.config.copy_to_clipboard
    
    -- Properly format the reference
    reference = reference:gsub('"', ''):gsub("'", '')  -- Remove any existing quotes
    reference = '"' .. reference .. '"'  -- Add quotes around the reference
    
    -- Build command arguments
    local args = {"-v", reference}
    
    if version then
      table.insert(args, "-b")
      table.insert(args, version)
    end
    
    -- Always use markdown for clipboard formatting
    table.insert(args, "-m")
    
    -- Always use -n to prevent the CLI from copying to clipboard
    table.insert(args, "-n")
    
    -- Execute rbible command with properly escaped arguments
    local command = "rbible " .. table.concat(args, " ")
    local output = vim.fn.system(command)
    
    -- Copy to clipboard if enabled
    if copy and M.config.copy_to_clipboard then
      local clipboard_text = output
      
      -- Use custom formatter if provided
      if opts.clipboard_formatter and type(opts.clipboard_formatter) == "function" then
        clipboard_text = opts.clipboard_formatter(output)
      end
      
      vim.fn.setreg('+', clipboard_text)
      vim.notify("Verse copied to clipboard", vim.log.levels.INFO)
    end
  
  -- Display in floating window with title
  M.create_floating_window_with_title(output, ref, ver)
end

-- Function to show parallel verses
function M.parallel_verses(reference, versions)
  -- Ensure versions is a table
  if type(versions) == "string" then
    versions = {versions}
  end
  
  -- Instead of using the -p flag, we'll look up the verse in each version separately
  local outputs = {}
  
  -- Properly format the reference - ensure it's properly quoted
  reference = reference:gsub('"', '')  -- Remove any existing quotes
  
  for _, version in ipairs(versions) do
    -- Construct the command for each version - add -n to prevent clipboard copy
    -- Use proper quoting for the reference
    local cmd = string.format('rbible -v "%s" -b %s -m -n', reference, version)
    
    -- Execute the command
    local output = vim.fn.system(cmd)
    
    -- Check if we got actual content
    if vim.v.shell_error == 0 then
      -- Add a header for each version
      table.insert(outputs, "## " .. version .. "\n" .. output)
    else
      vim.notify("Error looking up verse in " .. version .. ": " .. output, vim.log.levels.WARN)
    end
  end
  
  -- Combine the outputs with clear separation
  local combined_output = table.concat(outputs, "\n\n---\n\n")
  
  -- Copy to clipboard if enabled
  if M.config.copy_to_clipboard then
    vim.fn.setreg('+', combined_output)
    vim.notify("Parallel verses copied to clipboard", vim.log.levels.INFO)
  end
  
  -- Display the result
  if combined_output ~= "" then
    M.create_floating_window(combined_output)
  else
    vim.notify("No results found for parallel verses", vim.log.levels.ERROR)
  end
end

-- Function to search the Bible
function M.search_bible(query, opts)
  opts = opts or {}
  local version = opts.version or M.config.default_version
  
  -- Properly format the query
  query = query:gsub('"', ''):gsub("'", '')  -- Remove any existing quotes
  query = '"' .. query .. '"'  -- Add quotes around the query
  
  -- Build command arguments
  local args = {"-s", query, "-m"}  -- Add -m flag for markdown formatting
  
  if version then
    table.insert(args, "-b")
    table.insert(args, version)
  end
  
  -- Execute rbible command
  local command = "rbible " .. table.concat(args, " ")
  local output = vim.fn.system(command)
  
  -- Create a search-specific title
  local search_title = "Search: " .. query
  if version then
    search_title = search_title .. " (" .. version .. ")"
  end
  
  -- Display in floating window with title
  M.create_floating_window_with_title(output, search_title, nil)
end

-- Function to show favorites
function M.show_favorites()
  -- Execute rbible command
  local command = "rbible -F"
  local output = vim.fn.system(command)
  
  -- Display in floating window with title
  M.create_floating_window_with_title(output, "Favorites", nil)
end

-- Function to get a specific favorite
function M.get_favorite(index, opts)
  opts = opts or {}
  local use_markdown = opts.markdown ~= nil and opts.markdown or M.config.use_markdown
  local copy = opts.copy ~= nil and opts.copy or M.config.copy_to_clipboard
  
  -- Build command arguments
  local args = {"-F", tostring(index)}
  
  if use_markdown then
    table.insert(args, "-m")
  end
  
  if not copy then
    table.insert(args, "-n")
  end
  
  -- Execute rbible command
  local command = "rbible " .. table.concat(args, " ")
  local output = vim.fn.system(command)
  
  -- Extract reference and version from output if available
  local ref, ver
  if use_markdown then
    ref, ver = output:match("> %*%*([^%)]+)%s%(([^%)]+)%)")
  end
  
  -- Display in floating window with title
  M.create_floating_window_with_title(output, ref, ver)
end

return M