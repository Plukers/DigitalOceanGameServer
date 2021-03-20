#!/usr/bin/env python

# Copyright (C) 2003-2007  Robey Pointer <robeypointer@gmail.com>
#
# This file is part of paramiko.
#
# Paramiko is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# Paramiko is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Paramiko; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.


import base64
import getpass
import os
import socket
import sys
import traceback
from pathlib import Path
from paramiko.py3compat import input

import paramiko

def exec_commands(commands):
    for command in commands:
        print("*** {}".format(command))
        stdin, stdout, stderr = client.exec_command(command)
        print(stdout.read().decode())
        errors = stderr.read().decode()
        if errors:
          print("*** Errors")
          print(stderr.read())
    

port = 22

if len(sys.argv) != 3:
    print("*** user@hostname and path to save file required.")
    sys.exit(1)

username = ""
hostname = sys.argv[1]
if hostname.find("@") >= 0:
  username, hostname = hostname.split("@")
else:
  print("*** Hostname required.")
  sys.exit(1)

save_file_path = sys.argv[2]
if(not os.path.exists(save_file_path)):
  print("*** Save file not found.")
  sys.exit(1)

# get rsa key
ssh_key_path = os.path.join(Path.home(), ".ssh", "id_ed25519")
if(not os.path.exists(ssh_key_path)):
  print("No .ssh/id_ed25519 key found for server login.")
  sys.exit(1)

pw = getpass.getpass("Password for key .ssh/id_ed25519:")
if(not pw):
  pw = None
pkey = paramiko.Ed25519Key.from_private_key_file(str(ssh_key_path), password=pw)

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
        pw = getpass.getpass("Password for private key wrong?: " % (username, hostname))
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

    sftp = client.open_sftp()

    print("Copying save file {}".format(save_file_path))
    sftp.put(save_file_path, os.path.join("/opt/factorio/saves", os.path.basename(save_file_path)))

    sftp.close()

    commands = [
      "docker start factorio",
    ]
    exec_commands(commands)
   
    client.close()

except Exception as e:
    print("*** Caught exception: %s: %s" % (e.__class__, e))
    # traceback.print_exc()
    try:
        client.close()
        pass
    except:
        pass
    sys.exit(1)
