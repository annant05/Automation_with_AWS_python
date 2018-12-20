import subprocess
import json
import os
import sys
import time

# Dictionary of instances and their types for easy editing
instance = {
    "t2.micro": "i-027b481b0af2a79ae",
    "t2.small": "i-0f1f555ed44e3fbdd",
    "t2.medium": "i-0242a6d8d6acd36bf"
}

# Dictionary of volumes with their attachment_type : For ex: /dev/sda1
volumes = {
    "main_boot_vol": ["vol-0bf263386c4415c6f", "/dev/sda1"],
    "additional_storage_vol": ["vol-05a99df42b26e6b83", "/dev/sda2"]
    # "temp_5gb_vol": ["vol-02a6bf5074d93f6f1", "xvdf"]
}

# enter the username and password used to login into the instance using RDP.
user = ""
password = ""

# Change if using any custom port for RDP.
port = "3389"

# This variable is used to set instance_id to be used by all the functions.
instance_id = ""

# This string is searched in JSON response to get the Public IP_address of the instance.
public_ip_add_string = "PublicIpAddress"

# JSON response from the ec2 describe function is stored in this variable for use by different functions.
response = ""

# JSON response is traversed to get description data of the chosen instance.
instance_data = ""

# Get the state of the instance to perform the respective function or operation.
state = ""


# Function that is used to select the instance for launch or RDP.
def select_instance():
    # Show the list of available instances.
    ch = str(input(" f: t2.micro(free)  /  s:  t2.small(economy)   /  m: t2.medium(performance) : "))

    # access global variable instance_id inside the function
    global instance_id

    # if else code to change global instance id to the selected instance id.
    if ch == 'f':
        instance_id = instance["t2.micro"]
    elif ch == 'm':
        instance_id = instance["t2.medium"]
    elif ch == 's':
        instance_id = instance["t2.small"]
    else:
        print("Wrong option selected. \n Enter a valid choice ")
        # If wrong option is selected. Ask again for a valid choice recursively.
        select_instance()

    # print the selected instance to the command line
    print(" You have selected Instance with id : " + instance_id)

    # Call function to check state of the instance.
    check_state()


# Function that checks the instance state to decide between RDP or starting the instance.
def check_state():
    # access global variables instance_data and state inside the function.
    global instance_data
    global state

    # amount of time to wait between checking for change in the state of the instance.
    wait = 30

    # call this function to execute the aws cli commands.
    get_instance_state()

    # This conditional statements decide to  RDP or start the instance.

    # if the instance is started and in pending state then wait for some time and check again.
    if state == "pending":
        time.sleep(wait)
        check_state()

    # if the instance is stooped then ask the user to start it and proceed.
    elif state == "stopped":

        # get user input from command line
        choice = input("Enter \"y\" to start the instance:  ")
        if choice == "y":
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
        print("instance started" + instance_id)


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
        print("Error describing instance : ", e.output)


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
            print("Error: ", e.output)


def start_instance():
    global instance_id
    print("Instance id in start_instance is : " + instance_id)
    cmd_start_instance = "aws ec2 start-instances --instance-ids " + instance_id
    try:
        current_state = subprocess.check_output(cmd_start_instance, stderr=subprocess.STDOUT)
        print(current_state)
    except subprocess.CalledProcessError as e:
        print("Error starting instance : ", e.output)
        exit()


def detach_attach_volume(instance_to_attach):
    global volumes
    cmd_detach_volume = "aws ec2 detach-volume --volume-id "

    for vol in volumes.keys():
        try:
            print(str(subprocess.check_output(cmd_detach_volume + volumes[vol][0], stderr=subprocess.STDOUT))
                  .replace("\\r\\n", '').strip('b\''))
        except subprocess.CalledProcessError as e:
            print("Already attached: ", e.output)

    for vol in volumes.keys():
        try:
            cmd_attach_volume = "aws ec2 attach-volume --volume-id " + volumes[vol][0] + " --device " + volumes[vol][
                1] + " --instance " + instance_to_attach
            print(str(subprocess.check_output(cmd_attach_volume, stderr=subprocess.STDOUT))
                  .replace("\\r\\n", '').strip('b\''))
        except subprocess.CalledProcessError as e:
            print("Error attaching volume: ", e.output)


# Function to write the instance data in a file for debugging.
def write_response_in_file():
    global response
    print(os.getcwd() + "\\response.json")
    res_file = open("response.json", "w")
    res_file.write(response)


select_instance()
