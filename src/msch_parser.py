import os
import sys
import json
from   struct    import unpack
from   zlib      import decompress
from   typing    import List, Dict

from   core.tile      import Tile
from   core.block     import Blocks 
from   core.point2    import Point2
from   core.schematic import Schematic 
from   core.io        import ByteReader


def read_config_bytez(stream, config_type):
    if config_type == 0:
        return None
    elif config_type == 1:
        return stream.read_int()
    elif config_type == 2:
        return stream.read_long()
    elif config_type == 3:
        return stream.read_float()
    elif config_type == 4:
        return stream.read_utf()
    elif config_type == 5:
        return (stream.read_byte(), stream.read_short())
    elif config_type == 6:
        size = steam.read_short()
        out = []
        for _ in range(size):
            out.append(stream.read_int())
        return out 
    elif config_type == 7:
        return (stream.read_int(), stream.read_int())
    elif config_type == 8:
        size = steam.read_byte()
        out = []
        for _ in range(size):
            out.append(stream.read_int())
        return out 
    elif config_type == 9:
        return (stream.read_byte(), stream.read_utf())
    elif config_type == 10:
        return stream.read_bool()
    elif config_type == 11:
        return stream.read_double()
    elif config_type == 12:
        return stream.read_int()
    elif config_type == 13:
        return stream.read_short() 
    elif config_type == 14: 
        blen = stream.read_int()
        bytez = stream.stream[stream.offset:stream.offset+blen]
        stream.offset += blen
        return bytez
    elif config_type == 15:
        return stream.read_byte()

def read_config(stream, config_type):
    config_raw = read_config_bytez(stream, config_type)
    config = None  
    if config_type == 14:
        config = {}
        config_stream = ByteReader(config_raw)
        # Skip version for now
        config_stream.read_byte()
        code_len = config_stream.read_int()
        config['code_lenght'] = code_len
        code = config_stream.read(code_len)
        config['code'] = code.decode('UTF-8') 
        total = config_stream.read_int()
        config['total_lenght'] = total
        config['total'] = [] 
        for _ in range(total):
            name = config_stream.read_utf()
            x = config_stream.read_short()
            y = config_stream.read_short()
            config['total'].append({'name': name, 'x': x, 'y': y}) 

    return config if config else config_raw


def check_header(file_stream):
    for byte in Schematic.HEADER:
        if byte != file_stream.read(1):
            print('ERROR: Wrong header. No .msch file was provided.',
                  file=sys.stderr)
            exit(1)


def read_schematic_file(filepath: str):
    with open(filepath, 'rb') as file:

        # Check header
        check_header(file) 
        
        # Get version
        version = unpack('b', file.read(1))[0]

        # Create stream for comfort read
        stream = ByteReader(file.read())
        
        # Get width and height
        width = stream.read_short()
        height = stream.read_short()

        # Read tags
        tags_count = stream.read_byte()
        tags = {}
        for _ in range(tags_count):
            tag_name = stream.read_utf()
            tag_value = stream.read_utf()
            tags[tag_name] =  tag_value
        
        # Read blocks
        blocks_count = stream.read_byte()
        blocks = []
        for _ in range(blocks_count):
            block_name = stream.read_utf()
            try:
                blocks.append(Blocks[block_name])
            except KeyError:
                print(f'ERROR: No found \'{block_name}\' in schematic.Blocks')
                exit(1)

        # Read total
        total = stream.read_int()
        tiles = []
        for i in range(total):
            block = blocks[stream.read_byte()]
            position = stream.read_int()
            x = Point2.x(position)
            y = Point2.y(position)
            # Read config 
            config_type = stream.read_byte()
            config = read_config(stream, config_type)
            rotation = stream.read_byte() 
            tiles.append(Tile(block, x, y, rotation, config_type, config))  

    schematic = Schematic(tiles, tags, width, height) 

    schematic_filepath = os.path.split(filepath)[-1].split('.')[0] + '.json'

    with open(schematic_filepath, 'w') as file:
        json.dump(schematic.__dict__(), file, indent=4)

    print(f'`{schematic_filepath}` was written successfully.')


if __name__ == "__main__":

    if len(sys.argv) <= 1:
        print('ERROR: No input file was profided', 
              file=sys.stderr)
        exit()

    read_schematic_file(sys.argv[1])
