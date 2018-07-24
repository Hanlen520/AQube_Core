#!/bin/sh
# 同时按音量上下键
sendevent /dev/input/event0 1 114 1
sendevent /dev/input/event0 0 0 0
sendevent /dev/input/event0 1 115 1
sendevent /dev/input/event0 0 0 0
# 按住5s
sleep 5s
# 松开
sendevent /dev/input/event0 1 114 0
sendevent /dev/input/event0 0 0 0
sendevent /dev/input/event0 1 115 0
sendevent /dev/input/event0 0 0 0