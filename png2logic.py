import os
import sys
import json
from   typing import List, Dict
from   struct import pack, unpack
from   zlib import decompress, compress

import PIL
from   PIL import Image

from   core.tile      import Tile
from   core.point2    import Point2 
from   core.schematic import Schematic 
from   core.io        import ByteWriter
from   core.block     import Blocks, Block


RENDER_CODE = 'set WIDTH 176\nset HEIGHT 176\nset connection 0\ngetlink block_link connection\nsensor block_type block_link @type\njump 22 notEqual block_type @memory-bank\nset i 0\njump 22 greaterThanEq i 512\nread pixel block_link i\nop and r pixel 255\nop shr pixel pixel 8\nop and g pixel 255\nop shr pixel pixel 8\nop and b pixel 255\nop shr pixel pixel 16\nop and x pixel 255\nop shr y pixel 8\ndraw color b g r 255 0 0\ndraw rect x y 1 1 0 0\nop add i i 1\ndrawflush display1\njump 7 always x false\nop add connection connection 1\njump 3 lessThanEq connection 110\nend'


def compare(point1, point2):
    return point1 if point1[0] > point2[0] else point2 


def get_unused_block(schematic, block):
    size = len(schematic.tiles)
    points = []
    for _ in range(size):
        point = Point2(-1, -1), None
        for i in range(size):
            if schematic.tiles[i].block.name == block.name:
                new_point = Point2(*schematic.tiles[i].pos), i
                if new_point not in points:
                    point = compare(new_point, point)
        points.append(point)
        yield point[1]


def write_image_to_schematic_file(image_path: str) -> None:
    
    schematic = Schematic(width=36, height=14)
    
    # add logic-processors to schematic
    for i in range(5):
        for j in range(7):
            block = Blocks['logic-processor']
            x = i * 6
            y = j * 2
            total_lenght = 1 if i >= 4 else 2
            total = [{'name': 'bank1', 'x': 2, 'y': 0}] 
            if i <= 4:
                total.append({'name': 'bank2', 'x': 4, 'y': 0})
            config = {'code': '', 
                      'code_lenght': 0, 
                      'total_lenght': total_lenght, 
                      'total': total
            }
            tile = Tile(block, x, y, 0, 14, config)
            schematic.add_tile(tile)
    
    # add two lines of memory-bank to schematic
    for j in range(7):
        block = Blocks['memory-bank']
        y = j * 2
        for i in range(5):
            x = i * 6 + 2
            tile = Tile(block, x, y, 0, 0, None)
            schematic.add_tile(tile)

        for i in range(4):
            x = i * 6 + 4
            tile = Tile(block, x, y, 0, 0, None) 
            schematic.add_tile(tile)
    
    # add two vertical line of liquid-source to schematic
    for i in range(2):
        for j in range(14):
            block = Blocks['liquid-source']
            x = 28 + (i * 7)
            tile = Tile(block, x, j, 0, 5, [4, 3])
            schematic.add_tile(tile)

    # add two horizontal line of liquid-source to schematic
    for i in range(6):
        for j in range(2):
            block = Blocks['liquid-source']
            x = i + 29
            y = j * 13
            tile = Tile(block, x, y, 0, 5, [4, 3])
            schematic.add_tile(tile)

    # add logic-display to schematic
    schematic.add_tile(Tile(Blocks['large-logic-display'], 31, 3, 0, 0, None))
    
    # add 4 render hyper-processors to schematic
    for i in range(2):
        for j in range(2):
            block = Blocks['hyper-processor']
            x = 30 + (i * 3)
            y = 8 + (j * 3)
            config = {'code': RENDER_CODE, 
                      'code_lenght': len(RENDER_CODE), 
                      'total_lenght': 1, 
                      'total': [{'name': 'display1', 'x': 31 - x, 'y': 3 - y}]
            }
            tile = Tile(block, x, y, 0, 14, config)
            schematic.add_tile(tile)
    

    # add image information to logic-processors in schematic
    image = Image.open(image_path) 
    
    # resize image if it more than 176x176
    if image.height > 176 or image.width > 176:
        image = image.resize((176, 176), Image.Resampling.BILINEAR)
    
    data = list(image.getdata())
    logic_processor_iter = get_unused_block(schematic, Blocks['logic-processor'])
    pixel_index = 0

    while data:

        processor_index = next(logic_processor_iter) 
        instructions_count = 0 
        code = ''
        bank_index = 1
        cell_index = 0
        
        while instructions_count <= 999 and data:

            x = int(pixel_index % image.width)
            y = 175 - (pixel_index // image.width)
            
            pixel = data.pop(0)
            color = pixel[0] << (8 * 2) | pixel[1] << (8 * 1) | pixel[2] 

            cell_value =  0x000000000000 | color
            cell_value |= y << (8*5) | x << (8*4)

            code += f'write {cell_value} bank{bank_index} {cell_index}\n'
            instructions_count += 1

            pixel_index += 1

            cell_index += 1
            if cell_index >= 512:
                if schematic.tiles[processor_index].config['total_lenght'] <= 1:
                    break
                else:
                    bank_index += 1
                    cell_index = 0

        schematic.tiles[processor_index].config['code'] = code
        schematic.tiles[processor_index].config['code_lenght'] = len(code)
    
    # add memory-banks link to hyper-processors
    hyper_processor_iter = get_unused_block(schematic, Blocks['hyper-processor'])
    memory_bank_iter = get_unused_block(schematic, Blocks['memory-bank'])
    while i := next(hyper_processor_iter):
        for _ in range(16):
            index = next(memory_bank_iter)
            if not index:
                break
            memory_bank = schematic.tiles[index]
            x = memory_bank.x - schematic.tiles[i].x
            y = memory_bank.y - schematic.tiles[i].y
            schematic.tiles[i].config['total_lenght'] += 1
            schematic.tiles[i].config['total'].append({'name': 'memory-bank', 'x': x, 'y': y})
    
    
    output_filepath = (os.path.split(image_path))[-1].split('.')[0] + '.msch' 

    schematic.tags['name'] = output_filepath.split('.')[0]
    schematic.tags['description'] = 'Generated by msch-py'

    schematic.write_to_msch(output_filepath)

    print('Generate', output_filepath)


if __name__ == '__main__':

    if len(sys.argv) <= 1:
        print('ERROR: No input file was profided')
        exit()

    write_image_to_schematic_file(sys.argv[1])
