from dge_ausgabeapp.cli import main


def run() -> None:
    main(auto_envvar_prefix="DGE")


if __name__ == "__main__":
    run()
