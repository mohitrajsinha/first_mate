# ui.py — CLI interface

import argparse
import sys
from agent import run_agent, MODELS

BANNER = r"""
 _____ _          _     __  __       _
|  ___(_)_ __ ___| |_  |  \/  | __ _| |_ ___
| |_  | | '__/ __| __| | |\/| |/ _` | __/ _ \
|  _| | | |  \__ \ |_  | |  | | (_| | ||  __/
|_|   |_|_|  |___/\__| |_|  |_|\__,_|\__\___|

  🏴‍☠️  Open Source Maintainer's First Mate
  GitHub, powered by Coral SQL
"""

HELP = """
Commands:
  triage <owner/repo>
  release-notes <owner/repo> <YYYY-MM-DD>
  help
  quit
"""

def parse_command(line: str, model: str):
    parts = line.strip().split()
    if not parts:
        return

    cmd = parts[0]

    if cmd in ("help", "?"):
        print(HELP)

    elif cmd == "triage":
        if len(parts) != 2 or "/" not in parts[1]:
            print("Usage: triage <owner/repo>")
            return
        owner, repo = parts[1].split("/", 1)
        run_agent(
            f"Triage open issues for {owner}/{repo}. Find duplicates and suggest priority labels.",
            model=model
        )

    elif cmd == "release-notes":
        if len(parts) != 3 or "/" not in parts[1]:
            print("Usage: release-notes <owner/repo> <YYYY-MM-DD>")
            return
        owner, repo = parts[1].split("/", 1)
        run_agent(
            f"Draft release notes for {owner}/{repo} for all PRs merged since {parts[2]}.",
            model=model
        )

    elif cmd in ("quit", "exit", "q"):
        print("⚓ Fair winds! Goodbye.")
        sys.exit(0)

    else:
        print(f"❌ Unknown command '{cmd}'. Type 'help' for usage.")


def main():
    parser = argparse.ArgumentParser(description="First Mate — OSS agent powered by Coral SQL")
    parser.add_argument(
        "--model",
        default="gemini",
        choices=list(MODELS.keys()),
        help="LLM to use: gemini (default), gemini-pro"
    )
    parser.add_argument(
        "command", nargs="*",
        help="Optional: run a single command non-interactively"
    )
    args = parser.parse_args()

    print(BANNER)
    print(f"  Model : {args.model}   |   Type 'help' for commands\n")

    if args.command:
        parse_command(" ".join(args.command), args.model)
        return

    while True:
        try:
            line = input("first-mate> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n⚓ Fair winds! Goodbye.")
            break
        if line:
            parse_command(line, args.model)


if __name__ == "__main__":
    main()