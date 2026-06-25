#!/bin/bash
DISPLAY=:0 nohup ./akvaarionapit.py &
echo $! > start_akvaarionapit.pid
