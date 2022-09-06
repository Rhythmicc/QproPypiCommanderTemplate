from QuickProject.Commander import Commander
from .__config__ import enable_config, QproPypiCommanderTemplateConfig

config: QproPypiCommanderTemplateConfig = None
if enable_config:
    config = QproPypiCommanderTemplateConfig()

app = Commander()


@app.command()
def hello(name: str):
    """
    echo Hello <name>

    :param name: str
    """
    print(f"Hello {name}!")


def main():
    """
    注册为全局命令时, 默认采用main函数作为命令入口, 请勿将此函数用作它途.
    When registering as a global command, default to main function as the command entry, do not use it as another way.
    """
    app()


if __name__ == '__main__':
    main()
