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
    print("*** Unknown {} host key for {}: {}".format(
              key.get_name(), hostname, hexlify(key.get_fingerprint()).decode()
          ))   

def __create_ssh_client(hostname, port, username, pkey) -> SSHClient:
    # now, connect and use paramiko Client to negotiate SSH2 across the connection
    try:
      client = paramiko.SSHClient()
      client.load_system_host_keys()
      client.set_missing_host_key_policy(__IgnorePolicy())
      print("*** Connecting...")
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
      print("*** Caught exception: %s: %s" % (e.__class__, e))
      try:
          client.close()
          pass
      except:
          pass
      sys.exit(1)

class GameServerManager(GameServerAPI):
  game = None
  client = None

  def __init__(self, game : Game):
    self.game = game

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

    if args.token is not None:
      print ("token has been set: {}".format(args.token))

    if args.key is not None:
      print ("key has been set: {}".format(args.key))
    
    if args.list is not None and args.list:
      print ("list has been set: {}".format(args.list))
      return

    if args.shutdown is not None and args.shutdown:
      print ("shutdown has been set: {}".format(args.shutdown))
      return

    for arg in vars(args):
      for action in self.game.supported_actions():
        (name, _, has_param, callback) = action
        if name == arg:
          if not has_param:
            callback(self)
          else:
            callback(self, getattr(args, arg))
            

  def server_address(self) -> str:
    return ""

  def exec_command(self, command: str):
    print("*** Error: exec_command not implemented.")
    sys.exit(1)

  def exec_commands(self, commands: list[str]):
    print("*** Error: exec_commands not implemented.")
    sys.exit(1)

  def upload(self, localFilePath: str, serverTargetPath: str):
    print("*** Error: upload not implemented.")
    sys.exit(1)

  def download(self, serverTargetPath: str, localFilePath: str):
    print("*** Error: download not implemented.")
    sys.exit(1)
