import dataclasses
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

src = Path(__file__).parent.parent

flake_compat_arg = ("--arg", "flake-compat", str(src / "../default.nix"))


def copy_fixture(name: str, to: Path):
    print(f"copying {name} to {to}")
    shutil.copytree(src / name, to, dirs_exist_ok=True)


def format_nix_config(vals: dict[str, str]) -> str:
    return "\n".join(f"{name} = {value}" for (name, value) in vals.items())


@dataclasses.dataclass
class NixResult:
    proc: subprocess.CompletedProcess[bytes]

    def ok(self):
        self.proc.check_returncode()

    def json(self):
        return json.loads(self.proc.stdout)


def nix_eval_flake_compat(tmpdir: Path, attr: str, extra_args: list[str] = []) -> Any:
    return nix(
        "eval",
        "--show-trace",
        "--json",
        *flake_compat_arg,
        *extra_args,
        "-f",
        "default.nix",
        attr,
        work_dir=tmpdir,
    ).json()


def nix_eval_flake_attr(tmpdir: Path, attr: str, extra_args: list[str] = []) -> Any:
    return nix("eval", "--json", *extra_args, ".#" + attr, work_dir=tmpdir).json()


def nix(
    *args: str,
    work_dir: Path | None = None,
    command: str = "nix",
    experimental_features: set[str] = {"nix-command", "flakes"},
    capture_stderr: bool = False,
) -> NixResult:
    # FIXME(jade): maybe should copy or reference the lix functional2 test suite?
    config = {"experimental-features": " ".join(experimental_features)}
    new_env = os.environ.copy()
    new_env["NIX_CONFIG"] = (
        new_env.get("NIX_CONFIG", "") + "\n" + format_nix_config(config)
    )
    print(f"$ {command}", " ".join(args))

    stderr = subprocess.PIPE if capture_stderr else None
    res = NixResult(
        subprocess.run(
            [command] + list(args),
            env=new_env,
            cwd=work_dir,
            stdout=subprocess.PIPE,
            stderr=stderr,
        )
    )
    print(res.proc.stdout.decode())
    return res


def write_file(path: Path, content: str):
    with open(path, "w") as handle:
        handle.write(content)
