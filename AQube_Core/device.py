"""
operation with android devices
"""

import subprocess
import logging
import json


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


__all__ = [
    'ADB',
    'Device',
]
