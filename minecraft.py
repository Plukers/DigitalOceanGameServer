from typing import Callable

from game import Game
from game_server_api import GameServerAPI
from game_server_manager import GameServerManager
import os

class Minecraft(Game):

  def name(self) -> str:
    return 'Minecraft'

  def supported_actions(self) -> list[tuple[str, str, bool, Callable]]:
    return [
      ('create', 'creates new empty minecraft server', False, self.create_server),
      ('download', 'downloads whole minecraft server to specified path', True, self.download_server)
    ]
   
  def create_server(self, gsmAPI: GameServerAPI):
    gsmAPI.create_droplet('s-1vcpu-2gb')
    # gsmAPI.exec_command('docker run -e EULA=TRUE -d -it -p 25565:25565 -e EULA=TRUE itzg/minecraft-server')
    commands = [
      'sudo mkdir -p /opt/minecraft',
      'sudo chown 1000:1000 /opt/minecraft',
      'sudo docker run -d '
      '-p 25565:25565 '
      '-v /opt/minecraft:/data '
      '--name minecraft '
      '--restart=unless-stopped '
      '-e TYPE=FORGE '
      '-e EULA=TRUE '
      'itzg/minecraft-server']
    gsmAPI.exec_commands(commands)

  def download_server(self, gsmAPI: GameServerAPI(), localPath: str):
    commands = [
      'docker stop minecraft',
      'tar -cf opt/server.tar opt/minecraft']
      
    gsmAPI.exec_commands(commands)
    gsmAPI.download('opt/server.tar', os.path.join(localPath))
    command = 'docker start minecraft'
    sgmAPI.exec_command(command)



  def actions_executed(self, gsmApi: GameServerAPI):
    print('Minecraft server created: {}:25565'.format(gsmApi.server_address()))

gsm = GameServerManager(Minecraft())
gsm.run()