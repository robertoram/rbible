-- Check if the plugin is already loaded
if vim.g.loaded_rbible == 1 then
  return
end
vim.g.loaded_rbible = 1

-- Create user commands
vim.api.nvim_create_user_command("RBible", function(opts)
  require("rbible").lookup_verse(opts.args)
end, {
  nargs = 1,
  desc = "Look up a Bible verse"
})

vim.api.nvim_create_user_command("RBibleParallel", function(opts)
  local args = vim.split(opts.args, " ", {trimempty = true})
  if #args < 2 then
    vim.notify("Usage: RBibleParallel <reference> <version1,version2,...>", vim.log.levels.ERROR)
    return
  end
  
  local reference = args[1]
  local versions = vim.split(args[2], ",")
  require("rbible").parallel_verses(reference, versions)
end, {
  nargs = "+",
  desc = "Show parallel verses in multiple translations"
})

vim.api.nvim_create_user_command("RBibleSearch", function(opts)
  require("rbible").search_bible(opts.args)
end, {
  nargs = 1,
  desc = "Search the Bible for text"
})

-- Add a new command for adding favorites using comma as separator
vim.api.nvim_create_user_command("RBibleAddFavorite", function(opts)
  local args = vim.split(opts.args, ",", {trimempty = true})
  if #args < 2 then
    vim.notify("Usage: RBibleAddFavorite <reference>,<name>", vim.log.levels.ERROR)
    return
  end
  
  local reference = args[1]
  local name = args[2]
  require("rbible").add_to_favorites(reference, name)
end, {
  nargs = 1,
  desc = "Add a verse to favorites (format: reference,name)"
})

vim.api.nvim_create_user_command("RBibleFavorites", function()
  require("rbible").show_favorites()
end, {
  desc = "Show favorite verses"
})

vim.api.nvim_create_user_command("RBibleFavorite", function(opts)
  require("rbible").get_favorite(opts.args)
end, {
  nargs = 1,
  desc = "Get a specific favorite verse by index"
})