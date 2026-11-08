import argparse
import re
import sys
from pathlib import Path
from subprocess import SubprocessError
from tempfile import NamedTemporaryFile

import pyperclip

from .api import latest_pgns


def _copy_pgn(pgn: str) -> None:
    try:
        pyperclip.copy(pgn)
        copied = pyperclip.paste()
    except (pyperclip.PyperclipException, OSError, SubprocessError, UnicodeError) as error:
        raise RuntimeError(
            "Could not access the clipboard. Check the desktop setup or use --output FILE."
        ) from error

    # Some clipboard backends return without raising when the copy fails.
    if copied.replace("\r\n", "\n") != pgn.replace("\r\n", "\n"):
        raise RuntimeError("Could not verify the clipboard copy. Use --output FILE.")


def _save_pgn(path: Path, pgn: str) -> None:
    temporary = NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=path.parent,
        prefix=".chess-pgn-",
        delete=False,
    )
    temporary_path = Path(temporary.name)
    try:
        with temporary:
            temporary.write(pgn)
        # Close before replacing so this works on Windows too.
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export recent Chess.com games as PGN.")
    parser.add_argument("username", help="Chess.com username")
    parser.add_argument(
        "-n", "--count", type=int, default=1, help="number of games (default: 1)"
    )
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--copy", action="store_true", help="copy PGN to the clipboard")
    destination.add_argument(
        "-o", "--output", type=Path, metavar="FILE", help="save PGN to a file"
    )
    args = parser.parse_args()

    username = args.username.strip().lower()
    if not re.fullmatch(r"[a-z0-9_-]+", username):
        parser.error("enter a Chess.com username")
    if args.count < 1:
        parser.error("--count must be a positive integer")

    try:
        games = latest_pgns(username, args.count)
        if not games:
            raise RuntimeError(f"No games with PGN found in the archive for {username}.")

        pgn = "\n\n".join(games) + "\n"
        if args.copy:
            _copy_pgn(pgn)
            target = "the clipboard"
        else:
            path = args.output.expanduser()
            _save_pgn(path, pgn)
            target = str(path)
    except (OSError, RuntimeError) as error:
        print(f"{parser.prog}: {error}", file=sys.stderr)
        return 1

    print(f"Exported {len(games)}/{args.count} games to {target}.")
    return 0
