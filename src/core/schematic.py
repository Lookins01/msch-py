from   struct import pack 
from   zlib   import compress
from   typing import NamedTuple, Dict, List, Set, Any

from   .tile   import Tile
from   .block  import Block
from   .point2 import Point2 
from   .io     import ByteWriter, write_config


class Schematic:
    HEADER = (b'm', b's', b'c', b'h')

    def __init__(
            self, 
            tiles: List[Tile] = None, 
            tags: Dict[str, str] = None, 
            width: int = 0, 
            height: int = 0
    ) -> None:
        self.tiles: List[Tile] = tiles if tiles else []
        self.tags: Dict[str, str] = tags if tags else {}
        self.width: int = width
        self.height: int = height
        self.blocks: List[Block] = set()
    
    def add_tile(self, tile) -> None:
        self.tiles.append(tile)
        self._update_blocks()
    
    def remove_tile(self, tile_index) -> None:
        self.tiles.pop(tile_index)
        self._update_blocks()
    
    def write_to_msch(self, msch_filepath: str) -> None:
        with open(msch_filepath, 'wb') as file:

            # Check header
            for byte in self.HEADER:
                file.write(byte) 

            # Get version
            version = pack('b', 1)
            file.write(version)

            # Create stream for comfort read
            stream = ByteWriter()

            # Get width and height
            stream.write_short(self.width)
            stream.write_short(self.height)

            # Read tags
            stream.write_byte(len(self.tags))
            for tag_name, tag_value in self.tags.items():
                stream.write_utf(tag_name)
                stream.write_utf(tag_value)
            
            # Read blocks
            blocks = self.blocks
            stream.write_byte(len(blocks))
            for block in blocks:
                stream.write_utf(block.name)
            
            # Read total
            total = len(self.tiles) 
            stream.write_int(total)
            for tile in self.tiles:
                stream.write_byte(blocks.index(tile.block))
                position = stream.write_int(Point2.pack(*tile.pos))
                # Read config 
                stream.write_byte(tile.config_type)
                write_config(tile.config_type, tile.config, stream)
                stream.write_byte(tile.rotation)

            file.write(compress(stream.stream))


    def _update_blocks(self) -> None:
        self.blocks: List[Block] = list(set(tile.block for tile in self.tiles))
    
    def __dict__(self) -> Dict[str, Any]:
        self._update_blocks()
        schematic = {}
        schematic['tiles'] = [tile.__dict__() for tile in self.tiles]
        schematic['tags'] = self.tags 
        schematic['width'] = self.width 
        schematic['height'] = self.height
        schematic['blocks'] = [block.name for block in self.blocks]
        return schematic
