from pathlib import Path
import dataclasses
import subprocess
import shutil
import json
import os

src = Path(__file__).parent

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


def nix(
    *args: str,
    work_dir: Path | None = None,
    command: str = "nix",
    experimental_features: set[str] = {"nix-command", "flakes"},
) -> NixResult:
    # FIXME(jade): maybe should copy or reference the lix functional2 test suite?
    config = {"experimental-features": " ".join(experimental_features)}
    new_env = os.environ.copy()
    new_env["NIX_CONFIG"] = (
        new_env.get("NIX_CONFIG", "") + "\n" + format_nix_config(config)
    )
    print(f"$ {command}", " ".join(args))
    res = NixResult(
        subprocess.run(
            [command] + list(args), env=new_env, cwd=work_dir, stdout=subprocess.PIPE
        )
    )
    print(res.proc.stdout.decode())
    return res


def write_file(path: Path, content: str):
    with open(path, "w") as handle:
        handle.write(content)
