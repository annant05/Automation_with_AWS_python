#!/usr/bin/env python3

import boto3
import json
import time 
import sys 

instance_id = "i-031bc1e674943a27d"
rdp_username = ""
rdp_password = ""

AWS_credentials = {
    "AWS_ACCESS_KEY": "",
    "AWS_SECRET_KEY": "",
    "AWS_REGION": "ap-south-1"
}

session = boto3.Session(
    aws_access_key_id=AWS_credentials["AWS_ACCESS_KEY"],
    aws_secret_access_key=AWS_credentials["AWS_SECRET_KEY"],
    region_name=AWS_credentials["AWS_REGION"]
)

aws_ec2_client = session.client('ec2')



def get_instance_state(instance_id,get_ip=False):

    response = aws_ec2_client.describe_instances(
        InstanceIds=[instance_id]
    )
    instance_meta = response["Reservations"][0]["Instances"][0]
    
    if(get_ip):
        if("PublicIpAddress")
    else:
        return (instance_meta["State"]["Name"]).lower()


def start_instance(instance_id):
    choice_start = (input("Do you want to START the server YES/NO : ")).lower()
    if(choice_start == "yes"):
        aws_ec2_client.start_instance(
            InstanceIds=[instance_id]
        )
    if(choice_start == "no"):
        choice_exit = (input("Do you want to EXIT the program : YES/NO : ")).lower()
        if(choice_exit == "yes"):
            exit(0)

def start_rdp(instance_id):
    choice_rdp = (input("Do you want to RDP into server YES/NO : ")).lower()
    if(choice_rdp == "yes" or ""):

        cmd_cmdkey = f'cmdkey /add: {server_ip} /user: {rdp_username} /pass: {rdp_password}'

        cmd_mstsc = f'mstsc /v:server_ip:port /f'
   
    if(choice_rdp == "no"):
        choice_exit = (input("Do you want to EXIT the program : YES/NO : ")).lower()
        if(choice_exit == "yes"):
            exit(0)
    return


def state_change(instance_id):
    state = get_instance_state(instance_id)

    if(state == "stopped"):
        start_instance(instance_id)
    elif(state == "running"):
        start_rdp(instance_id)
    elif(state == "pending"):
        print("Please wait for some time")
        state_change(instance_id)


while(1):
    state_change(instance_id)

