import subprocess
import pprint
import requests
import os
import shutil
import logging
import functools
import json
from pythonjsonlogger import jsonlogger


# --- pc ---
PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
WORKSPACE_DIR = os.path.join(PROJECT_DIR, 'workspace')
EXTEND_DIR = os.path.join(PROJECT_DIR, 'extend')
LOG_FILE = os.path.join(PROJECT_DIR, 'qube.log')

# --- phone ---
TEMP_SHELL_DIR = '/data/local/tmp'

if not os.path.exists(WORKSPACE_DIR):
    os.makedirs(WORKSPACE_DIR, exist_ok=True)


# init logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=LOG_FILE,
    filemode="a",
)

ch = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
ch.setFormatter(formatter)
ch.setLevel(logging.INFO)

logging.getLogger("").addHandler(ch)


# --- standard print ---
# 统一使用json格式输出
def standard_print(output_content, need_pack=None):
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


class ADB(object):
    def __init__(self, device_id=None):
        adb_exec = ["adb", ]
        if device_id:
            adb_exec += ["-s", device_id]
        self.adb_exec = adb_exec
        logging.debug("adb exec: {}".format(self.adb_exec))

    def __call__(self, *args, **_):
        """
        pure adb command

        :param args:
        :param _:
        :return:
        """
        exec_cmd = [*self.adb_exec, *args]
        completed_process = subprocess.run(exec_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        exec_result = completed_process.stdout
        exec_err = completed_process.stderr
        if exec_err:
            raise RuntimeError(exec_err.decode())
        logging.debug("{} => {}".format(exec_cmd, exec_result))
        return exec_result.decode()

    def shell(self, *args, **_):
        """
        pure adb shell command

        :param args:
        :param _:
        :return:
        """
        exec_cmd = [*self.adb_exec, "shell", *args]
        completed_process = subprocess.run(exec_cmd, stdout=subprocess.PIPE)
        exec_result = completed_process.stdout
        exec_err = completed_process.stderr
        if exec_err:
            raise RuntimeError(exec_err.decode())
        logging.debug("{} => {}".format(exec_cmd, exec_result))
        return exec_result.decode()


class Device(object):
    def __init__(self, device_id):
        self.device_id = device_id
        self.adb = ADB(device_id)
        self.status = self.is_connected(device_id)

    def __repr__(self):
        return json.dumps({
            "device_id": self.device_id,
            "status": self.status
        })

    __str__ = __repr__

    def is_connected(self, device_id):
        """
        check if your device connected

        :param device_id:
        :return: bool
        """
        adb_devices_result = self.adb("devices")
        result = [i for i in adb_devices_result.split("\n") if device_id in i and "device" in i]
        logging.debug("Device {} is {}.".format(
            device_id,
            "connected" if result else "disconnected"
        ))
        return bool(result)


def action_wrapper(func):
    @functools.wraps(func)
    def wrap(cls, device_list, *args, **kwargs):
        device_list = cls._filter_device_list(device_list)
        exec_result = func(cls, device_list, *args, **kwargs)
        standard_print(exec_result, need_pack=True)
        return exec_result
    return wrap


class DeviceHandler(object):
    device_dict = dict()
    shell_dict = load_extend_shell()
    action_dict = {
        "airplane_on": [
            ["settings", "put", "global", "airplane_mode_on", "1"],
            ["am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "true"]],
        "airplane_off": [
            ["settings", "put", "global", "airplane_mode_on", "0"],
            ["am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE", "--ez", "state", "false"]],
        "wifi_on": [
            ["svc", "wifi", "enable"],
        ],
        "wifi_off": [
            ["svc", "wifi", "disable"],
        ],
    }

    def __init__(self):
        raise NotImplementedError("DeviceHandler is single-instance")

    @classmethod
    def _filter_device_list(cls, old_device_list):
        """
        检查传入的设备列表并过滤
        结果如果为空（没有交集），抛出异常

        :param old_device_list:
        :return new_device_list:
        """
        new_device_list = cls._check_connect(old_device_list)
        if not new_device_list:
            raise ValueError("all devices disconnected")
        return new_device_list

    @classmethod
    def _update_device_status(cls):
        """
        更新设备状态，返回当前可用的设备字典

        :return: 当前设备字典
        """
        adb_devices_result = ADB()("devices")
        device_list = [i.split("\t") for i in adb_devices_result.split("\n") if "\t" in i and "device" in i]
        for each_device in device_list:
            each_device_id = each_device[0]
            cls.device_dict[each_device_id] = Device(each_device_id)
        logging.debug("now devices: \n{}".format(pprint.saferepr(cls.device_dict)))
        return cls.device_dict

    @classmethod
    def _check_connect(cls, device_list):
        """
        检查列表内机器的连接状态，并返回过滤后可用的设备列表

        :param device_list:
        :return:
        """
        cls._update_device_status()
        device_list = list(device_list)
        for each_device in device_list:
            if each_device not in cls.device_dict:
                logging.warning("Device {} disconnected.".format(each_device))
                device_list.remove(each_device)
        return device_list

    @classmethod
    def _apply_cmd(cls, device_list, *cmd, shell=None):
        """
        对device_list批量执行cmd

        :param device_list:
        :param cmd:
        :param shell:
        :return:
        """
        result_list = list()
        for each_device_id in device_list:
            each_device = cls.device_dict[each_device_id]
            if shell:
                each_result = each_device.adb.shell(*cmd)
            else:
                each_result = each_device.adb(*cmd)
            result_list.append(each_result)
        return result_list

    # --- 以下为暴露出来的方法 ---

    @classmethod
    @action_wrapper
    def install(cls, device_list, apk_src):
        """
        安装应用

        :param device_list: 目标设备列表
        :param apk_src: apk源，可以是url或者本地文件
        :return:
        """
        device_list = cls._filter_device_list(device_list)
        dst_apk_path = os.path.join(WORKSPACE_DIR, "temp.apk")
        if apk_src.startswith("http"):
            download_apk(apk_src, dst_apk_path)
        else:
            shutil.copyfile(apk_src, dst_apk_path)
        exec_result = cls._apply_cmd(device_list, "install", "-r", "-d", "-t", dst_apk_path)
        logging.debug(exec_result)
        return exec_result

    @classmethod
    @action_wrapper
    def uninstall(cls, device_list, package_name):
        """
        卸载应用

        :param device_list: 目标设备列表
        :param package_name: 目标包名
        :return:
        """
        device_list = cls._filter_device_list(device_list)
        return cls._apply_cmd(device_list, "uninstall", package_name)


    @classmethod
    @action_wrapper
    def setting(cls, device_list, action):
        """
        修改设置

        :param device_list: 目标设备列表
        :param action: 目标动作，关联 cls.action_dict
        :return:
        """
        device_list = cls._filter_device_list(device_list)
        if action not in cls.action_dict:
            raise NotImplementedError("action {} not supported yet".format(action))
        cmd_list = cls.action_dict[action]
        for each_cmd in cmd_list:
            cls._apply_cmd(device_list, *each_cmd, shell=True)
        return True

    @classmethod
    @action_wrapper
    def screenshot(cls, device_list, dst_dir):
        """
        截图并保存到指定位置

        :param device_list: 目标设备列表
        :param dst_dir: 目标文件夹（PC）
        :return:
        """
        device_list = cls._filter_device_list(device_list)
        for each_device_id in device_list:
            temp_pic_path = "/sdcard/{}.png".format(each_device_id)
            shot_cmd = ["screencap", "-p", temp_pic_path]
            pull_cmd = ["pull", temp_pic_path, dst_dir]
            cls._apply_cmd([each_device_id, ], *shot_cmd, shell=True)
            cls._apply_cmd([each_device_id, ], *pull_cmd)
        return True

    @classmethod
    @action_wrapper
    def push(cls, device_list, src, dst):
        """
        类比adb的push

        :param device_list:
        :param src:
        :param dst:
        :return:
        """
        # TODO windows路径有问题
        device_list = cls._filter_device_list(device_list)
        push_cmd = ["push", src, dst]
        return cls._apply_cmd(device_list, *push_cmd, shell=False)

    @classmethod
    @action_wrapper
    def pull(cls, device_list, src, dst):
        """
        类比adb的pull

        :param device_list:
        :param src:
        :param dst:
        :return:
        """
        device_list = cls._filter_device_list(device_list)
        pull_cmd = ["pull", src, dst]
        return cls._apply_cmd(device_list, *pull_cmd, shell=False)

    @classmethod
    @action_wrapper
    def exec_cmd(cls, device_list, cmd_list, on_shell):
        """
        执行自定义adb命令

        :param device_list: 目标设备列表
        :param cmd_list: cmd命令
        :param on_shell: 是否由shell执行
        :return:
        """
        device_list = cls._filter_device_list(device_list)
        return cls._apply_cmd(device_list, *cmd_list, shell=on_shell)

    @classmethod
    @action_wrapper
    def exec_extend_shell(cls, device_list, shell_name):
        """
        运行放置在extend文件夹下的shell脚本

        :param device_list:
        :param shell_name:
        :return:
        """
        cls.push(device_list, cls.shell_dict[shell_name], TEMP_SHELL_DIR)
        current_shell_path = TEMP_SHELL_DIR + "/" + shell_name
        cls.exec_cmd(device_list, ["chmod", "777", current_shell_path], on_shell=True)
        cls.exec_cmd(device_list, ["sh", current_shell_path], on_shell=True)
        return True


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
