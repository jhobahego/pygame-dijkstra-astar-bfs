"""Application entrypoint for Grid Chase."""

from game.app import App


def main() -> None:
    """Start the game application."""
    App().run()


if __name__ == "__main__":
    main()
