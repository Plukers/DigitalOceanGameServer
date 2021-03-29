#!/usr/bin/env python

import base64
import getpass
import os
import socket
import getopt
import sys
from pathlib import Path
import digitalocean

import paramiko
from paramiko.py3compat import input

def exec_commands(commands):
    for command in commands:
        print("*** {}".format(command))
        stdin, stdout, stderr = client.exec_command(command)
        print(stdout.read().decode())
        errors = stderr.read().decode()
        if errors:
          print("*** Errors")
          print(stderr.read())

def usage():
  f = open("help.txt", "r")
  print(f.read)



# Parse arguments
try:
  options, remainder = getopt.gnu_getopt(
    sys.argv[1:], 'h:s:v', ["stop", "save=", "verbose", "version", "help"])
except getopt.GetoptError as err:
  print("*** " + str(err))
  usage()
  sys.exit(2)

version = "0.5"
verbose = False
port = 22
save_file_path = ""
stop_server = False

for opt, arg in options:
  if opt in ("-s", "--save"):
    save_file_path = arg
    if(not os.path.exists(save_file_path)):
      print("*** Save file not found!")
      sys.exit(1)
  elif opt in ("--verbose"):
    verbose = True
  elif opt in ("-v", "--version"):
    print(str(sys.argv[0]) + " version: " + str(version))
    sys.exit(0)
  elif opt in ("--stop"):
    stop_server = True
  elif opt in ("-h", "--help"):
    usage()
    sys.exit(0)

verboseprint = print if verbose else lambda *a, **k: None
verboseprint("OPTIONS    :", options)
verboseprint("ARGV       :", sys.argv[1:])

if(not save_file_path):
  print("*** No save file provided. New save file will be created.")

# get rsa key
ssh_key_path = os.path.join(Path.home(), ".ssh", "id_ed25519")
if(not os.path.exists(ssh_key_path)):
  print("No .ssh/id_ed25519 key found for server login.")
  sys.exit(1)

pw = getpass.getpass("Password for key .ssh/id_ed25519:")
if(not pw):
  pw = None
pkey = paramiko.Ed25519Key.from_private_key_file(str(ssh_key_path), password=pw)

token = "token here"

if (stop_server):
  print("*** Shutdown droplet...")

  manager = digitalocean.Manager(token=token)

  my_droplets = manager.get_all_droplets()
  for i, v in enumerate(my_droplets):
      v.destroy()

  sys.exit(0)


print("*** Creating droplet...")

manager = digitalocean.Manager(token=token)
keys = manager.get_all_sshkeys()

droplet = digitalocean.Droplet(token=token,
                                name='FactorioServer',
                                region='fra1',
                                image='docker-20-04', 
                                size_slug='s-1vcpu-1gb',
                                ssh_keys=keys, #Add all keys
                                backups=False)
droplet.create()

droplet_created = False
while not droplet_created:
  for action in droplet.get_actions():
      action.load()
      if action.status == "completed":
        droplet_created = True;
        break
      if action.status == "errored":
        print("Error when creating droplet.")
        sys.exit(1)

# Request all droplets and find recently created droplet
# We do this as the created droplet object is missing some information, e.g. ip address
found_droplet = False
my_droplets = manager.get_all_droplets()
for i, v in enumerate(my_droplets):
  if v.id == droplet.id:
      droplet = v
      found_droplet = True;

if(not found_droplet):
  print("*** Could not setup droplet.")
  sys.exit(1)

username = "root"
hostname = droplet.ip_address

# now, connect and use paramiko Client to negotiate SSH2 across the connection
try:
  client = paramiko.SSHClient()
  client.load_system_host_keys()
  client.set_missing_host_key_policy(paramiko.WarningPolicy())
  print("*** Connecting...")
  try:
      client.connect(
          hostname,
          port,
          username,
          pkey=pkey,
      )
  except Exception:
      pw = getpass.getpass("Password for private key wrong?: ")
      pkey = paramiko.Ed25519Key.from_private_key_file(str(ssh_key_path), password=pw)
      client.connect(
          hostname,
          port,
          username,
          pkey=pkey,
      )

  commands = [ 
    "sudo mkdir -p /opt/factorio", 
    "sudo chown 845:845 /opt/factorio",
    "sudo docker run -d -p 34197:34197/udp -p 27015:27015/tcp -v /opt/factorio:/factorio --name factorio --restart=always factoriotools/factorio",
    "docker stop factorio",
  ]
  exec_commands(commands)

  if(save_file_path):
    sftp = client.open_sftp()

    print("Copying save file {}".format(save_file_path))
    sftp.put(save_file_path, os.path.join("/opt/factorio/saves", os.path.basename(save_file_path)))

    sftp.close()

  commands = [
    "docker start factorio",
  ]
  exec_commands(commands)
  
  client.close()

  print("Server id: {}".format(hostname))

except Exception as e:
    print("*** Caught exception: %s: %s" % (e.__class__, e))
    try:
        client.close()
        pass
    except:
        pass
    sys.exit(1)
