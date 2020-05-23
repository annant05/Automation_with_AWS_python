#!/usr/bin/env python3

import boto3
import json
import time
import sys
import subprocess

instance_id = ""
RDP_USERNAME = ""
RDP_PASSWORD = ""

STR_PUBLIC_IP = "PublicIpAddress"

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


def get_instance_state(instance_id, get_ip=False):

    response = aws_ec2_client.describe_instances(InstanceIds=[instance_id])
    instance_meta = response["Reservations"][0]["Instances"][0]

    if(get_ip):
        if(STR_PUBLIC_IP) in instance_meta:
            return (instance_meta[STR_PUBLIC_IP])
        else:
            return None
    else:
        return (instance_meta["State"]["Name"]).lower()


def start_instance(instance_id):
    choice_start = (
        input("-> START <- the server YES/NO (default - NO): ")).lower()

    if(choice_start == "yes"):
        aws_ec2_client.start_instances(InstanceIds=[instance_id])

    if(choice_start == "" or choice_start == "no"):
        exit_prog()

    return


def exit_prog():
    choice_exit = (
        input("-> EXIT <- the program : YES/NO (default - YES): ")).lower()

    if(choice_exit == "" or choice_exit == "yes"):
        exit(0)


def start_rdp(instance_id):
    choice_rdp = (
        input("-> RDP <- into server YES/NO (default - YES): ")).lower()

    if(choice_rdp == "" or choice_rdp == "yes"):
        print("doing_rdp")

        SERVER_IP = get_instance_state(instance_id, get_ip=True)
        PORT = 3389

        cmd_cmdkey = f'cmdkey /add: {SERVER_IP} /user: {RDP_USERNAME} /pass: {RDP_PASSWORD}'
        cmd_mstsc = f'mstsc /v:{SERVER_IP}:{PORT} /f'
        try:
            print(cmd_cmdkey)
            subprocess.Popen(cmd_cmdkey)
            print(cmd_mstsc)
            subprocess.Popen(cmd_mstsc)
            sys.exit(0)
        except subprocess.CalledProcessError as e:
            print("Error: ", e.output)
        
        time.sleep(3)
        exit_prog()

    if(choice_rdp == "no"):
        choice_stop = (input("-> STOP <- the server YES/NO (default - NO): ")).lower()

        if(choice_stop == "yes"):
            aws_ec2_client.stop_instances(InstanceIds=[instance_id])
            print("We are stopping your server")

        exit_prog()

    return


def state_change(instance_id):
    state = get_instance_state(instance_id)

    if(state == "stopped"):
        start_instance(instance_id)

    elif(state == "running"):
        start_rdp(instance_id)

    elif(state == "pending"):
        wait = 20
        print("Please wait for some time for server to start")
        time.sleep(wait)
        state_change(instance_id)

    elif(state == "stopping"):
        print("The instance is stopping at this moment")

    else:
        print("The instance is in some other state")


while(1):
    state_change(instance_id)

# print(get_instance_state(instance_id,get_ip=True))
