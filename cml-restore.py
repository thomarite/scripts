# example: $ python cml-restore.py -f FILE.yaml -l LAB_NAME
# default user is admin

import requests
import yaml
import argparse
import getpass
import sys

_version_ = "0.0.1"

cml_hostname = "cml01.test"

def parse.args():
    parser = argparse.ArgumentParser(description="Upload lab into CML")
    parser.add_argument("-u","--user",help="user to login to CML",nargs='?', const=1, default="admin")
    parser.add_argument("-f","--file",help="Lab yaml file to upload")
    parser.add_argument("-l","--lab",help="Lab name in CML")
    parser.add_argument("-v","--version",action="version",version="%(prog)s (version {})".format(__version__))
    args = parser.parse_args()
    return args

# Authenticate with CML and get token
def auth_cml(cml_ip,user,password):
    auth_url = "https://" + cml_ip + "/api/v0/authenticate"
    auth_header = {"Content-Type": "application/json", "accept": "application/json"}
    auth_payload = {"username": user, "password": password}
    response = requests.post(url=auth_url, headers=auth_header, json=auth_payload, verify=False)

    token = ""

    if response.ok:
        print("\nAuthentication Successful: " + str(response.status_code) + "\n")
        # somehow the token includes " as part of the string so need to remove " before using it later
        token = response.text.replace('"','')
        return token
    else:
        sys.exit("Authentication Error - HTTP Error " + str(response.status_code) + ":" + response.reason + " occurred")

# Upload lab file into CML with name "lab_name"
def upload_lab(cml_ip,token,lab_name,file_name):
    upload_url = "https://" + cml_ip + "/api/v0/import?tittle="+lab_name
    upload_header = {"Content-Type": "application/json", "accept": "application/json","Authorization": "Bearer "+token}

    lab_file = None
    with open(file_name, 'r') as file:
        lab_file = yaml.safe_load(file)

    response = requests.post(url=upload_url, headers=upload_header, json=lab_file, verify=False)

    if response.ok:
        print("\nLab Upload Successful: " + str(response.status_code) + "\n")
    else:
        sys.exit("Lab Upload Error -- HTTP Error " + str(response.status_code) + ":" + response.reason + " occurred")

# Destroy lab with title from var file_name: It needs to stop, wipe-out and delete the lab.
def delete_lab(cml_ip,token,lab_name):
    # Get list of all labs in CML:
    labs_url = "https://" + cml_ip + "/api/v0/labs?show_all=true"
    labs_header = {"accept": "application/json","Authorization": "Bearer "+token}
    response = requests.get(url=labs_url, headers=labs_header,verify=False)

    if not response.ok:
        sys.exit("List Labs Error -- HTTP Error " + str(response.status_code) + ":" + response.reason + " occurred")

    # Delete lab that matches the provided title. Earlier response was a list of labs. So we iterate over the list.
    list_labs = response.json()
    lab_url = "https://" + cml_ip + "/api/v0/labs/"
    for lab in list_labs:
        response = requests.get(url=lab_url+lab, headers=labs_header,verify=False)
        if ((response.ok) and (response.json()["lab_title"]==lab_name)):
            # stop lab
            response = requests.put(url=lab_url+lab+"/stop", headers=labs_header,verify=False)
            response.raise_for_status()
            # wipe-out lab
            response = requests.put(url=lab_url+lab+"/wipe", headers=labs_header,verify=False)
            response.raise_for_status()
            # destroy lab
            response = requests.put(url=lab_url+lab, headers=labs_header,verify=False)
            response.raise_for_status()
            print("\nLab "+lab_name+" has been deleted successfully.\n")

def main():
    args = parse.args()
    cml_pass = getpass.getpass(prompt="Password for user "+args.user+" in CML: ")
    token = auth_cml(cml_hostname,args.user,cml_pass)
    delete_lab(cml_hostname,token,args.lab)
    upload_lab(cml_hostname,token,args.lab,args.file)

if __name__ == "__main__":
    main()
