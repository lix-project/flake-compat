{
  inputs.lix-manifest = {
    type = "file";
    # I can't get a file URL to work, idk, probably a bug in flakes lol
    # This was chosen since it's a tiny file that is likely to remain there
    # immutable ~forever
    url = "https://releases.lix.systems/lix/lix-2.90.0/manifest.nix";
    flake = false;
  };
  outputs =
    { lix-manifest, ... }:
    {
      inherit lix-manifest;
    };
}
