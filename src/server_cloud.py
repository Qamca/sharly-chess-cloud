"""
Cloud/Docker entrypoint for Sharly Chess.

Bypasses the Toga GUI module so the server starts cleanly on headless systems
without requiring GTK or a display. All other behaviour is identical to the
normal startup path.
"""

import asyncio
import os
import sys
from pathlib import Path

# Ensure the src/ directory is on the path when running directly
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == '__main__':
    import argparse
    from dotenv import load_dotenv

    # Parse --path first (mirrors init_script()) to chdir before any module reads paths
    path_parser = argparse.ArgumentParser(add_help=False)
    path_parser.add_argument('--path', default=str(Path.cwd()))
    path_args, _ = path_parser.parse_known_args()
    os.chdir(path_args.path)
    load_dotenv()

    from web.server_engine import ServerEngine

    parser = argparse.ArgumentParser(description='Sharly Chess cloud server')
    parser.add_argument('-p', '--port', type=int, help='web server port', default=8080)
    parser.add_argument('--path', default=str(Path.cwd()), help='working directory')
    args = parser.parse_args()

    try:
        se = ServerEngine(port=args.port)
        asyncio.run(se.serve())
    except KeyboardInterrupt:
        pass
