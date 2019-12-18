#!/bin/bash
 
while :
do
    git pull
    python3 telegram-rss-bot.py "$1" --interval 60 &
    TASK_PID=$!
    echo "Got TASK_PID = $TASK_PID"
    sleep 3600
    kill -9 $TASK_PID
done