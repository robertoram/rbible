return {
  -- Use local directory instead of GitHub repository
  dir = "/Users/david/Documents/projects/rbible/rbible.nvim",
  name = "rbible.nvim",
  config = function()
    require('rbible').setup({
      default_version = "LBLA",
      use_markdown = true,
      setup_keymaps = true,
      floating_window = {
        width = 0.7,
        height = 0.5,
        border = "rounded",
        title = "rbible",
        title_pos = "center"
      }
    })
  end
}