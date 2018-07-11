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
python run.py --device <device_id> --install <url或者apk文件>
python run.py --device <device_id> --uninstall <url或者apk文件>
python run.py --device <device_id> --update <url或者apk文件>
```

### 修改设置

``` bash
python run.py --device <device_id> --setting airplane_on
python run.py --device <device_id> --setting airplane_off
python run.py --device <device_id> --setting wifi_on
python run.py --device <device_id> --setting wifi_off

... and so on
```

### 文件管理

``` bash
python run.py --device <device_id> --upload <src_path_in_pc>,<dst_path_in_android>
python run.py --device <device_id> --download <src_path_in_android>,<dst_path_in_pc>
```

### 截图

``` bash
python run.py --device <device_id> --screenshot <dst_path_in_pc>
```

## More

- 封装成桌面应用供用户使用
- 提供更加细致的操作方案（例如借助json、yaml）
- 需要有良好方便的插件化扩展能力，方便加新功能



