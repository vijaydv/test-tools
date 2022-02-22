#!/usr/local/bin/python
import paramiko
import os
from optparse import OptionParser

SSH_TIMEOUT = 50
LAB_URL = ""
mc_list = []

parser = OptionParser()
parser.add_option("-m", "--machinelist", dest="machine_list", help="provide comma separated machine list")
parser.add_option("-u", "--url", dest="lab_url", help="netinstall lab url page. Provide either lab url link or machine list, not both. If both machine list and URL are not provided, then all machines in IBQA netinstall page(http://install.ibqa/netinstall.cgi) is used")
(options, args) = parser.parse_args()
if options.lab_url and options.machine_list:
  print "\nProvide either URL or comma separated machine list, not both. If both not provided, IBQA netinstall page is used to get machine list"
  exit(1)

if options.lab_url and not options.machine_list:
  LAB_URL = options.lab_url
  print("\nLab url= %s" %(LAB_URL))
if options.machine_list and not options.lab_url:
  mc_list = options.machine_list.split(',')
  print("\nMachine list = %s" %(mc_list))
if not options.lab_url and not options.machine_list:
  LAB_URL = "http://install.ibqa/netinstall.cgi"
  print("\nLab url= %s" %(LAB_URL))

if LAB_URL:
  lab_output_file = "/tmp/lab_machines_%s.html" %(os.getpid())
  os.system("rm -rf %s" %(lab_output_file))
  print("Downloading the URL page using curl to get the machine list")
  os.system("curl -s -o %s %s" %(lab_output_file, LAB_URL))
  try:
    read_lab_file = open(lab_output_file,"r")
  except:
    print("Couldn't download the URL page provided. Please check the URL value provided")
    exit(1)
  for line in read_lab_file:
    if "A HREF=" in line:
      if "NOBR" in line:
        mc_name = line.split(":8123")[0].split("http://")[1]
        match_pattern = 0
        for pattern in ["bsd", "win", "lin"]:
          if pattern in mc_name:
            match_pattern = 1
            break
        if not match_pattern:
          mc_list.append(mc_name)
  read_lab_file.close()
  os.system("rm -rf %s" %(lab_output_file))
  print("Machine list = %s\n" %(mc_list))

product = ""
amp_parm = {}
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
for host in mc_list:
  print "checking host = ", host
  mc_ver = ""
  try:
    ssh.connect(host,username="rtestuser",password="ironport",timeout=SSH_TIMEOUT)
    stdin, stdout, stderr = ssh.exec_command("/data/bin/cli.sh version")
    for line in stdout.read().splitlines():
      if "Web Security" in line:
        product = "wsa"
      elif "Email Security" in line:
        product = "esa"
      if "Version:" in line:
        mc_full_version = line.split(":")[1].strip()
        mc_ver = line.split(":")[1].split("-")[0].strip()
      if "Serial #:" in line:
        mc_serial = line.split(":")[1].strip()
        break
    if product == "esa" and mc_ver >= "8.5.5":
      stdin, stdout, stderr = ssh.exec_command("cat /data/release/current/fire_amp/fireamp.ini | egrep -e rep_api_key -e analysis_api_key")
    elif product == "wsa" and mc_ver >= "8.0.5":
      stdin, stdout, stderr = ssh.exec_command("cat /data/fire_amp/fireamp.ini | egrep -e rep_api_key -e analysis_api_key")
    else:
      ssh.close()
      continue
    ssh.close()
    amp_parm[host] = {}
    amp_parm[host]["version"] = mc_full_version
    amp_parm[host]["serial_no"] = mc_serial
    amp_parm[host]["analysis_api_key"] = ""
    amp_parm[host]["rep_api_key"] = ""
    for line in stdout.read().splitlines():
      if "analysis_api_key" in line:
        amp_parm[host]["analysis_api_key"] = line.split("=")[1].strip()
      if "rep_api_key" in line:
        amp_parm[host]["rep_api_key"] = line.split("=")[1].strip()
  except Exception as ne:
    print("Error [%s] while trying to get AMP details from host [%s]" %(ne,host))
#print("\namp_parm = %s\n" %(amp_parm))

print("\nAMP API details for machines running 8.5.5 and above in case of ESA and 8.0.5 and above in case of WSA")
print("\n%s | %s | %s | %s | %s" %("Hostname","Serial No.","Version","analysis_api_key","rep_api_key"))
for host in amp_parm.keys():
  print("%s | %s | %s | %s | %s" %(host,amp_parm[host]["serial_no"],amp_parm[host]["version"],amp_parm[host]["analysis_api_key"],amp_parm[host]["rep_api_key"]))

