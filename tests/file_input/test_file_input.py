from pathlib import Path

from tests.testlib import copy_fixture, nix_eval_flake_attr, nix_eval_flake_compat


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
