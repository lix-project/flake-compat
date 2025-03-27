from pathlib import Path

from tests.testlib import (
    copy_fixture,
    flake_compat_arg,
    nix,
    nix_eval_flake_attr,
    nix_eval_flake_compat,
)


# May fail randomly on older Lixes and CppNixes due to: https://git.lix.systems/lix-project/lix/issues/750
def test_file_input(tmpdir: Path):
    copy_fixture("file_input", tmpdir)
    compat = nix_eval_flake_compat(tmpdir, "lix-manifest")
    native = nix_eval_flake_attr(tmpdir, "lix-manifest")

    assert native == compat


# Check that the file input is not a derivation, in spite of our use of
# derivations internally.
def test_file_input_not_derivation(tmpdir: Path):
    copy_fixture("file_input", tmpdir)
    compat = nix_eval_flake_compat(tmpdir, "dependent")
    native = nix_eval_flake_attr(tmpdir, "dependent")

    assert native == compat


def test_native_fetchTree(tmpdir: Path):
    copy_fixture("file_input", tmpdir)

    # Make builtins.fetchTree print something visible when it is actually used.
    def do_eval(*args):
        res = nix(
            "eval",
            "--json",
            *flake_compat_arg,
            *args,
            "--impure",
            "--expr",
            """
            let
              scope = {
                builtins = builtins // {
                  fetchTree = x: builtins.trace "meow kitty" (builtins.fetchTree x);
                };
                import = builtins.scopedImport scope;
              };
            in builtins.scopedImport scope ./default.nix
            """,
            "lix-manifest",
            work_dir=tmpdir,
            capture_stderr=True,
        )

        res.ok()
        return res

    res = do_eval()
    assert b"meow kitty" not in res.proc.stderr

    res = do_eval("--arg", "useBuiltinsFetchTree", "true")
    assert b"meow kitty" in res.proc.stderr
