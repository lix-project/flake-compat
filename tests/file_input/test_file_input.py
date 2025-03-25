from pathlib import Path
from tests.testlib import copy_fixture, nix, flake_compat_arg


# May fail randomly due to: https://git.lix.systems/lix-project/lix/issues/750
def test_file_input(tmpdir: Path):
    copy_fixture("file_input", tmpdir)
    compat = nix(
        "eval",
        "--json",
        *flake_compat_arg,
        "-f",
        "default.nix",
        "lix-manifest",
        work_dir=tmpdir,
    ).json()
    native = nix("eval", "--json", ".#lix-manifest", work_dir=tmpdir).json()

    assert native == compat
