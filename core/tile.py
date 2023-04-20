from typing import List, Any, Tuple, Dict

from .block import Block


class Tile:

    def __init__(
            self, 
            block: Block, 
            x: int, 
            y: int, 
            rotation: int, 
            config_type: int, 
            config: Any): 
        self.block: Block = block
        self.width: int = block.width
        self.height: int = block.height
        self.x: int = x
        self.y: int = y
        self.rotation: int = rotation
        self.config_type: int = config_type
        self.config: Any = config

    @property
    def pos(self) -> Tuple[int, int]:
        return self.x, self.y

    def __dict__(self) -> Dict[str, Any]:
        tile = {}
        tile['block'] = self.block.name 
        tile['width'] = self.width
        tile['height'] = self.height 
        tile['x'] = self.x 
        tile['y'] = self.y
        tile['rotation'] = self.rotation 
        tile['config_type'] = self.config_type
        tile['config'] = self.config if not isinstance(self.config, dict) else {i: j if not isinstance(j, bytes) else j.decode('UTF-8') for i, j in self.config.items()} 
        return tile

