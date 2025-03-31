return {
  {
    "which-key.nvim",
    event = "VeryLazy",
    init = function()
      vim.o.timeout = true
      vim.o.timeoutlen = 300
    end,
    opts = {}
  },
  {
    "davidmh/rbible.nvim",
    dependencies = { "which-key.nvim" },
    config = function()
      require("rbible").setup({
        setup_keymaps = true
      })
    end
  }
}