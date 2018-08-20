"""
tools
"""
from .config import *

import json
import requests
import logging
import os
import pprint


def standard_print(output_content, need_pack=None):
    """
    统一使用json格式输出

    :param output_content:
    :param need_pack:
    :return:
    """
    if need_pack:
        final_output = json.dumps({"result": output_content})
    else:
        final_output = str(output_content)
    print(final_output)
    return final_output


def load_extend_shell():
    """
    读取extend文件夹下的shell脚本

    :return: shell list
    """
    if not os.path.exists(EXTEND_DIR):
        logging.warning("no extend directory found")
        return dict()
    shell_dict = {
        each_shell_name: os.path.join(EXTEND_DIR, each_shell_name)
        for each_shell_name in os.listdir(EXTEND_DIR)
        if each_shell_name.endswith(".sh")
    }
    logging.debug("extend shell: \n{}".format(pprint.saferepr(shell_dict)))
    return shell_dict


def download_apk(url, dst):
    """
    Download file and save it to dst path

    :param url: target url
    :param dst: dst path
    :return:
    """
    logging.debug("start download: " + url)
    res = requests.get(url)
    res.raise_for_status()
    apk_file = open(dst, "wb")
    for chunk in res.iter_content(100000):
        apk_file.write(chunk)
    apk_file.close()
    logging.debug("download finished")
