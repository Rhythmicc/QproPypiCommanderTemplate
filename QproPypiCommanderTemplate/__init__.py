# -*- coding: utf-8 -*-

name = "QproPypiCommanderTemplate"

from .__config__ import *

config: QproPypiCommanderTemplateConfig = None
if enable_config:
    config = QproPypiCommanderTemplateConfig()

import sys
from QuickProject import user_pip, _ask


def external_exec(
    cmd: str,
    without_output: bool = False,
    without_stdout: bool = False,
    without_stderr: bool = False,
):
    """
    外部执行命令

    :param cmd: 命令
    :param without_output: 是否不输出
    :return: status code, output
    """
    # import threading
    from subprocess import Popen, PIPE
    from concurrent.futures import ThreadPoolExecutor, wait

    class MixContent:
        def __init__(self):
            self.content = ""

        def __add__(self, other):
            self.content += other
            return self

        def __str__(self):
            return self.content

    content = MixContent()

    def _output(pipe_name: str, process: Popen, content: MixContent):
        ignore_status = (
            without_stdout if pipe_name == "stdout" else without_stderr
        ) or without_output
        for line in iter(eval(f"process.{pipe_name}.readline"), ""):
            if not ignore_status:
                QproDefaultConsole.print(line.strip())
            content += line

    pool = ThreadPoolExecutor(2)
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, bufsize=1, encoding="utf-8")

    wait(
        [
            pool.submit(_output, "stdout", p, content),
            pool.submit(_output, "stderr", p, content),
        ]
    )
    pool.shutdown()
    ret_code = p.wait()

    return ret_code, str(content)


def requirePackage(
    pname: str,
    module: str = "",
    real_name: str = "",
    not_exit: bool = True,
    not_ask: bool = False,
    set_pip: str = user_pip,
):
    """
    获取本机上的python第三方库，如没有则询问安装

    :param not_ask: 不询问，无依赖项则报错
    :param set_pip: 设置pip路径
    :param pname: 库名
    :param module: 待引入的模块名，可缺省
    :param real_name: 用于 pip3 install 的名字
    :param not_exit: 安装后不退出
    :return: 库或模块的地址
    """
    try:
        exec(f"from {pname} import {module}" if module else f"import {pname}")
    except (ModuleNotFoundError, ImportError):
        if not_ask:
            return None
        if _ask(
            {
                "type": "confirm",
                "name": "install",
                "message": f"""{name} require {pname + (' -> ' + module if module else '')}, confirm to install?
  {name} 依赖 {pname + (' -> ' + module if module else '')}, 是否确认安装?""",
                "default": True,
            }
        ):
            with QproDefaultConsole.status(
                "Installing..." if user_lang != "zh" else "正在安装..."
            ):
                external_exec(
                    f"{set_pip} install {pname if not real_name else real_name} -U",
                    True,
                )
            if not_exit:
                exec(f"from {pname} import {module}" if module else f"import {pname}")
            else:
                QproDefaultConsole.print(
                    QproInfoString,
                    f'just run again: "{" ".join(sys.argv)}"'
                    if user_lang != "zh"
                    else f'请重新运行: "{" ".join(sys.argv)}"',
                )
                exit(0)
        else:
            exit(-1)
    finally:
        return eval(f"{module if module else pname}")
