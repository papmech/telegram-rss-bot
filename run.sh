#!/bin/sh
 
while :
do
    python3 telegram-rss-bot.py "$1" --interval 60 &
    TASK_PID=$!
    echo "Got TASK_PID = $TASK_PID"
    # Restart the bot every 30 minutes
    sleep 1800
    kill -9 $TASK_PID
done