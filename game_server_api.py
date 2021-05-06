from abc import ABC, abstractmethod

class GameServerAPI:

  @abstractmethod
  def create_droplet(self, droplet_size: str) -> str:
    """Creates a new droplet with the given size."""
    pass

  @abstractmethod
  def server_address(self) -> str:
    """Returns address of server."""
    pass

  @abstractmethod
  def exec_command(self, command: str):
    """Executes the command on the game server."""
    pass

  @abstractmethod
  def exec_commands(self, commands: list[str]):
    """Executes the commands on the game server."""
    pass

  @abstractmethod
  def upload(self, localPath: str, serverPath: str):
    """Uploads the local file to the path on the server."""
    pass

  @abstractmethod
  def download(self, serverPath: str, localPath: str):
    """Downloads the file from the serverr to local file path."""
    pass