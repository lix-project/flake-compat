# flake-compat

## Usage

> [!WARNING]
> During the Lix private beta period during which Forgejo is private, this
> requires configuring netrc in Lix for the tarball download to work.
>
> Your netrc should look something like so:
> ```
> machine git.lix.systems login YOUR-USERNAME password SOME-PERSONAL-ACCESS-TOKEN-REPO-READ
> ```
>
> We are terribly sorry for the UX for this being very bad
> ([issue](https://git.lix.systems/lix-project/lix/issues/254)).

To use, add the following to your `flake.nix`:

<!-- FIXME: this can use the standard non-api archive url when we are
un-privated -->

```nix
inputs.flake-compat.url = "https://git.lix.systems/api/v1/repos/lix-project/flake-compat/archive/main.tar.gz";
```

Afterwards, create a `default.nix` file containing the following:

```nix
(import
  (
    let lock = builtins.fromJSON (builtins.readFile ./flake.lock); in
    fetchTarball {
      url = lock.nodes.flake-compat.locked.url;
      sha256 = lock.nodes.flake-compat.locked.narHash;
    }
  )
  { src = ./.; }
).defaultNix
```

If you would like a `shell.nix` file, create one containing the above, replacing `defaultNix` with `shellNix`.
