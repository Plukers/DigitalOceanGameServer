import sys
import argparse
import os
import getpass
from pathlib import Path
import paramiko
from paramiko import SSHClient
from paramiko.py3compat import input
from binascii import hexlify
import digitalocean

from game_server_api import GameServerAPI
from game import Game


class IgnorePolicy(paramiko.MissingHostKeyPolicy):
  """
  Policy for logging a Python-style warning for an unknown host key, but
  accepting it. This is used by `.SSHClient`.
  """

  def missing_host_key(self, client, hostname, key):
    # We ignore this
    pass

class GameServerManager(GameServerAPI):
  game = None

  client = None
  hostname = None
  token = None
  name = None

  pkey_path = None
  pkey = None

  def __init__(self, game: Game):
    self.game = game

  def run(self):
    parser = argparse.ArgumentParser()

    parser.add_argument('-n', '--name', nargs=1,
                        help='Name of the droplet.')
    parser.add_argument('-t', '--token', nargs=1,
                        help='Digital Ocean API token.')
    parser.add_argument('-k', '--key',
                        type=str,
                        default=os.path.join(
                            Path.home(), '.ssh', 'id_ed25519'),
                        help='path to SSH key for server login. Defaults to ~/.ssh/id_ed25519')

    control_group = parser.add_mutually_exclusive_group(required=False)

    control_group.add_argument(
        '-l', '--list', action='store_true', help='lists running servers')
    control_group.add_argument(
        '-s', '--shutdown', action='store_true', help='stops and deletes all running servers.')

    for action in self.game.supported_actions():
      (name, help, has_param, callback) = action
      if not has_param:
        parser.add_argument('--' + name, action='store_true', help=help)
      else:
        parser.add_argument('--' + name, help=help)

    args = parser.parse_args()

    if args.token is None:
      print('Error: Digital Ocean API token required.')
      sys.exit(1)

    self.token = args.token

    if args.key is not None:
      self.pkey_path = args.key
      if(not os.path.exists(self.pkey_path)):
        print('No {} key found for server login.'.format(self.pkey_path))
        sys.exit(1)

      try:
        self.pkey = paramiko.Ed25519Key.from_private_key_file(self.pkey_path)
      except Exception:
        pw = getpass.getpass('Password for key {}:')
        if(not pw):
          pw = None
        self.pkey = paramiko.Ed25519Key.from_private_key_file(
            self.pkey_path, password=pw)
    else:
      print('Error: SSH key for server login required.')
      sys.exit(1)

    if args.list is not None and args.list:
      self.__list_server()
      sys.exit(0)

    if args.name is None:
      print('Error: Name is required.')
      sys.exit(1)

    self.name = args.name[0]

    if args.shutdown is not None and args.shutdown:
      self.__shutdown_server()
      sys.exit(0)

    for arg in vars(args):
      if getattr(args, arg) is not None:
        for action in self.game.supported_actions():
          (name, _, has_param, callback) = action
          if name == arg:
            if not has_param:
              if getattr(args, arg):
                callback(self)
            else:
              callback(self, getattr(args, arg))

    self.game.actions_executed(self)

  def __get_all_game_server_droplets(self):
    manager = digitalocean.Manager(token=self.token)
    return manager.get_all_droplets()

  def __get_game_server_droplet(self):
    droplets = list(filter(lambda d: d.name == self.name, self.__get_all_game_server_droplets()))

    if len(droplets) == 0:
      print('Error: No droplet named {} found.'.format(self.name))
      sys.exit(1)

    return droplets[0]

  def __list_server(self):
    game_server_droplets = self.__get_all_game_server_droplets()

    num = len(game_server_droplets)

    pluralS = ''
    if (num != 1):
      pluralS = 's'

    print('Found {} {} server{}:'.format(num, self.game.name(), pluralS))
    for server in game_server_droplets:
      print('{} : {}'.format(server.name, server.ip_address))

  def __shutdown_server(self):
    print('Destroying {} server {}...'.format(self.game.name(), self.name))

    game_server_droplet = self.__get_game_server_droplet()

    game_server_droplet.destroy()

    print('{} server {} destroyed.'.format(self.game.name(), self.name))

  def __setup_client(self):
    if self.client is not None:
      return True

    game_server_droplet = self.__get_game_server_droplet()

    self.hostname = game_server_droplet.ip_address

    username = 'root'
    port = 22

    # now, connect and use paramiko Client to negotiate SSH2 across the connection
    try:
      self.client = paramiko.SSHClient()
      self.client.load_system_host_keys()
      self.client.set_missing_host_key_policy(IgnorePolicy())
      print('Connecting...')
      try:
          self.client.connect(
              self.hostname,
              port,
              username,
              pkey=self.pkey,
          )
      except Exception as e:
          pw = getpass.getpass('Password for private key wrong?: ')
          self.pkey = paramiko.Ed25519Key.from_private_key_file(
              str(self.pkey_path), password=pw)
          self.client.connect(
              self.hostname,
              port,
              username,
              pkey=self.pkey,
          )

      return True
    except Exception as e:
      print('Caught exception: %s: %s' % (e.__class__, e))
      try:
          self.client.close()
          pass
      except:
          pass
      sys.exit(1)

  def __client_guard(self):
    if self.client is None and not self.__setup_client():
      print('Error: No server available.')
      sys.exit(1)

  def create_droplet(self, droplet_size: str) -> str:
    game_server_droplets = list(
        filter(lambda d: d.name == self.name, self.__get_all_game_server_droplets()))
    if len(game_server_droplets) > 0:
      print('There exist already {} {} server with the name {}.'.format(
          len(game_server_droplets), self.game.name(), self.name))
      sys.exit(1)

    print('Creating {} server: {}'.format(self.game.name(), self.name))

    manager = digitalocean.Manager(token=self.token)
    keys = manager.get_all_sshkeys()

    droplet = digitalocean.Droplet(token=self.token,
                                   name=self.name,
                                   region='fra1',
                                   image='docker-20-04',
                                   size_slug=droplet_size,
                                   ssh_keys=keys,  # Add all keys
                                   backups=False)

    loading = ['\\', '-', '/', '|' ]
    loading_inc = 0
    droplet.create()

    droplet_created = False
    while not droplet_created:
      for action in droplet.get_actions():
          action.load()
          loading_inc += 1
          print('Creating droplet... ', str(loading[loading_inc % 4]), end='\r')
          if action.status == "completed":
            droplet_created = True
            break
          if action.status == "errored":
            print("Error when creating droplet.")
            sys.exit(1)

    # Request all droplets and find recently created droplet
    # We do this as the created droplet object is missing some information, e.g. ip address
    found_droplet = False
    droplets = manager.get_all_droplets()
    for d in droplets:
      if d.id == droplet.id:
          droplet = d
          found_droplet = True

    if(not found_droplet):
      print("Error: Could not setup droplet.")
      sys.exit(1)

    tag = digitalocean.Tag(token=self.token, name=self.game.name())
    tag.create() # create tag if not already created
    tag.add_droplets([droplet.id])

    self.hostname = droplet.ip_address

  def server_address(self) -> str:
    self.__client_guard()
    return self.hostname

  def exec_command(self, command: str):
    self.__client_guard()

    print('*** {}'.format(command))
    _, stdout, stderr = self.client.exec_command(command)
    print(stdout.read().decode())
    errors = stderr.read().decode()
    if errors:
      print('*** Errors')
      print(errors)

  def exec_commands(self, commands: list[str]):
    self.__client_guard()
    for command in commands:
      self.exec_command(command)

  def upload(self, localFilePath: str, serverTargetPath: str):
    self.__client_guard()

    sftp = self.client.open_sftp()

    print('*** Uploading {}'.format(localFilePath))
    sftp.put(localFilePath, serverTargetPath)

    sftp.close()

  def download(self, serverTargetPath: str, localFilePath: str):
    self.__client_guard()

    sftp = self.client.open_sftp()

    print('*** Downloading to {}'.format(localFilePath))
    sftp.get(serverTargetPath, localFilePath)

    sftp.close()
