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

return M 