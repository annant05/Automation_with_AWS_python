import subprocess
import json
import os
import sys
import time

instance_id = "i-0d212a70a060e0ba7"
public_ip_add_string = "PublicIpAddress"
port = "3389"
user = str(raw_input("enter username: ")).lstrip().rstrip().strip(" ") or ""
password = str(raw_input("enter password: ")).lstrip().rstrip().strip(" ") or ""
response = ""
instance_data = ""
state = ""


def write_response_in_file():
    global response
    print(os.getcwd() + "\\response.json")
    res_file = open("response.json", "w")
    res_file.write(response)


def start_rdp():
    global response
    global public_ip_add_string
    is_having_ip = (response.find(public_ip_add_string))
    if is_having_ip == -1:
        print("ec2 instance has no public ipv4")
        exit(0)
    else:
        server_ip = str(instance_data[public_ip_add_string])
        print(server_ip)
        cmd_cmdkey = "cmdkey " + "/add:" + server_ip + " /user:" + user + " /pass:" + password
        cmd_mstsc = "mstsc /v:" + server_ip + ":" + port + " /f"
        print(cmd_cmdkey)
        subprocess.Popen(cmd_cmdkey)
        print(cmd_mstsc)
        subprocess.Popen(cmd_mstsc)
        sys.exit(0)


def start_instance():
    global instance_id
    cmd_start_instance = "aws ec2 start-instances --instance-ids " + instance_id
    current_state = subprocess.check_output(cmd_start_instance, stderr=subprocess.STDOUT)
    print(current_state)


def check_state():
    global instance_data
    global state
    wait = 30
    get_instance_state()
    if state == "pending":
        time.sleep(wait)
        check_state()
    elif state == "stopped":
        choice = raw_input("Enter \"YES\" to start the instance:  ")
        if choice == "YES":
            start_instance()
            print('Please! wait for ' + str(wait) + 'seconds')
            time.sleep(wait)
            check_state()
        else:
            print("BYE :)")
            exit(0)
    else:
        start_rdp()


def get_instance_state():
    global response
    global instance_data
    global state
    cmd_describe_ec2 = "aws ec2 describe-instances --instance-ids " + instance_id
    response = str(subprocess.check_output(cmd_describe_ec2, stderr=subprocess.STDOUT)).replace("\\r\\n", '').strip(
        'b\'')
    obj_json = json.loads(response)
    instance_data = ((obj_json['Reservations'][0])['Instances'][0])
    state = str((instance_data['State'])['Name'])


check_state()
