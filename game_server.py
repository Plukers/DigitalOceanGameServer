import sys
from abc import ABC, abstractmethod

class GameServerManagerAPI:

  @abstractmethod
  def exec_command(self, command: str):
    """Executes the command on the game server."""
    pass

  @abstractmethod
  def exec_commands(self, commands: list[str]):
    """Executes the commands on the game server."""
    pass

  @abstractmethod
  def upload(self, localFilePath: str, serverTargetPath: str):
    """Uploads the local file to the target path on the server."""
    pass

  @abstractmethod
  def download(self, serverTargetPath: str, localFilePath: str):
    """Downloads the file from the target path on the server to local file path."""
    pass

class Game:

  @abstractmethod
  def name(self) -> str:
    """Name of the game."""
    pass

  @abstractmethod
  def size(self) -> str:
    """Size configuration of the droplet, e.g. s-1vcpu-1gb"""
    pass

  @abstractmethod
  def create_server(self, gsmAPI: GameServerManagerAPI):
    """Create's the server."""
    pass

  @abstractmethod
  def upload_to_server(self, gsmAPI: GameServerManagerAPI, pathToUpload: str):
    """Upload files from pathToUpload (save_files, configuration, ...) to the server."""
    pass

  @abstractmethod
  def download_from_server(self, gsmAPI: GameServerManagerAPI, pathToDownloadTo: str):
    """Download files (save_files, configuration, ...) from the server and save results in pathToDownloadTo"""
    pass


class GameServerManager(GameServerManagerAPI):
  game = None

  def __init__(self, game: Game):
    self.game = game

  def run(self):
    """Parses arguments and manages game server for game accordingly."""
    pass

  def exec_command(self, command: str):
    print("*** Error: Interface not implemented.")
    sys.exit(1)

  def exec_commands(self, commands: list[str]):
    print("*** Error: Interface not implemented.")
    sys.exit(1)

  def upload(self, localFilePath: str, serverTargetPath: str):
    print("*** Error: Interface not implemented.")
    sys.exit(1)

  def download(self, serverTargetPath: str, localFilePath: str):
    print("*** Error: Interface not implemented.")
    sys.exit(1)
