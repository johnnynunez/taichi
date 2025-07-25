# -*- coding: utf-8 -*-

# -- stdlib --
import os
import platform
import re
import shutil
import sys
from typing import Tuple

# -- third party --
# -- own --
from . import misc
from .dep import download_dep
from .misc import banner, get_cache_home, path_prepend, info
from .tinysh import Command, sh


# -- code --
def setup_miniforge(prefix):
    u = platform.uname()
    if (u.system, u.machine) == ("Linux", "x86_64"):
        url = "https://github.com/conda-forge/miniforge/releases/download/25.3.0-3/Miniforge3-25.3.0-3-Linux-x86_64.sh"
        download_dep(url, prefix, args=["-bfp", str(prefix)])
    elif (u.system, u.machine) in (("Linux", "arm64"), ("Linux", "aarch64")):
        url = "https://github.com/conda-forge/miniforge/releases/download/25.3.0-3/Miniforge3-25.3.0-3-Linux-aarch64.sh"
        download_dep(url, prefix, args=["-bfp", str(prefix)])
    elif (u.system, u.machine) == ("Darwin", "arm64"):
        url = "https://github.com/conda-forge/miniforge/releases/download/25.3.0-3/Miniforge3-25.3.0-3-MacOSX-arm64.sh"
        download_dep(url, prefix, args=["-bfp", str(prefix)])
    elif (u.system, u.machine) == ("Darwin", "x86_64"):
        url = "https://github.com/conda-forge/miniforge/releases/download/25.3.0-3/Miniforge3-25.3.0-3-MacOSX-x86_64.sh"
        download_dep(url, prefix, args=["-bfp", str(prefix)])
    elif u.system == "Windows":
        url = (
            "https://github.com/conda-forge/miniforge/releases/download/25.3.0-3/Miniforge3-25.3.0-3-Windows-x86_64.exe"
        )
        download_dep(
            url,
            prefix,
            args=[
                "/S",
                "/InstallationType=JustMe",
                "/RegisterPython=0",
                "/KeepPkgCache=0",
                "/AddToPath=0",
                "/NoRegistry=1",
                "/NoShortcut=1",
                "/NoScripts=1",
                "/CheckPathLength=1",
                f"/D={prefix}",
            ],
        )
    else:
        raise RuntimeError(f"Unsupported platform: {u.system} {u.machine}")


def get_desired_python_version() -> str:
    version = misc.options.python
    version = version or os.environ.get("PY", None)
    v = sys.version_info
    this_version = f"{v.major}.{v.minor}"

    if version in ("3.x", "3", None):
        assert v.major == 3
        return this_version
    elif version and re.match(r"^3\.\d+$", version):
        return version
    elif version in ("native", "Native"):
        return "(Native)"
    else:
        raise RuntimeError(f"Unsupported Python version: {version}")


@banner("Setup Python {version}")
def setup_python(version: str) -> Tuple[Command, Command]:
    """
    Find the required Python environment and return the `python` and `pip` commands.
    """
    if version == "(Native)":
        info("Using your current Python interpreter as requested.")
        python = sh.bake(sys.executable)
        pip = python.bake("-m", "pip")
        return python, pip

    windows = platform.system() == "Windows"

    prefix = get_cache_home() / "miniforge"
    setup_miniforge(prefix)

    if windows:
        conda_path = prefix / "Scripts" / "conda.exe"
    else:
        conda_path = prefix / "bin" / "conda"

    if not conda_path.exists():
        shutil.rmtree(prefix, ignore_errors=True)
        setup_miniforge(prefix)
        if not conda_path.exists():
            raise RuntimeError(f"Failed to setup miniforge at {prefix}")

    conda = sh.bake(str(conda_path))

    env = prefix / "envs" / version
    if windows:
        exe = env / "python.exe"
        paths = [
            env,
            env / "Library" / "mingw-w64" / "bin",
            env / "Library" / "usr" / "bin",
            env / "Library" / "bin",
            env / "Scripts",
            env / "bin",
            prefix / "condabin",
        ]
        path_prepend("PATH", *paths)
    else:
        exe = env / "bin" / "python"
        path_prepend("PATH", env / "bin", prefix / "condabin")

    if not exe.exists():
        conda.create("-y", "-n", version, f"python={version}")

    # For CMake
    os.environ["Python_ROOT_DIR"] = str(env)
    os.environ["Python2_ROOT_DIR"] = str(env)  # Align with setup-python@v4
    os.environ["Python3_ROOT_DIR"] = str(env)

    python = sh.bake(str(exe))
    pip = python.bake("-m", "pip")

    return python, pip
