# Chess PGN CLI

Export recent public Chess.com games to a `.pgn` file or copy them as plain text. This is an independent tool that uses the [Chess.com Published-Data API](https://www.chess.com/news/view/published-data-api).

## Install from source

Install Python 3.9 or newer and open a terminal in the project folder.

**Linux and macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
chess-pgn --help
```

**Windows PowerShell**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\chess-pgn.exe --help
```

In PowerShell, use `.\.venv\Scripts\chess-pgn.exe` in place of `chess-pgn` in the examples below.

## Usage

```sh
chess-pgn hikaru --copy
chess-pgn hikaru -n 5 --copy
chess-pgn hikaru -n 10 --output games.pgn
```

Replace `hikaru` with the Chess.com username you want to export. The default count is one. Games are ordered by finish time, most recent first. If fewer games have PGN records than requested, the tool exports those available and reports the count. The public archive may take time to show a recently finished game.

Choose `--copy` or `--output FILE` on each run. File output is UTF-8. An existing output file is replaced after the new export is ready.

## Clipboard setup

File output works anywhere the CLI can run. Clipboard output needs a working clipboard in the desktop session.

| System | Clipboard backend |
| --- | --- |
| Windows | Native Windows clipboard |
| macOS | System clipboard via `pbcopy` and `pbpaste` |
| Linux with Wayland, including Hyprland | `wl-clipboard` (`sudo pacman -S wl-clipboard` on Arch or `sudo apt install wl-clipboard` on Debian and Ubuntu) |
| Linux with X11 | `xclip` (`sudo pacman -S xclip` on Arch or `sudo apt install xclip` on Debian and Ubuntu) |

For SSH or a headless server, use `--output FILE`.

## Code layout

- `api.py` fetches archive JSON with `urllib.request` and picks the newest PGNs.
- `cli.py` parses arguments with `argparse` and sends the PGN to a file or to `pyperclip`.
- `pyproject.toml` declares the dependency and installs the `chess-pgn` command. An editable install (`-e .`) picks up changes to the Python source when you run the command again.
