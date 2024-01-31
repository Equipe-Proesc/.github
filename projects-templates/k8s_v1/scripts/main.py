from lib import start
from lib.app import app
from lib.config import app_name


def main() -> None:
    start()
    app(prog_name=app_name)


if __name__ == "__main__":
    main()
