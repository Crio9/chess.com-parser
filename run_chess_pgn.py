import os
import ssl

import certifi

from chess_pgn.cli import main


if __name__ == "__main__":
    # The build machine's OpenSSL certificate file may be absent on the target.
    if ssl.get_default_verify_paths().cafile is None:
        os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    raise SystemExit(main())
