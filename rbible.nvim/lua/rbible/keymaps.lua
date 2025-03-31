local M = {}

function M.setup()
  -- Define keybindings
  vim.keymap.set("n", "<leader>rb", function()
    vim.ui.input({ prompt = "Bible verse: " }, function(input)
      if input then
        -- Remove any quotation marks from the input
        input = input:gsub('"', ''):gsub("'", '')
        
        vim.ui.input({ prompt = "Bible version (leave empty for default): " }, function(version)
          local opts = {}
          if version and version ~= "" then
            opts.version = version
          end
          
          -- Always use markdown for better formatting
          opts.markdown = true
          
          -- Set a custom clipboard formatter to preserve CLI output
          opts.clipboard_formatter = function(text)
            return text
          end
          
          require("rbible").lookup_verse(input, opts)
        end)
      end
    end)
  end, { desc = "Look up Bible verse" })

  vim.keymap.set("n", "<leader>rp", function()
    vim.ui.input({ prompt = "Bible verse: " }, function(verse)
      if verse then
        -- Get available versions and show them in a selection menu
        local command = "rbible -l"
        local output = vim.fn.system(command)
        local versions = {}
        for line in output:gmatch("[^\r\n]+") do
          if line:match("^%s+%w+") then
            table.insert(versions, line:match("^%s+(%w+)"))
          end
        end
        
        -- Create a custom multi-select UI
        local selected_versions = {}
        
        -- Function to display the selection UI
        local function display_selection_ui()
          -- Create a formatted list with checkmarks for selected versions
          local items = {}
          for _, v in ipairs(versions) do
            local is_selected = false
            for _, sv in ipairs(selected_versions) do
              if v == sv then
                is_selected = true
                break
              end
            end
            
            local display = is_selected and "✓ " .. v or "  " .. v
            table.insert(items, {text = display, value = v, selected = is_selected})
          end
          
          -- Add a "Done" option at the end
          table.insert(items, {text = "✅ Done - Show parallel verses", value = "DONE"})
          
          vim.ui.select(items, {
            prompt = "Select Bible versions (current: " .. table.concat(selected_versions, ", ") .. ")",
            format_item = function(item)
              return item.text
            end
          }, function(item)
            if item then
              if item.value == "DONE" then
                if #selected_versions > 0 then
                  -- Execute the parallel verses lookup
                  require("rbible").parallel_verses(verse, selected_versions)
                else
                  vim.notify("Please select at least one version", vim.log.levels.WARN)
                  display_selection_ui()
                end
              else
                -- Toggle selection
                local found = false
                for i, v in ipairs(selected_versions) do
                  if v == item.value then
                    table.remove(selected_versions, i)
                    found = true
                    break
                  end
                end
                
                if not found then
                  table.insert(selected_versions, item.value)
                end
                
                -- Show the UI again
                display_selection_ui()
              end
            end
          end)
        end
        
        -- Start the selection process
        display_selection_ui()
      end
    end)
  end, { desc = "Show parallel verses" })

  vim.keymap.set("n", "<leader>rs", function()
    vim.ui.input({ prompt = "Search Bible for: " }, function(query)
      if query then
        local opts = {
          markdown = true  -- Enable markdown formatting for search results
        }
        require("rbible").search_bible(query, opts)
      end
    end)
  end, { desc = "Search Bible" })

  -- Show favorites with interactive selection
  vim.keymap.set("n", "<leader>rf", function()
    -- First get the favorites list
    local command = "rbible -F"
    local output = vim.fn.system(command)
    
    -- Parse the favorites
    local favorites = {}
    local favorite_items = {}
    for line in output:gmatch("[^\r\n]+") do
      local index, desc = line:match("^(%d+)%. (.+)$")
      if index and desc then
        favorites[index] = desc
        table.insert(favorite_items, { index = index, desc = desc })
      end
    end
    
    if #favorite_items == 0 then
      vim.notify("No favorites found", vim.log.levels.INFO)
      return
    end
    
    -- Show selection menu
    vim.ui.select(favorite_items, {
      prompt = "Select a favorite verse:",
      format_item = function(item)
        return item.index .. ". " .. item.desc
      end
    }, function(selected)
      if selected then
        require("rbible").get_favorite(selected.index)
      end
    end)
  end, { desc = "Show and select favorite verses" })

  -- Add history command
  vim.keymap.set("n", "<leader>rh", function()
    -- Get history
    local command = "rbible -H"
    local output = vim.fn.system(command)
    
    -- Parse history
    local history_items = {}
    for line in output:gmatch("[^\r\n]+") do
      local index, ref = line:match("^(%d+)%. (.+)$")
      if index and ref then
        table.insert(history_items, { index = index, reference = ref })
      end
    end
    
    if #history_items == 0 then
      vim.notify("No history found", vim.log.levels.INFO)
      return
    end
    
    -- Show selection menu
    vim.ui.select(history_items, {
      prompt = "Select a verse from history:",
      format_item = function(item)
        return item.index .. ". " .. item.reference
      end
    }, function(selected)
      if selected then
        -- Extract just the reference part - look for the book and reference format
        local book_ref = selected.reference:match("([%w%s]+%s%d+:%d+[%-%d:]*)") 
        if book_ref then
          -- Clean up any trailing spaces and wrap in quotes to handle spaces in book names
          local clean_ref = '"' .. book_ref:gsub("%s+$", "") .. '"'
          -- Use lookup_verse instead of direct command
          local opts = {
            markdown = true
          }
          require("rbible").lookup_verse(book_ref, opts)
        else
          vim.notify("Could not parse reference: " .. selected.reference, vim.log.levels.ERROR)
        end
      end
    end)
  end, { desc = "Show verse history" })

  -- Add a favorite with version selection
    -- Add a favorite with version selection
    vim.keymap.set("n", "<leader>ra", function()
      vim.ui.input({ prompt = "Bible verse to add as favorite: " }, function(verse)
        if verse then
          -- Get available versions and show them in a selection menu
          local command = "rbible -l"
          local output = vim.fn.system(command)
          local versions = {}
          for line in output:gmatch("[^\r\n]+") do
            if line:match("^%s+%w+") then
              table.insert(versions, line:match("^%s+(%w+)"))
            end
          end
          
          vim.ui.select(versions, {
            prompt = "Select Bible version:",
            format_item = function(item)
              return item
            end
          }, function(version)
            if version then
              vim.ui.input({ prompt = "Optional name for this favorite: " }, function(name)
                -- Remove any quotation marks from the verse reference
                verse = verse:gsub('"', ''):gsub("'", '')
                
                -- Check if verse contains a book name
                if not verse:match("%a+%s+%d+:%d+") then
                  vim.notify("Invalid verse format. Should be 'Book Chapter:Verse' (e.g. Jos 1:9)", vim.log.levels.ERROR)
                  return
                end
                
                -- Properly escape and quote the favorite argument
                local favorite_arg = verse
                if name and name ~= "" then
                  favorite_arg = favorite_arg .. "|" .. name
                end
                
                -- Construct the command with proper quoting
                local favorite_cmd = "rbible -f '" .. favorite_arg .. "' -b " .. version
                
                -- Debug output
                vim.notify("Executing: " .. favorite_cmd, vim.log.levels.DEBUG)
                
                local result = vim.fn.system(favorite_cmd)
                if vim.v.shell_error ~= 0 then
                  vim.notify("Error adding favorite: " .. result, vim.log.levels.ERROR)
                else
                  vim.notify("Added to favorites: " .. verse, vim.log.levels.INFO)
                end
              end)
            end
          end)
        end
      end)
    end, { desc = "Add verse to favorites with version selection" })
end

return M