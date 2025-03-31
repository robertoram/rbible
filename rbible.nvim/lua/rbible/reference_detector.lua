local M = {}

-- Bible reference pattern with capture groups to exclude surrounding spaces
local reference_pattern = "[%s]*([1-3]?%s*[A-Za-zÀ-ÿ]+%s+%d+:%d+[%-]?%d*)"

function M.detect_references()
  local bufnr = vim.api.nvim_get_current_buf()
  local lines = vim.api.nvim_buf_get_lines(bufnr, 0, -1, false)
  local references = {}
  
  for lnum, line in ipairs(lines) do
    local start_idx = 1
    while true do
      local s, e, reference = line:find(reference_pattern, start_idx)
      if not s then break end
      
      -- Calculate actual reference position without spaces
      local ref_start = line:find(reference, s, true)
      local ref_length = #reference
      
      -- Normalize spaces in reference
      reference = reference:gsub("%s+", " "):match("^%s*(.-)%s*$")
      
      table.insert(references, {
        reference = reference,
        lnum = lnum - 1,
        col_start = ref_start - 1,
        col_end = ref_start + ref_length - 2
      })
      
      start_idx = s + ref_length
    end
  end
  
  return references
end

function M.setup()
  -- Set updatetime for faster hover response
  vim.o.updatetime = 300

  -- Create highlight group for references
  vim.api.nvim_command('highlight default link BibleReference Underlined')

  -- Setup hover handler and highlighting
  vim.api.nvim_create_autocmd({"CursorHold", "BufEnter", "TextChanged", "TextChangedI"}, {
    pattern = {"*"},
    callback = function()
      -- Skip special buffers
      local buftype = vim.bo.buftype
      if buftype == "prompt" or buftype == "nofile" then
        return
      end

      -- Clear existing highlights
      vim.fn.clearmatches()
      
      -- Get references and highlight them
      local references = M.detect_references()
      for _, ref in ipairs(references) do
        vim.fn.matchaddpos("BibleReference", {{
          ref.lnum + 1,
          ref.col_start + 1,
          ref.col_end - ref.col_start + 1
        }})
      end

      -- Check for hover
      local line = vim.api.nvim_get_current_line()
      local pos = vim.api.nvim_win_get_cursor(0)
      local col = pos[2]

      for reference in line:gmatch(reference_pattern) do
        local start_pos = line:find(reference, 1, true)
        if start_pos and col >= start_pos - 1 and col <= start_pos + #reference - 1 then
          local command = string.format('rbible -v "%s" -m', reference)
          local output = vim.fn.system(command)
          
          if output and output ~= "" then
            local lines = vim.split(output, "\n")
            if #lines > 0 then
              vim.lsp.util.open_floating_preview(
                lines,
                "markdown",
                { border = "rounded", focus = false }
              )
            end
          end
          break
        end
      end
    end
  })
end

return M