from typing import Callable
from getpass import getpass
import os

from game import Game
from game_server_api import GameServerAPI
from game_server_manager import GameServerManager

class FoundryVTT(Game):

  def name(self) -> str:
    return 'FoundryVTT'

  def supported_actions(self) -> list[tuple[str, str, bool, Callable]]:
    return [
      ('create', 'Creates new empty Foundry VTT server.', False, self.create_server),
      ('download', 'Downloads zipped data to specified path', True, self.download_data),
      ('upload', 'Uploads zipped data', True, self.upload_data),
    ]
   
  def create_server(self, gsmAPI: GameServerAPI):
    username = input('Foundry Username: ')
    password = getpass(prompt='Foundry Password: ')
    adminKey = getpass(prompt='Admin Key: ')

    gsmAPI.create_droplet('s-2vcpu-2gb')
    gsmAPI.exec_commands([ 
      'sudo mkdir -p /opt/foundryvtt/data',
      f'docker run --name foundryvtt -d --env FOUNDRY_USERNAME="{username}" --env FOUNDRY_PASSWORD="{password}" --env FOUNDRY_ADMIN_KEY="{adminKey}" --publish 30000:30000/tcp --volume=/opt/foundryvtt/data:/data felddy/foundryvtt:release',
    ])

  def download_data(self, gsmAPI: GameServerAPI, localPath : str):     
    gsmAPI.exec_commands([
      'docker stop foundryvtt',
      'tar -czvf /opt/data.tar -C /opt/foundryvtt/ data'
    ])

    gsmAPI.download('/opt/data.tar', localPath)

    gsmAPI.exec_commands([
      'rm /opt/data.tar'
      'docker start foundryvtt'
    ])

  def upload_data(self, gsmAPI: GameServerAPI, localDataPath : str):
    gsmAPI.exec_commands([
      'docker stop foundryvtt'
    ])

    gsmAPI.upload(localDataPath, '/opt/data.tar')

    gsmAPI.exec_commands([
      'rm -r /opt/foundryvtt/data',
      'tar -xzvf /opt/data.tar -C /opt/foundryvtt/',
      'docker start foundryvtt',
      'rm /opt/data.tar'
    ])

  def actions_executed(self, gsmApi: GameServerAPI):
    print('Foundry VTT server created: {}:30000'.format(gsmApi.server_address()))

gsm = GameServerManager(FoundryVTT())
gsm.run()