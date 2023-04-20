from zlib   import compress, decompress
from struct import pack, unpack


class ByteReader:

    def __init__(self, stream):
        self.stream = decompress(stream)
        self.offset = 0 

    def read(self, bytes_count: int = 1):
        bytez = self.stream[self.offset:self.offset+bytes_count]
        self.offset += bytes_count
        return bytez

    def read_short(self):
        return unpack('>h', self.read(2))[0]
    
    def read_float(self):
        return unpack('>f', self.read(2))[0]
    
    def read_double(self):
        return unpack('>d', self.read(2))[0]

    def read_ushort(self):
        return unpack('>H', self.read(2))[0]

    def read_byte(self):
        return unpack('>b', self.read(1))[0]
    
    def read_int(self):
        return unpack('>i', self.read(4))[0]

    def read_utf(self):
        utf_size = self.read_ushort()
        utf_raw = self.read(utf_size)
        utf = utf_raw.decode('UTF-8')
        return utf


class ByteWriter:

    def __init__(self, stream = b''):
        self.stream = stream

    def write(self, bytez: bytes):
        self.stream += bytez

    def write_short(self, short):
        self.write(pack('>h', short))
    
    def write_float(self, fload):
        self.write(pack('>f', fload))
    
    def write_double(self, double):
        self.write(pack('>d', double))

    def write_ushort(self, ushort):
        self.write(pack('>H', ushort))

    def write_byte(self, byte):
        self.write(pack('>b', byte))
    
    def write_int(self, integer):
        self.write(pack('>i', integer))

    def write_utf(self, utf):
        self.write_ushort(len(utf.encode('UTF-8')))
        self.write(utf.encode('UTF-8'))


def write_config(type, config, stream):
    if type == 0:
        return None
    elif type == 1:
        stream.write_int(config)
    elif type == 2:
        stream.write_long(config)
    elif type == 3:
        stream.write_float(config)
    elif type == 4:
        stream.write_utf(config)
    elif type == 5:
        stream.write_byte(config[0])
        stream.write_short(config[1])
    elif type == 6:
        steam.write_short(len(config))
        for integer in range(config):
            stream.write_int(integer)
    elif type == 7:
        stream.write_int(config[0])
        stream.write_int(config[1])
    elif type == 8:
        steam.write_byte(len(out))
        for integer in range(config):
            stream.write_int(integer)
    elif type == 9:
        stream.write_byte(config[0])
        stream.write_utf(config[1])
    elif type == 10:
        stream.write_bool(config)
    elif type == 11:
        stream.write_double(config)
    elif type == 12:
        stream.write_int(config)
    elif type == 13:
        stream.write_short(config) 
    elif type == 14: 
        config = get_config_bytes(config)
        stream.write_int(len(config))
        stream.write(config)
    elif type == 15:
        stream.write_byte(config)

def get_config_bytes(config):
    config_bytes = ByteWriter()
    config_bytes.write_byte(1)
    config_bytes.write_int(config['code_lenght']) 
    config_bytes.write(config['code'].encode('UTF-8')) 
    config_bytes.write_int(config['total_lenght'])
    for t in config['total']:
        config_bytes.write_utf(t['name'])
        config_bytes.write_short(t['x'])
        config_bytes.write_short(t['y'])
    return compress(config_bytes.stream)
