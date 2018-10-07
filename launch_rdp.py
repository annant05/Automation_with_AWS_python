import subprocess
import json
import os
import sys
import time

instance = {
    "t2.small": "i-",
    "t2.medium": "i-"
}

instance_id = ""
public_ip_add_string = "PublicIpAddress"
port = "3389"
user = ""
password = ""
response = ""
instance_data = ""
state = ""
volume_id = "vol-"


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
    print("Instance id in start_instance is : " + instance_id)
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
            detach_attach_volume(instance_id)
            start_instance()
            print('Please! wait for ' + str(wait) + 'seconds')
            time.sleep(wait)
            check_state()
        else:
            print("BYE :)")
            exit(0)
    else:
        start_rdp()
        print ("instance started" + instance_id)


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


def detach_attach_volume(instance_to_attach):
    global volume_id
    cmd_detach_volume = "aws ec2 detach-volume --volume-id " + volume_id
    print(str(subprocess.check_output(cmd_detach_volume, stderr=subprocess.STDOUT)).replace("\\r\\n", '').strip(
        'b\''))
    cmd_attach_volume = "aws ec2 attach-volume --volume-id " + volume_id + " --device /dev/sda1 --instance " + instance_to_attach
    print (str(subprocess.check_output(cmd_attach_volume, stderr=subprocess.STDOUT)).replace("\\r\\n", '').strip(
        'b\''))


def select_instance():
    ch = int(raw_input(" 1: t2.small  and  2: t2.medium    :"))
    global instance_id
    if ch == 1:
        instance_id = instance["t2.small"]  # instance id for t2.small
    elif ch == 2:
        instance_id = instance["t2.medium"]  # instance id for t2.medium
    print("Initial Instance id : " + instance_id)
    check_state()


select_instance()
