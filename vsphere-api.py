import requests
import getpass

_version_ = "0.0.1"


server = "SERVER_IP"
user = "USER"
password = getpass.getpass(prompt="Password for user "+args.user+" to login to vsphere server "+server+": ")
vm = "VM-ID"
session_id = ""

# Get session ID
auth_url = "https://" + server + "/api/session"
response = requests.post(auth_url, auth=(user,password), verify=False)
if response.ok:
    session_id = response.json()
    print("\nSession ID: " + session_id + "\n")
else:
    raise ValueError("Unable to retrieve a session ID.")

# Get VMs for example
response = requests.get("https://"+server+"/api/vcenter/vm/"+vm, headers={"vmware-api-session-id": session_id}, verify=False)
if response.ok:
    print("\nVM Details:")
    print(response.json())
else:
    raise ValueError("Unable to retrieve VM details")

# Logout
response = requests.delete("https://"+server+"/api/session", headers={"vmware-api-session-id": session_id}, verify=False)
if response.ok:
    print("\nLogout Successful:")
else:
    raise ValueError("Unable to logut")

