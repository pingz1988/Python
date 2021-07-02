#!/bin/sh

PWD=`pwd`
DIR=/home/MPMS/
NAME=upload
TARGET=$DIR$NAME

while true
do
    exsit=false
    lines=$(pgrep -a $NAME | awk '{print $2}')
    for line in $lines
    do
        if [ $line == $TARGET ]
        then
            exsit=true
        fi
    done

    if [ $exsit = false ]
    then
        echo "--- Starting [upload]..."
        #cd $DIR
        #./$NAME
        $TARGET
        cd ${PWD}
    fi
    
    sleep 10
done