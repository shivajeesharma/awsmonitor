#!/usr/bin/env python

# ***************************************************************************************************** #
# Author: Shivajee.R.Sharma <shivajee.sharma@gmail.com>                                                 #
# License: Apache                                                                                       #
#                                                                                                       #
# This program is used for monitoring AWS instances, the program stops/terminates aws instances based   #
# instance tag values. By changing the dryrun value to False, the user of this program completely owns  #
# the responsibility of the consequences arising out of it.                                             #
#                                                                                                       #
# This script depends on boto3, pytz and aws-cli pip packages                                           #
# This program is tested on Ubuntu 16.04, please refere to relevant os guide to setup the packages      #
# On Ubuntu 16.04                                                                                       #
# $ sudo apt install python-pip                                                                         #
# $ sudo pip install --upgrade pip                                                                      #
# $ sudo pip install --upgrade awscli                                                                   #
# $ sudo pip install --upgrade boto3                                                                    #
# $ sudo pip install --upgrade pytz                                                                     #
#                                                                                                       #
# Note: Create an IAM user on your AWS Console and note down the AccessID and Access Key                #
# $ aws configure                                                                                       #
# AWS Access Key ID: <enter your IAM user Access Key here>                                              #
# AWS Secret Access Key:<enter your IAM user Secret Access Key here>                                    #
# Default region name: <Enter your default region Name>                                                 #
# Default output format: json                                                                           #
#                                                                                                       #
# Check if everything is configured properly                                                            #
# $ aws ec2 describe-instances                                                                          #
# list of aws instances and their properties                                                            #
#                                                                                                       #
# Copy this program in your home folder and execute                                                     #
# $ python awsmonitor.py                                                                                #
#                                                                                                       #
# For the script to function you will have to add tags to your instances valid tags are                 #
# Key           Values                                                                                  #
# Shutdown      daily HH:MM or DD-MMM-YYYY HH:MM                                                        #
# Destroy       DD-MMM-YYYY HH:MM                                                                       #
#                                                                                                       #
# For Eg:                                                                                               #
# Shutdown      daily 18:00  will check and stop the machine daily at 6 PM IST or                         #
# Shutdown      03-Nov-2017 18:00  will check and stop the machine on 3 Nov 2017 at 6 PM IST            #
# Destroy       03-Nov-2017 18:00  will check and terminate the machine on 3 Nov 2017 at 6 PM IST       #
#                                                                                                       #
# An instance can have bot shutdown as well as Destroy tags                                             #
# Please note time is hardcoded in IST time zone, also the variable dryrun must be set to false for     #
# the script to actually perform the action                                                             #
# the script can be easily added to crontab for repeated execution                                      #
# ***************************************************************************************************** #


import sys
import boto3 
import pytz  
import syslog
import datetime

logpath = 'instances.log'
IST = pytz.timezone('Asia/Kolkata')
dryrun = True

def getInstanceState(ec2, instance):
    curstate = ec2.Instance(instance.id)
    return curstate.state['Name']

def canShutdown( ec2, instance ):
    returnValue = False;
    shutDownTag = False;
    schedule = ""

    sys.stdout.write(str(datetime.datetime.now(IST)) + ' AWS Monitor: Checking shutdown schedule for ' + instance.id)
    for tag in instance.tags:
        cmdStr = str(tag['Key']).lower();
        if cmdStr == 'shutdown':
            shutDownTag = True
            schedule = str(tag['Value']).lower()
            sys.stdout.write(' : found shutdown @ ' + schedule + '\n')
            break;

    if shutDownTag == False:
        print ": None\n"
    else :
        if schedule.find('daily') > -1:
            cmdSchedule = schedule.split(' ');
            cmdTime = datetime.datetime.strptime(cmdSchedule[1],'%H:%M').time()
            curTime = datetime.datetime.now(IST).time()
        else:
            curTime = datetime.datetime.now(IST)
            cmdTime = datetime.datetime.strptime(schedule, '%d-%b-%Y %H:%M').replace(tzinfo=curTime.tzinfo)

        if curTime > cmdTime:
            sys.stdout.write('  Schedule expired, checking current state ... ')
            status = getInstanceState(ec2, instance);
            sys.stdout.write(status + '\n')
            if status == 'running':
                sys.stdout.write('  Performing shut down ' + instance.id + ' @ ' + str(curTime) + '\n')
                returnValue = True
            else:
                sys.stdout.write('  Skipping shut down ' + instance.id + ' @ ' + str(curTime) + '\n')
                returnValue = False

    return returnValue

def canTerminate(ec2, instance ):
    returnValue = False;
    terminateTag = False;
    schedule = ""

    sys.stdout.write(str(datetime.datetime.now(IST)) + ' AWS Monitor: Checking terminate schedule for ' + instance.id)
    for tag in instance.tags:
        cmdStr = str(tag['Key']).lower();
        if cmdStr == 'destroy':
            terminateTag = True
            schedule = str(tag['Value']).lower()
            sys.stdout.write(' : found terminate @ ' + schedule + '\n')
            break;

    if terminateTag == False:
        print ": None\n"
    else:
        curTime = datetime.datetime.now(IST)
        cmdTime = datetime.datetime.strptime(schedule, '%d-%b-%Y %H:%M').replace(tzinfo=curTime.tzinfo)
        if curTime > cmdTime:
            sys.stdout.write('  Schedule expired, checking current state ... ')
            status = getInstanceState(ec2, instance);
            sys.stdout.write(status + '\n')
            if status == 'running' or status == 'stopped':
                sys.stdout.write('  Performing terminate ' + instance.id + ' @ ' + str(curTime) + '\n')
                returnValue = True
            else:
                sys.stdout.write('  Skipping terminate ' + instance.id + ' @ ' + str(curTime) + '\n')
                returnValue = False

    return returnValue

def main():
    ec2 = boto3.resource('ec2')
    fp = open(logpath, 'a+')
    for instance in ec2.instances.all():
        if getInstanceState(ec2, instance) == 'terminated':
            continue
        if instance.tags is None:
            sys.stdout.write(str(datetime.datetime.now(IST)) + ' AWS Monitor: Skipping Instance ' + instance.id + ', No command string found in tags\n')
            continue
        else:
            if canShutdown(ec2 , instance) == True:
                sys.stdout.write('  Shutting down instance ' + instance.id + '\n')
                if dryrun == False:
                    ec2.instances.filter(InstanceIds=[instance.id]).stop()
            elif canTerminate(ec2, instance) == True:
                sys.stdout.write('  Terminating instance ' + instance.id + '\n')
                if dryrun == False:
                    ec2.instances.filter(InstanceIds=[instance.id]).terminate()
    fp.close()

if __name__ == '__main__':
    main()
