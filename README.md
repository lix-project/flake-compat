# flake-compat

## Usage

To use, add the following to your `flake.nix`:

```nix
inputs.flake-compat = {
  url = "git+https://git.lix.systems/lix-project/flake-compat";
  # Optional:
  flake = false;
};
```

Afterwards, create a `default.nix` file containing the following:

```nix
(import
  (
    let
      lock = builtins.fromJSON (builtins.readFile ./flake.lock);
      nodeName = lock.nodes.root.inputs.flake-compat;
      inherit (lock.nodes.${nodeName}.locked) narHash rev url;
    in
    builtins.fetchTarball {
      url = "${url}/archive/${rev}.tar.gz";
      sha256 = narHash;
    }
  )
  { src = ./.; }
).defaultNix
```

If you would like a `shell.nix` file, create one containing the above, replacing `defaultNix` with `shellNix`.

You can access any flake output via the `outputs` attribute returned by `flake-compat`, e.g.

```nix
(import ... { src = ./.; }).outputs.packages.x86_64-linux.default
```
