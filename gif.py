#!/usr/bin/python3
import struct
import lzw

class GifTerminator(Exception):
    pass

class Gif:
    def __init__(self):
        self.frames = []

    def load(self,path):
        f = open(path,"rb")
        self.read_header(f)
        self.read_descriptor(f)
        if self.gct_flag: self.read_gct(f)
        self.images = []
        self.extensions = []
        try:
            while True:
                self.read_block(f)
        except GifTerminator:
            print("done")
        #except Exception as e:
        #    print("ERROR",e)

    def read_gct(self,f):
        self.gct = []
        fmt = "<BBB"
        for i in range(self.gct_entries):
            self.gct.append(struct.unpack(fmt,f.read(3)))

    def read_descriptor(self,f):
        fmt = "<HHBBB"
        sz = struct.calcsize(fmt)
        (self.width, self.height, packed, self.bg_idx, self.aspect) = struct.unpack(fmt,f.read(sz))
        self.gct_flag = (packed & 0x80) != 0
        self.sort_flag = (packed & 0x08) != 0
        self.color_bits = ((packed & 0x70) >> 4) + 1
        self.gct_entries = 2 ** ((packed & 0x07) + 1)

    def read_header(self,f):
        header = f.read(6)
        if header == b'GIF87a': 
            self.version = '87a'
        elif header == b'GIF89a':
            self.version = '89a'
        else:
            raise ValueError('Unrecognized GIF magic number {0}'.format(header))

    def read_blockstream(f):
        data = b''
        while True:
            sz = f.read(1)[0]
            if sz == 0: break
            data = data + f.read(sz)
        return data

    class Extension:
        def __init__(self,f):
            (intro,self.exttype)=struct.unpack('BB',f.read(2))
            if intro != 0x21:
                raise ValueError()
            self.data = Gif.read_blockstream(f)
            if self.exttype == 0x01:
                print("Plain text label",self.data)
            elif self.exttype == 0xfe:
                print("Comment:",self.data) 

    class Frame:
        def __init__(self,f):
            fmt="<BHHHHB"
            sz = struct.calcsize(fmt)
            (sep,self.left,self.top,self.w,self.h,packed) = struct.unpack(fmt,f.read(sz))
            if sep != 0x2C:
                raise ValueError("Expected 0x2c, got {0:x}".format(sep))
            self.lct_flag = (packed & 0x80) != 0
            self.interlace_flag = (packed & 0x40) != 0
            self.sort_flag = (packed & 0x20) != 0
            self.lct_entries = 2 ** ((packed & 0x07) + 1)
            if self.lct_flag:
                read_lct(f)
            self.min_code_sz = f.read(1)[0]
            d=Gif.read_blockstream(f)
            self.data = b''
            for j in lzw.decode(d,self.min_code_sz):
                self.data = self.data + j
            print("frame",self.left,self.top,self.w,self.h,"mincode",self.min_code_sz)

        def read_lct(self,f):
            self.lct = []
            fmt = "BBB"
            for i in range(self.lct_entries):
                self.lct.append(struct.unpack(fmt,f.read(3)))

    def read_block(self,f):
        blocktype = f.read(1)[0]
        f.seek(-1,1)
        if blocktype == 0x3B:
            raise GifTerminator()
        elif blocktype == 0x2C:
            self.frames.append(Gif.Frame(f))
        elif blocktype == 0x21:
            self.extensions.append(Gif.Extension(f))
        else:
            raise ValueError('Unknown block type {0:2x}'.format(blocktype))

if __name__ == '__main__':
    g = Gif()
    g.load('example.gif')
    print(g.version,g.width,g.height,g.color_bits)
