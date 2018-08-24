import os
import subprocess
import json

instance_id = "i-0463*****"
cmd = "aws ec2 describe-instances --instance-ids " + instance_id
server_ip = "0.0.0.0"
user = str(input("enter username : ")).lstrip().rstrip().strip(" ") or "Administrator"
password = str(input("enter password: ")).lstrip().rstrip().strip(" ") or "password"
port = "3389"

response = str(subprocess.check_output(cmd, stderr=subprocess.STDOUT)).replace("\\r\\n", '').strip('b\'')
# print(response)
public_ip_add = "PublicIpAddress"
is_having = (response.find(public_ip_add))

if is_having == -1:
    print("ec2 instance has no public ipv4")
    exit(0)
else:
    obj_json = json.loads(response)
    server_ip = str(((obj_json['Reservations'][0])['Instances'][0])[public_ip_add])
    print(server_ip)
    cmd_key_cmd = "cmdkey " + "/add:" + server_ip + " /user:" + user + " /pass:" + password
    mstsc_cmd = "mstsc /v:" + server_ip + ":" + port + " /f"
    print(cmd_key_cmd)
    subprocess.check_output(cmd_key_cmd, stderr=subprocess.STDOUT)
    print(mstsc_cmd)
    subprocess.check_output(mstsc_cmd, stderr=subprocess.STDOUT)
