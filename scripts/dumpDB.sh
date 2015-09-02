#!/bin/bash

# Script will dump the current live Django database

TARGETDIR=../django_db
TARGETNAME=spedish_django.sql

if [ ! -d $TARGETDIR ] ; then
    mkdir $TARGETDIR
fi

mysqldump -h spedish.cgeej8k7vn8d.us-west-1.rds.amazonaws.com -P 3306 -u spedish_master -p spedish_django > $TARGETDIR/$TARGETNAME
