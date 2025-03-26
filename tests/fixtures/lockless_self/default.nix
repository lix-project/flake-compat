{
  flake-compat ? ../../../default.nix,
  # Required to be duplicated since --arg autocall is HAUNTED
  # See: https://git.lix.systems/lix-project/lix/issues/263
  copySourceTreeToStore ? true,
}:
(import flake-compat {
  src = ./.;
  inherit copySourceTreeToStore;
}).defaultNix
