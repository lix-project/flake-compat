{
  flake-compat ? ../../default.nix,
}:
(import flake-compat {
  src = ./.;
}).defaultNix
