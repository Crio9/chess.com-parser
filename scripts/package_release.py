import argparse
import subprocess
import tarfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def main() -> None:
    parser = argparse.ArgumentParser(description="Check and archive a standalone build.")
    parser.add_argument(
        "target", choices=("windows-x64", "linux-x64", "macos-arm64", "macos-x64")
    )
    target = parser.parse_args().target

    windows = target == "windows-x64"
    executable = Path("dist") / ("chess-pgn.exe" if windows else "chess-pgn")
    subprocess.run([str(executable.resolve()), "--help"], check=True, timeout=30)

    release_dir = Path("release")
    release_dir.mkdir(exist_ok=True)
    asset = release_dir / f"chess-pgn-{target}"
    if windows:
        with ZipFile(asset.with_suffix(".zip"), "w", ZIP_DEFLATED) as archive:
            archive.write(executable, arcname=executable.name)
    else:
        with tarfile.open(asset.with_suffix(".tar.gz"), "w:gz") as archive:
            archive.add(executable, arcname=executable.name)


if __name__ == "__main__":
    main()
