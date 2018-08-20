import subprocess
import os

from .config import *
from .handler import DeviceHandler
from .utils import standard_print


# --- fire part ---
def format_device(device_list):
    # for some fire version, device list is not a list.
    if isinstance(device_list, str):
        return device_list.split(",")
    elif isinstance(device_list, (tuple, list)):
        return device_list
    else:
        raise TypeError("unexpected type: {}".format(device_list))


class CmdHandler(object):
    # 安装/删除/更新 软件
    def install(self, device, apk_src):
        device = format_device(device)
        if not apk_src.endswith(".apk"):
            raise ValueError("src should be apk: {}".format(apk_src))
        DeviceHandler.install(device, apk_src)

    def uninstall(self, device, package_name):
        device = format_device(device)
        DeviceHandler.uninstall(device, package_name)

    # 修改设置
    def setting(self, device, action):
        device = format_device(device)
        DeviceHandler.setting(device, action)

    # 文件管理
    def push(self, device, src, dst):
        device = format_device(device)
        if not os.path.exists(src):
            raise FileNotFoundError("no file found in: {}".format(src))
        DeviceHandler.push(device, src, dst)

    def pull(self, device, src, dst):
        device = format_device(device)
        # TODO should check if src exists?
        DeviceHandler.pull(device, src, dst)

    # 截图
    def screenshot(self, device, dst):
        device = format_device(device)
        os.makedirs(dst, exist_ok=True)
        DeviceHandler.screenshot(device, dst)

    # 获取可用设备
    def get_devices(self):
        result = DeviceHandler._update_device_status()
        standard_print(result)

    # 执行自定义adb命令
    def exec_cmd(self, device, cmd, shell):
        device = format_device(device)
        cmd_list = cmd.split(" ")
        DeviceHandler.exec_cmd(device, cmd_list, bool(shell))

    # 执行自定义shell脚本
    def exec_extend_shell(self, device, shell_name):
        device = format_device(device)
        if shell_name not in DeviceHandler.shell_dict:
            raise FileNotFoundError("no shell named {}".format(shell_name))
        DeviceHandler.exec_extend_shell(device, shell_name)

    # 与手机无关的部分
    def npm_install(self, project_dir):
        now_cwd = os.getcwd()
        os.chdir(project_dir)
        subprocess.run(['npm', 'install'], shell=True)
        os.chdir(now_cwd)

    def npm_build(self, project_dir, test=None):
        now_cwd = os.getcwd()
        os.chdir(project_dir)
        if test:
            subprocess.run(['npm', 'run', 'build:test'], shell=True)
        else:
            subprocess.run(['npm', 'run', 'build'], shell=True)
        os.chdir(now_cwd)
