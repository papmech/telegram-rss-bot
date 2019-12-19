#!/bin/sh
 
while :
do
    if [ $# -eq 1 ]
    then
        python3 telegram-rss-bot.py "$1" --interval 60 &
    elif [ $# -eq 2 ]
    then
        python3 telegram-rss-bot.py "$1" --interval 60 --seendb "$2" &
    else
        echo "USAGE: run.sh <BOT_TOKEN>"
        echo "USAGE: run.sh <BOT_TOKEN> <SQLITE_DB_FILE>"
        exit 1
    fi
    TASK_PID=$!
    echo "Got TASK_PID = $TASK_PID"
    # Restart the bot every 30 minutes
    sleep 1800
    kill -9 $TASK_PID
done