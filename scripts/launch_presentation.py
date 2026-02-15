#!/usr/bin/env python3
"""Build payload and serve presentation pages locally."""

from __future__ import annotations

import argparse
import http.server
import socketserver
import subprocess
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build_payload() -> None:
    subprocess.run(["python3", "scripts/build_presentation_data.py"], cwd=ROOT, check=True)


def serve(port: int, open_browser: bool) -> None:
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        if open_browser:
            webbrowser.open(f"http://localhost:{port}/presentation/index.html")
        print(f"Serving from {ROOT}")
        print(f"Deck:  http://localhost:{port}/presentation/index.html")
        print(f"Paper: http://localhost:{port}/presentation/paper.html")
        print(f"Reg:   http://localhost:{port}/presentation/regulatory.html")
        print(f"Map:   http://localhost:{port}/presentation/portfolio_map.html")
        print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped presentation server.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and serve Costco presentation pages.")
    parser.add_argument("--port", type=int, default=8080, help="Local port (default: 8080)")
    parser.add_argument("--no-open", action="store_true", help="Do not auto-open browser")
    args = parser.parse_args()

    build_payload()
    serve(args.port, open_browser=not args.no_open)


if __name__ == "__main__":
    main()
