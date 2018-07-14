import fire
import inspect
import subprocess
import pprint
import requests
import os
import shutil
import logging
import config as cf

# init logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=cf.LOG_FILE,
    filemode='a',
)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logging.getLogger('').addHandler(ch)


def download_apk(url, dst):
    logging.info('start download: ' + url)
    res = requests.get(url)
    res.raise_for_status()
    apk_file = open(dst, 'wb')
    for chunk in res.iter_content(100000):
        apk_file.write(chunk)
    apk_file.close()
    logging.info('download finished')


def desc_func():
    func_name = inspect.stack()[1][3]
    print('call function: {}'.format(func_name))
    return func_name


class ADB(object):
    def __init__(self, device_id=None):
        adb_exec = ['adb']
        if device_id:
            adb_exec += ['-s', device_id]
        self.adb_exec = adb_exec

    def __call__(self, *args, **_):
        exec_cmd = [*self.adb_exec, *args]
        completed_process = subprocess.run(exec_cmd, stdout=subprocess.PIPE)
        exec_result = completed_process.stdout
        exec_err = completed_process.stderr
        if exec_err:
            raise RuntimeError(exec_err.decode())
        logging.debug('{} => {}'.format(exec_cmd, exec_result))
        return exec_result.decode()

    def shell(self, *args, **_):
        exec_cmd = [*self.adb_exec, 'shell', *args]
        completed_process = subprocess.run(exec_cmd, stdout=subprocess.PIPE)
        exec_result = completed_process.stdout
        exec_err = completed_process.stderr
        if exec_err:
            raise RuntimeError(exec_err.decode())
        logging.debug('{} => {}'.format(exec_cmd, exec_result))
        return exec_result.decode()


class Device(object):
    def __init__(self, device_id):
        self.device_id = device_id
        self.adb = ADB(device_id)
        self.status = self.is_connected(device_id)

    def __repr__(self):
        return 'Device <id={} connected={}>'.format(self.device_id, self.status)

    def is_connected(self, device_id):
        adb_devices_result = self.adb('devices')
        result = [i for i in adb_devices_result.split('\n') if device_id in i and 'device' in i]
        logging.debug('Device {} is {}.'.format(
            device_id,
            'connected' if result else 'disconnected'
        ))
        return bool(result)


class DeviceHandler(object):
    device_dict = dict()
    action_dict = {
        'airplane_on': [
            ['settings', 'put', 'global', 'airplane_mode_on', '1'],
            ['am', 'broadcast', '-a', 'android.intent.action.AIRPLANE_MODE', '--ez', 'state', 'true']],
        'airplane_off': [
            ['settings', 'put', 'global', 'airplane_mode_on', '0'],
            ['am', 'broadcast', '-a', 'android.intent.action.AIRPLANE_MODE', '--ez', 'state', 'false']],
        'wifi_on': [
            ['svc', 'wifi', 'enable'],
        ],
        'wifi_off': [
            ['svc', 'wifi', 'disable'],
        ],
    }

    def __init__(self):
        raise NotImplementedError('DeviceHandler is single-instance')

    @classmethod
    def update_device_status(cls):
        adb_devices_result = ADB()('devices')
        device_list = [i.split('\t') for i in adb_devices_result.split('\n') if '\t' in i and 'device' in i]
        for each_device in device_list:
            each_device_id = each_device[0]
            cls.device_dict[each_device_id] = Device(each_device_id)
        logging.info('now devices: \n{}'.format(pprint.saferepr(cls.device_dict)))
        return cls.device_dict

    @classmethod
    def check_connect(cls, device_list):
        cls.update_device_status()
        for each_device in device_list:
            if each_device not in cls.device_dict:
                logging.warning('Device {} disconnected.'.format(each_device))
                device_list.remove(each_device)
        return device_list

    @classmethod
    def apply_cmd(cls, device_list, *cmd, shell=None):
        for each_device_id in device_list:
            each_device = cls.device_dict[each_device_id]
            if shell:
                each_device.adb.shell(*cmd)
            else:
                each_device.adb(*cmd)

    @classmethod
    def install(cls, device_list, apk_src):
        device_list = cls.check_connect(device_list)
        dst_apk_path = os.path.join(cf.WORKSPACE_DIR, 'temp.apk')
        if apk_src.startswith('http'):
            download_apk(apk_src, dst_apk_path)
        else:
            shutil.copyfile(apk_src, dst_apk_path)
        cls.apply_cmd(device_list, 'install', '-r', '-d', dst_apk_path)

    @classmethod
    def uninstall(cls, device_list, package_name):
        device_list = cls.check_connect(device_list)
        cls.apply_cmd(device_list, 'uninstall', package_name)

    @classmethod
    def setting(cls, device_list, action):
        device_list = cls.check_connect(device_list)
        if action not in cls.action_dict:
            raise NotImplementedError('action {} not supported yet'.format(action))
        cmd_list = cls.action_dict[action]
        for each_cmd in cmd_list:
            cls.apply_cmd(device_list, *each_cmd, shell=True)

    @classmethod
    def screenshot(cls, device_list, dst_dir):
        device_list = cls.check_connect(device_list)
        for each_device_id in device_list:
            temp_pic_path = '/sdcard/{}.png'.format(each_device_id)
            shot_cmd = ['screencap', '-p', temp_pic_path]
            pull_cmd = ['pull', temp_pic_path, dst_dir]
            cls.apply_cmd([each_device_id, ], *shot_cmd, shell=True)
            cls.apply_cmd([each_device_id, ], *pull_cmd)


class CmdHandler(object):
    # 安装/删除/更新 软件
    def install(self, device, apk_src):
        device_list = device.split(',')
        if not apk_src.endswith('.apk'):
            raise ValueError('src should be apk: {}'.format(apk_src))
        DeviceHandler.install(device_list, apk_src)

    def uninstall(self, device, package_name):
        device_list = device.split(',')
        DeviceHandler.uninstall(device_list, package_name)

    # 修改设置
    def setting(self, device, action):
        device_list = device.split(',')
        DeviceHandler.setting(device_list, action)

    # 文件管理
    def upload(self):
        desc_func()
        raise NotImplementedError('this function still building.')

    def download(self):
        desc_func()
        raise NotImplementedError('this function still building.')

    # 截图
    def screenshot(self, device, dst):
        device_list = device.split(',')
        os.makedirs(dst, exist_ok=True)
        DeviceHandler.screenshot(device_list, dst)

    # 获取可用设备
    def get_devices(self):
        DeviceHandler.update_device_status()


if __name__ == '__main__':
    fire.Fire(CmdHandler)
