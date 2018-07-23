#!/bin/sh
sendevent /dev/input/event0 1 114 1
sendevent /dev/input/event0 0 0 0

sendevent /dev/input/event0 1 115 1
sendevent /dev/input/event0 0 0 0

sleep 5s

sendevent /dev/input/event0 1 114 0
sendevent /dev/input/event0 0 0 0

sendevent /dev/input/event0 1 115 0
sendevent /dev/input/event0 0 0 0
