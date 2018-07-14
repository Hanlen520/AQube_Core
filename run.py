import fire
import logging
import inspect
import subprocess
import pprint
import requests
import os
import shutil
import config as cf

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s || %(levelname)s || %(message)s',
)


def download_apk(url, dst):
    res = requests.get(url)
    res.raise_for_status()
    apk_file = open(dst, 'wb')
    for chunk in res.iter_content(100000):
        apk_file.write(chunk)
    apk_file.close()


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

    def __call__(self, *args, **kwargs):
        exec_cmd = [*self.adb_exec, *args]
        exec_result = subprocess.run(exec_cmd, stdout=subprocess.PIPE).stdout
        logging.info('{} => {}'.format(exec_cmd, exec_result))
        return exec_result.decode()

    def shell(self, *args, **_):
        exec_cmd = [*self.adb_exec, 'shell', *args]
        exec_result = subprocess.run(exec_cmd, stdout=subprocess.PIPE).stdout
        logging.info('{} => {}'.format(exec_cmd, exec_result))
        return exec_result.decode()


class Device(object):
    def __init__(self, device_id):
        self.device_id = device_id
        self.adb = ADB(device_id)
        self.status = self.is_connected(device_id)

    def __repr__(self):
        return '< Device id={} connected={} >'.format(self.device_id, self.status)

    def is_connected(self, device_id):
        adb_devices_result = self.adb('devices')
        result = [i for i in adb_devices_result.split('\n') if device_id in i and 'device' in i]
        logging.info('Device {} is {}.'.format(
            device_id,
            'connected' if result else 'disconnected'
        ))
        return bool(result)


class DeviceHandler(object):
    device_dict = dict()

    @classmethod
    def update_device_status(cls):
        adb_devices_result = ADB()('devices')
        device_list = [i.split('\t') for i in adb_devices_result.split('\n') if '\t' in i and 'device' in i]
        for each_device in device_list:
            each_device_id = each_device[0]
            cls.device_dict[each_device_id] = Device(each_device_id)
        logging.info('now devices: \n{}'.format(pprint.saferepr(cls.device_dict)))

    @classmethod
    def check_connect(cls, device_list):
        cls.update_device_status()
        for each_device in device_list:
            if each_device not in cls.device_dict:
                logging.warning('Device {} disconnected.'.format(each_device))
                device_list.remove(each_device)
        return device_list

    @classmethod
    def apply_cmd(cls, device_list, *cmd):
        for each_device_id in device_list:
            each_device = cls.device_dict[each_device_id]
            each_device.adb(*cmd)

    @classmethod
    def install(cls, device_list, apk_src):
        device_list = cls.check_connect(device_list)
        dst_apk_path = os.path.join(cf.WORKSPACE_DIR, 'temp.apk')
        if apk_src.startswith('http'):
            download_apk(apk_src, dst_apk_path)
        else:
            shutil.copyfile(apk_src, dst_apk_path)
        cls.apply_cmd(device_list, 'install', dst_apk_path)


class CmdHandler(object):
    # 安装/删除/更新 软件
    def install(self, device, apk_src):
        device_list = device.split(',')
        if not apk_src.endswith('.apk'):
            raise ValueError('src should be apk: {}'.format(apk_src))
        DeviceHandler.install(device_list, apk_src)

    def uninstall(self, device, *args, **kwargs):
        desc_func()
        print(device, *args, **kwargs)

    def update(self, device, *args, **kwargs):
        desc_func()
        print(device, *args, **kwargs)

    # 修改设置
    def setting(self, device, operation):
        desc_func()
        print(device, operation)

    # 文件管理
    def upload(self, device, src, dst):
        desc_func()
        print(device, src, dst)

    # 截图
    def screenshot(self, device, dst):
        desc_func()
        print(device, dst)


if __name__ == '__main__':
    fire.Fire(CmdHandler)
    # Device(device_id='ZH7SPBVS99999999')
    # DeviceHandler.install(['ZH7SPBVS99999999',], '/Users/fengzhangchi/Downloads/ADBKeyBoard.apk')
