from typing import Callable
import os

from game import Game
from game_server_api import GameServerAPI
from game_server_manager import GameServerManager

class Factorio(Game):

  def name(self) -> str:
    return 'Factorio'

  def supported_actions(self) -> list[tuple[str, str, bool, Callable]]:
    return [
      ('create', 'creates new empty factorio server', False, self.create_server),
      ('upload_save', 'uploads the given save file', True, self.upload_save)
    ]
   
  def create_server(self, gsmAPI: GameServerAPI):
    gsmAPI.create_droplet('s-1vcpu-1gb')
    commands = [ 
      'sudo mkdir -p /opt/factorio', 
      'sudo chown 845:845 /opt/factorio',
      'sudo docker run -d -p 34197:34197/udp -p 27015:27015/tcp -v /opt/factorio:/factorio --name factorio --restart=always factoriotools/factorio',
    ]
    gsmAPI.exec_commands(commands)

  def upload_save(self, gsmAPI: GameServerAPI, savePath):
    commands = [
      'docker stop factorio',
      'rm /opt/factorio/saves/*'
    ]
    gsmAPI.exec_commands(commands)

    gsmAPI.upload(savePath, os.path.join('/opt/factorio/saves', os.path.basename(savePath)))

    gsmAPI.exec_command('docker start factorio')

  def actions_executed(self, gsmApi: GameServerAPI):
    print('Factorio server created: {}:34197'.format(gsmApi.server_address()))

gsm = GameServerManager(Factorio())
gsm.run()