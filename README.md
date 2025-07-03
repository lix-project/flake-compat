# flake-compat

## Usage

To use, add the following to your `flake.nix`:

```nix
inputs.flake-compat = {
  url = "https://git.lix.systems/lix-project/flake-compat/archive/main.tar.gz";
  # Optional:
  flake = false;
};
```

Afterwards, create a `default.nix` file containing the following:

```nix
let
  lockFile = builtins.fromJSON (builtins.readFile ./flake.lock);
  flake-compat-node = lockFile.nodes.${lockFile.nodes.root.inputs.flake-compat};
  flake-compat = builtins.fetchTarball {
    inherit (flake-compat-node.locked) url;
    sha256 = flake-compat-node.locked.narHash;
  };

  flake = (
    import flake-compat {
      src = ./.;
    }
  );
in
  flake.defaultNix
```

If you would like a `shell.nix` file, create one containing the above, replacing `defaultNix` with `shellNix`.

You can access any flake output via the `outputs` attribute returned by `flake-compat`, e.g.

```nix
(import ... { src = ./.; }).outputs.packages.x86_64-linux.default
```

## Output attributes

Lix flake-compat exposes the following attributes (which you can inspect with `nix repl -f default.nix` for example):
- `inputs` - the same `inputs` that a flake would receive in the `outputs` function.
- `defaultNix` - the outputs of a flake; what you would see in `nix repl .#`, plus a `default` attribute of the default package.
- `shellNix` - the same as `defaultNix`, but with `default` as the default dev shell rather than the default package.

## Input attributes

- `src` - the source tree to use, containing `flake.nix`. Generally `./.` or similar.
- `copySourceTreeToStore` - whether to copy the flake's source tree to the Nix store.

  By default Lix flake-compat behaves the same as native flakes and copies the flake's source tree to the Nix store.
  This option allows for faster evaluation by skipping this copy and breaking strict compatibility with flakes if desired.

  Setting this to false may lead to the content of gitignored paths or the absolute path of the flake being evaluated leaking into the evaluation.
  We strongly recommend using [nix-diff] to verify evaluation produces the smae result.
  Here be (some) dragons.

  See [Copying to the store](#copying-to-the-store).

  Default: `true`.
- `useBuiltinsFetchTree` - whether to use `builtins.fetchTree` in place of flake-compat's Nix language implementation of it.
  If enabled and if `builtins.fetchTree` is present, it will be used.
  This will throw an error if using Lix older than 2.93 or CppNix <=2.18.x with flakes disabled due to a bug in the Nix implementation.

  The benefit of using this setting is that it will expose the full functionality (and bug-compatible behaviour) of the built-in flake implementation's fetchers and thus eliminate some possible evaluation divergences by doing the exact same thing as native flakes for fetching.

  Default: `false`.
- `system` - the attributes to expose as `.default` from `devShells` and `packages` for `default.nix` and `shell.nix`.
  Default: `builtins.currentSystem`.

### Copying to the store

Flakes are known for many things, but one thing they are known for is very poor evaluation performance on nixpkgs and other large repos on account of copying several dozen megabytes of source to the store repeatedly.
This leads to the premise of a long-promised feature in CppNix called Lazy Trees that's been a significant struggle to stabilize, and which will not exist in Lix for the foreseeable future; the concept is to virtualize the flake filesystem access model, effectively returning to the behaviour of non-flakes Nix, albeit following gitignore.

If you *need* Lazy Trees today, Lix flake-compat has you covered:

Lix flake-compat, by default, is compatible with the Flakes behaviour of copying your entire source tree to the store and thereby obeying gitignore.
If you *need* to not copy a flake to the store, i.e., to undo the "automatic gitignore" feature of flakes, there is an option `copySourceTreeToStore` that may be set to false when importing flake-compat.

Setting this option is likely to cause evaluation to change results especially if there are references to directories inside of `.nix` files, and requires validating the lack of unintended changes.
To do such validation, use [nix-diff]:

```
$ nix-diff $(nix eval --raw -f default.nix default.drvPath) $(nix eval --raw .#default.drvPath)
```

[nix-diff]: https://github.com/Gabriella439/nix-diff

Often times, this will reveal that some things in gitignore *were* load-bearing.
One way to fix these issues is to use [lib.fileset] in order to explicitly define the files expected to be copied to the store.
A benefit of this, regardless of using Flakes or not is that there will be fewer spurious rebuilds since fewer random files land in derivations.

[lib.fileset]: https://nixos.org/manual/nixpkgs/stable/#sec-functions-library-fileset
