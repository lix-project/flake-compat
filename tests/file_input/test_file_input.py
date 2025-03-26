from pathlib import Path

from tests.testlib import copy_fixture, nix, nix_eval_flake_compat


# May fail randomly due to: https://git.lix.systems/lix-project/lix/issues/750
def test_file_input(tmpdir: Path):
    copy_fixture("file_input", tmpdir)
    compat = nix_eval_flake_compat(tmpdir, "lix-manifest")
    native = nix("eval", "--json", ".#lix-manifest", work_dir=tmpdir).json()

    assert native == compat
