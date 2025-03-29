local M = {}

function M.setup()
  -- Define keybindings
  vim.keymap.set("n", "<leader>rb", function()
    vim.ui.input({ prompt = "Bible verse: " }, function(input)
      if input then
        vim.ui.input({ prompt = "Bible version (leave empty for default): " }, function(version)
          local opts = {}
          if version and version ~= "" then
            opts.version = version
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
        
        vim.ui.select(versions, {
          prompt = "Select Bible versions (press <Tab> to select multiple):",
          format_item = function(item)
            return item
          end,
          kind = "multi_select"
        }, function(selected_versions)
          if selected_versions and #selected_versions > 0 then
            require("rbible").parallel_verses(verse, selected_versions)
          end
        end)
      end
    end)
  end, { desc = "Show parallel verses" })

  vim.keymap.set("n", "<leader>rs", function()
    vim.ui.input({ prompt = "Search Bible for: " }, function(query)
      if query then
        require("rbible").search_bible(query)
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
          local command = "rbible -v " .. clean_ref .. " -m"
          local output = vim.fn.system(command)
          require("rbible").create_floating_window(output)
        else
          vim.notify("Could not parse reference: " .. selected.reference, vim.log.levels.ERROR)
        end
      end
    end)
  end, { desc = "Show verse history" })

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
                local favorite_cmd = "rbible -f \"" .. verse
                if name and name ~= "" then
                  favorite_cmd = favorite_cmd .. "|" .. name
                end
                favorite_cmd = favorite_cmd .. "\" -b " .. version
                
                local result = vim.fn.system(favorite_cmd)
                vim.notify(result, vim.log.levels.INFO)
              end)
            end
          end)
        end
      end)
    end, { desc = "Add verse to favorites with version selection" })
end

return M