#!/bin/bash
DISPLAY=:0 ./akvaarionapit2.py > akvaarionapit.log 2>&1 &
echo $! > start_akvaarionapit.pid
