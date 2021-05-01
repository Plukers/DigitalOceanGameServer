from abc import ABC, abstractmethod
from typing import Callable

from game_server_api import GameServerAPI

class Game:

  @abstractmethod
  def name(self) -> str:
    """Name of the game."""
    pass

  @abstractmethod
  def supported_actions(self) -> list[tuple[str, str, bool, Callable]]:
    """
    Returns supported list of supported actions:
    An action is defined by
    [
      name of action, 
      help for action,
      requires argument, 
      function to invoke if action is invoked (accepting optional argument if specified)
    ]
    """
    pass
   
  @abstractmethod
  def actions_executed(self, gsmApi: GameServerAPI):
    """Invoked after all actions have been executed"""
    pass
