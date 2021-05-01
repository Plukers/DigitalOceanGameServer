from typing import Callable

from game import Game
from game_server_api import GameServerAPI
from game_server_manager import GameServerManager

class Minecraft(Game):

  def name(self) -> str:
    return 'Minecraft'

  def supported_actions(self) -> list[tuple[str, str, bool, Callable]]:
    return [
      ("create", "creates new empty minecraft server", False, self.create_server)
    ]
   
  def create_server(self, gsmAPI: GameServerAPI):
    gsmAPI.create_droplet('s-1vcpu-2gb')
    gsmAPI.exec_command('docker run -e EULA=TRUE -d -it -p 25565:25565 -e EULA=TRUE itzg/minecraft-server')

  def actions_executed(self, gsmApi: GameServerAPI):
    print("*** Minecraft server created: {}:25565".format(gsmApi.server_address()))

gsm = GameServerManager(Minecraft())
gsm.run()