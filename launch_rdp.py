import subprocess
import json
import os
import sys
import time

instance = {
    "t2.micro": "i-",
    "t2.small": "i-",
    "t2.medium": "i-"
}

instance_id = ""
public_ip_add_string = "PublicIpAddress"
port = "3389"

user = str(input("enter username : ")).lstrip().rstrip().strip(" ") or "Administrator"
password = str(input("enter password: ")).lstrip().rstrip().strip(" ") or ""

response = ""
instance_data = ""
state = ""
volume_id = "vol-"


def select_instance():
    ch = str(raw_input(" f: t2.micro(free)  /  s:  t2.small(economy)   /  m: t2.medium(performance) : "))
    global instance_id
    if ch == 'f':
        instance_id = instance["t2.micro"]  # instance id for t2.small
    elif ch == 'm':
        instance_id = instance["t2.medium"]  # instance id for t2.medium
    elif ch == 's':
        instance_id = instance["t2.small"]  # instance id for t2.small
    else:
        print("Wrong option selected  ")
        select_instance()
    print("Initial Instance id : " + instance_id)
    check_state()


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

    try:
        response = str(subprocess.check_output(cmd_describe_ec2, stderr=subprocess.STDOUT)).replace("\\r\\n", '').strip(
            'b\'')
        obj_json = json.loads(response)
        instance_data = ((obj_json['Reservations'][0])['Instances'][0])
        state = str((instance_data['State'])['Name'])

    except subprocess.CalledProcessError as e:
        print "Error describing instance : ", e.output


def detach_attach_volume(instance_to_attach):
    global volume_id
    cmd_detach_volume = "aws ec2 detach-volume --volume-id " + volume_id

    try:
        print(str(subprocess.check_output(cmd_detach_volume, stderr=subprocess.STDOUT)).replace("\\r\\n", '').strip(
            'b\''))
    except subprocess.CalledProcessError as e:
        print "Already attached: ", e.output

    cmd_attach_volume = "aws ec2 attach-volume --volume-id " \
                        + volume_id + " --device /dev/sda1 --instance " + instance_to_attach
    print (str(subprocess.check_output(cmd_attach_volume, stderr=subprocess.STDOUT)).replace("\\r\\n", '').strip(
        'b\''))


def start_instance():
    global instance_id
    print("Instance id in start_instance is : " + instance_id)
    cmd_start_instance = "aws ec2 start-instances --instance-ids " + instance_id
    try:
        current_state = subprocess.check_output(cmd_start_instance, stderr=subprocess.STDOUT)
        print(current_state)
    except subprocess.CalledProcessError as e:
        print "Error starting instance : ", e.output
        exit()


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
        try:
            print(cmd_cmdkey)
            subprocess.Popen(cmd_cmdkey)
            print(cmd_mstsc)
            subprocess.Popen(cmd_mstsc)
            sys.exit(0)
        except subprocess.CalledProcessError as e:
            print "Error: ", e.output


def write_response_in_file():
    global response
    print(os.getcwd() + "\\response.json")
    res_file = open("response.json", "w")
    res_file.write(response)


select_instance()
