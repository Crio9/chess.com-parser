import json
from http.client import HTTPException
from urllib.error import HTTPError
from urllib.request import Request, urlopen


API_ROOT = "https://api.chess.com/pub/player"


def _fetch_list(url: str, field: str, username: str) -> list:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": f"chess-pgn-cli (Chess.com user {username})",
        },
    )
    try:
        with urlopen(request, timeout=20) as response:
            data = json.load(response)
    except HTTPError as error:
        messages = {
            404: "Chess.com could not find the player or archive. Check the username.",
            429: "Chess.com rate-limited the request. Try again later.",
        }
        message = messages.get(error.code, f"Chess.com returned HTTP {error.code}.")
        raise RuntimeError(message) from error
    except (OSError, HTTPException) as error:
        raise RuntimeError(f"Could not reach the Chess.com archive ({error}).") from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise RuntimeError("Chess.com returned invalid JSON.") from error

    if not isinstance(data, dict) or not isinstance(data.get(field), list):
        raise RuntimeError(f"The Chess.com response has no {field!r} list.")
    return data[field]


def latest_pgns(username: str, count: int) -> list[str]:
    months = _fetch_list(f"{API_ROOT}/{username}/games/archives", "archives", username)
    selected = []

    # Chess.com lists archives oldest first, grouped by game end month.
    for month_url in reversed(months):
        dated_pgns = []
        for game in _fetch_list(month_url, "games", username):
            pgn = game.get("pgn")
            if not isinstance(pgn, str) or not pgn.strip():
                continue
            end_time = game.get("end_time")
            if not isinstance(end_time, int):
                raise RuntimeError("Chess.com returned a PGN without a valid end time.")
            dated_pgns.append((end_time, pgn.strip()))

        dated_pgns.sort(key=lambda game: game[0], reverse=True)
        remaining = count - len(selected)
        selected.extend(pgn for _, pgn in dated_pgns[:remaining])
        if len(selected) == count:
            break

    return selected
