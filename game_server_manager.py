import sys
import argparse
import os
from pathlib import Path
import paramiko
from paramiko import SSHClient
from paramiko.py3compat import input

from game_server_api import GameServerAPI
from game import Game

class __IgnorePolicy(paramiko.MissingHostKeyPolicy):
  """
  Policy for logging a Python-style warning for an unknown host key, but
  accepting it. This is used by `.SSHClient`.
  """

  def missing_host_key(self, client, hostname, key):
    print("Unknown {} host key for {}: {}".format(
              key.get_name(), hostname, hexlify(key.get_fingerprint()).decode()
          ))   

def __create_ssh_client(hostname, port, username, pkey) -> SSHClient:
    # now, connect and use paramiko Client to negotiate SSH2 across the connection
    try:
      client = paramiko.SSHClient()
      client.load_system_host_keys()
      client.set_missing_host_key_policy(__IgnorePolicy())
      print("Connecting...")
      try:
          client.connect(
              hostname,
              port,
              username,
              pkey=pkey,
          )
      except Exception as e:
          pw = getpass.getpass("Password for private key wrong?: ")
          pkey = paramiko.Ed25519Key.from_private_key_file(str(ssh_key_path), password=pw)
          client.connect(
              hostname,
              port,
              username,
              pkey=pkey,
          )

      return client
    except Exception as e:
      print("Caught exception: %s: %s" % (e.__class__, e))
      try:
          client.close()
          pass
      except:
          pass
      sys.exit(1)

class GameServerManager(GameServerAPI):
  serverName = None
  game = None

  client = None
  token = None
  pkey = None

  def __init__(self, game : Game):
    self.game = game
    serverName = '{}Server'.format(game.name())

  def run(self):
    parser = argparse.ArgumentParser()
    

    parser.add_argument('-t', '--token', nargs=1,
                        help='Digital Ocean API token.')
    parser.add_argument('-k', '--key', 
                        type=str, 
                        default=os.path.join(Path.home(), ".ssh", "id_ed25519"), 
                        help='path to SSH key for server login. Defaults to ~/.ssh/id_ed25519')

    control_group = parser.add_mutually_exclusive_group(required=False)

    control_group.add_argument('-l', '--list', action='store_true', help='lists running servers')  
    control_group.add_argument('-s', '--shutdown', action='store_true', help='stops and deletes all running servers.')  

    for action in self.game.supported_actions():
      (name, help, has_param, callback) = action
      if not has_param:
        parser.add_argument('--' + name, action='store_true', help=help)  
      else:
        parser.add_argument('--' + name, help=help)

    args = parser.parse_args()

    if args.token is None:
      print("Error: Digital Ocean API token required.")
      sys.exit(1)
    
    self.token = args.token

    if args.key is not None:
      if(not os.path.exists(args.key)):
        print("No {} key found for server login.".format(args.key))
        sys.exit(1)

      try:
        self.pkey = paramiko.Ed25519Key.from_private_key_file(args.key)
      except Exception:
        pw = getpass.getpass("Password for key {}:")
        if(not pw):
          pw = None
        self.pkey = paramiko.Ed25519Key.from_private_key_file(args.key, password=pw)
    else:
      print("Error: SSH key for server login required.")
      sys.exit(1)

    
    if args.list is not None and args.list:
      self.__list_server()
      sys.exit(0)

    if args.shutdown is not None and args.shutdown:
      self__shutdown_server()
      sys.exit(0)

    for arg in vars(args):
      if getattr(args, arg) is not None:
        for action in self.game.supported_actions():
          (name, _, has_param, callback) = action
          if name == arg:
            if not has_param:
              callback(self)
            else:
              callback(self, getattr(args, arg))

  def __list_server(self):
    manager = digitalocean.Manager(token=self.token)

    numFound = 0

    my_droplets = manager.get_all_droplets()
    for i, v in enumerate(my_droplets):
      if(v.name == serverName):
        numFound += 1

    pluralS = ""
    if (numFound != 1):
      pluralS = "s"

    print("Found {} {} server{}".format(numFound, game.name(), pluralS))

  def __shutdown_server(self):
    print("Destroying {} servers...".format(game.name()))

    manager = digitalocean.Manager(token=self.token)

    numDestroyed = 0

    my_droplets = manager.get_all_droplets()
    for i, v in enumerate(my_droplets):
      if(v.name == serverName):
        v.destroy()
        numDestroyed += 1

    pluralS = ""
    if (numDestroyed != 1):
      pluralS = "s"
    
    print("{} {} server{} destroyed".format(numDestroyed, game.name(), pluralS))

  def create_droplet(self, droplet_size: str) -> str:    
    pass            

  def server_address(self) -> str:
    return ""

  def exec_command(self, command: str):
    print("*** {}".format(command))
    _, stdout, stderr = client.exec_command(command)
    print(stdout.read().decode())
    errors = stderr.read().decode()
    if errors:
      print("*** Errors")
      print(errors)

  def exec_commands(self, commands: list[str]):
    for command in commands:
      self.exec_command(command)

  def upload(self, localFilePath: str, serverTargetPath: str):
    sftp = client.open_sftp()

    print("*** Uploading {}".format(localFilePath))
    sftp.put(localFilePath, serverTargetPath)

    sftp.close()

  def download(self, serverTargetPath: str, localFilePath: str):
    sftp = client.open_sftp()

    print("*** Downloading to {}".format(localFilePath))
    sftp.get(serverTargetPath, localFilePath)

    sftp.close()
