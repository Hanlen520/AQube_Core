# AndroidQube

> 一个能够批量对android设备进行操作的软件

## 使用场景

- 在多台设备连接到同一台电脑上时对他们进行批量操作。
- 保持多台设备的配置一致。
- 监控设备的连接状态。

## 设计

暂定使用python+Fire开发。

## 功能

设备id统一使用逗号隔开

### 安装/删除/更新 软件

``` bash
python run.py install --device 123456F --apk_src <url或者apk文件>
python run.py uninstall --device 123456F --package <包名>
```

### 修改设置

``` bash
python run.py setting --device 123456F --action airplane_on
python run.py setting --device 123456F --action airplane_off
python run.py setting --device 123456F --action wifi_on
python run.py setting --device 123456F --action wifi_off
```

### 文件管理

``` bash
python run.py upload --device 123456F --src <src_path_in_pc> --dst <dst_path_in_android>
python run.py download --device 123456F --src <src_path_in_android> --dst <dst_path_in_pc>
```

### 截图

``` bash
python run.py screenshot --dst <dst_path_in_pc> --device 123456F
```

### 获取可用设备

``` bash
python run.py get_devices
```

## More

- 封装成桌面应用供用户使用
- 提供更加细致的操作方案（例如借助json、yaml）
- 需要有良好方便的插件化扩展能力，方便加新功能



