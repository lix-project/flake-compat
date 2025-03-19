# Separate flake for validation, since we don't want to make these visible to users
{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.pre-commit-hooks = {
    url = "github:cachix/git-hooks.nix";
    flake = false;
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      pre-commit-hooks,
    }:
    (flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };
        checks = self.checks.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          shellHook = ''
            ${nixpkgs.lib.optionalString (checks.pre-commit ? shellHook) checks.pre-commit.shellHook}
          '';
          nativeBuildInputs = with pkgs.buildPackages; [
            treefmt
            nixfmt-rfc-style
            ruff

            python3
            python3Packages.pytest
          ];
        };

        checks.pre-commit =
          let
            # Avoid an unnecessary reimport of nixpkgs
            tools = import (pre-commit-hooks + "/nix/call-tools.nix") pkgs;
            pre-commit-run = pkgs.callPackage (pre-commit-hooks + "/nix/run.nix") {
              inherit tools;
              isFlakes = true;
              # unused!
              gitignore-nix-src = builtins.throw "gitignore-nix-src is unused";
            };
          in
          pre-commit-run {
            src = ../.;
            hooks = {
              treefmt = {
                enable = true;
                settings.formatters = with pkgs.buildPackages; [
                  ruff
                  nixfmt-rfc-style
                ];
              };
            };
          };
      }
    ));
}
