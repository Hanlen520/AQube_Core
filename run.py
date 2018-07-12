import fire
import inspect


def desc_func():
    func_name = inspect.stack()[1][3]
    print('call function: {}'.format(func_name))
    return func_name


class DeviceHandler(object):
    pass


class CmdHandler(object):
    # 安装/删除/更新 软件
    def install(self, device, *args, **kwargs):
        desc_func()
        print(device, *args, **kwargs)

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
