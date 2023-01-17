from subprocess import run,PIPE
import requests
import sublist3r
import subprocess
import os
import sys
import json
import dnsdumpster
import re
import sys
from pymongo import MongoClient
from crtsh import crtshAPI


if len(sys.argv)==1:
    print("[*] Usage: python3 "+sys.argv[0]+" domain")
    sys.exit()

domain = sys.argv[1]

def subd(domain):
    print("[+] Searching for domain : " + domain)
    subdomains = []

    ##### Subfinder ######
    try:
        subfinderoutput = run(["subfinder","-d",domain], stderr=PIPE, stdout=PIPE, shell=False, text=True)
        subdomains += list(subfinderoutput.stdout.splitlines())
    except Exception as _:
        print("Subfinder Error")


    ##### Assetfinder ######
    try:
        assetfinderoutput = run(["assetfinder",domain], stderr=PIPE, stdout=PIPE, shell=False, text=True)
        subdomains += list(assetfinderoutput.stdout.splitlines())
    except Exception as _:
        print("Assefinder Error")

    ###### Sublist3r #######
    try:
        sublist3routput = sublist3r.main(domain, 40, savefile = None ,ports=None , verbose = True, silent = True ,enable_bruteforce = False, engines = None)
        subdomains += list(sublist3routput)
    except Exception as _:
        print("Sublist3r Error")


    ##### Amass ######
    try:
        amassoutput = run(["amass","enum","-passive","-norecursive","-noalts","-d",domain], stderr=PIPE, stdout=PIPE, shell=False, text=True)
        subdomains += list(amassoutput.stdout.splitlines())
    except Exception as _:
        print("Amass Error")

    ###### SONAR Project API ####### not working rn

    # response = requests.get("https://sonar.omnisint.io/subdomains/"+domain)
    # if(response.status_code == 200):
    #     data = response.json()
    #     subdomains += data['results']

    ##### CRT.SH API ##### 
    # response = requests.get("https://crt.sh", params={'q': domain, 'output' : 'json'}, verify=False)
    # if(response.status_code == 200):
    #     data = response.json()
    #     print(data)    
    try:
        res = json.loads(json.dumps(crtshAPI().search(domain)))
        crtshsubdomains = []
        for ele in res:
            namevalue = ele["name_value"] 
            if re.match(r"^\w.*$", namevalue): 
                crtshsubdomains.append(namevalue)
        subdomains += list(crtshsubdomains)
    except Exception as _:
        # print("CRTSH Error")
        print()

    subdomains = list(set(subdomains))
    print(subdomains)

    return subdomains


subd(domain) 
