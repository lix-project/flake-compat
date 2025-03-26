from pathlib import Path

from tests.testlib import copy_fixture, nix_eval_flake_attr, nix_eval_flake_compat

# FIXME(jade): this is misssing a whole bunch of attrs due to bugs with
# lockless flakes https://git.lix.systems/lix-project/flake-compat/issues/71
ATTRS_TO_VALIDATE = {"notOutPath", "dotSlashDot"}

cleanup_self = [
    "--apply",
    'x: builtins.removeAttrs x [ "outPath" "self" ] // { notOutPath = x.outPath; }',
]


def test_copy_to_store_equivalent(tmpdir: Path):
    copy_fixture("fixtures/lockless_self", tmpdir)

    compat = nix_eval_flake_compat(tmpdir, "self", cleanup_self)
    not_compat = nix_eval_flake_attr(tmpdir, "self", cleanup_self)

    assert compat["dotSlashDot"].startswith("/nix/store")

    for attr in ATTRS_TO_VALIDATE:
        assert compat[attr] == not_compat[attr], f"Mismatch in attr {attr}"


def test_no_copy_to_store(tmpdir: Path):
    copy_fixture("fixtures/lockless_self", tmpdir)

    compat = nix_eval_flake_compat(
        tmpdir,
        "self.outPath",
        [
            # This string coercion doesn't copy to the store, unlike "${foo}"
            # or the one done by --json itself
            "--apply",
            "toString",
            "--arg",
            "copySourceTreeToStore",
            "false",
        ],
    )

    assert not compat.startswith("/nix/store")

    compat = nix_eval_flake_compat(
        tmpdir,
        "self.dotSlashDot",
        [
            "--arg",
            "copySourceTreeToStore",
            "false",
        ],
    )
    assert not compat.startswith("/nix/store")
