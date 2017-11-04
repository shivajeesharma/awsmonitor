# Author: Shivajee.R.Sharma <shivajee.sharma@gmail.com>                                                 
# License: Apache                                                                                       
#                                                                                                       
# This program is used for monitoring AWS instances, the program stops/terminates aws instances based   
# instance tag values. By changing the dryrun value to False, the user of this program completely owns  
# the responsibility of the consequences arising out of it.                                             
#                                                                                                       
# This script depends on boto3, pytz and aws-cli pip packages                                           
# This program is tested on Ubuntu 16.04, please refere to relevant os guide to setup the packages      
# On Ubuntu 16.04                                                                                       
# $ sudo apt install python-pip                                                                         
# $ sudo pip install --upgrade pip                                                                      
# $ sudo pip install --upgrade awscli                                                                   
# $ sudo pip install --upgrade boto3                                                                    
# $ sudo pip install --upgrade pytz                                                                     
#                                                                                                       
# Note: Create an IAM user on your AWS Console and note down the AccessID and Access Key                
# $ aws configure                                                                                       
# AWS Access Key ID: <enter your IAM user Access Key here>                                              
# AWS Secret Access Key:<enter your IAM user Secret Access Key here>                                    
# Default region name: <Enter your default region Name>                                                 
# Default output format: json                                                                           
#                                                                                                       
# Check if everything is configured properly                                                            
# $ aws ec2 describe-instances                                                                          
# list of aws instances and their properties                                                            
#                                                                                                       
# Copy this program in your home folder and execute                                                     
# $ python awsmonitor.py                                                                                
#                                                                                                       
# For the script to function you will have to add tags to your instances valid tags are                 
# Key           Values                                                                                  
# Shutdown      daily HH:MM or DD-MMM-YYYY HH:MM                                                        
# Destroy       DD-MMM-YYYY HH:MM                                                                       
#                                                                                                       
# For Eg:                                                                                               
# Shutdown      daily 18:00  will check and stop the machine daily at 6 PM IST                          
# Shutdown      03-Nov-2017 18:00  will check and stop the machine on 3 Nov 2017 at 6 PM IST            
# Destroy       03-Nov-2017 18:00  will check and terminate the machine on 3 Nov 2017 at 6 PM IST       
#                                                                                                      
# An instance can have bot shutdown as well as Destroy tags                                             
# Please note time is hardcoded in IST time zone, also the variable dryrun must be set to false for     
# the script to actually perform the action                                                             
# the script can be easily added to crontab for repeated execution                                      
