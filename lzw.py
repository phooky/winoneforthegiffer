#!/usr/bin/python

class EndOfImage(Exception):
    pass

class LZWDict:
    def __init__(self,code_size):
        self.code_size = code_size
        self.clear_code = 2**code_size
        self.eoi_code = self.clear_code + 1
        self.clear()

    def clear(self):
        self.code_dict = { n: bytes([n]) for n in range(2**self.code_size) }
        self.last = b''
        self.code_len = self.code_size + 1
        self.next_code = self.eoi_code + 1

    def decode(self,code):
        if code == self.clear_code:
            self.clear()
            return b''
        elif code == self.eoi_code:
            raise EndOfImage()
        try:
            rv = self.code_dict[code]
        except:
            # assert?
            if (code != self.next_code): print("violation",code,self.next_code)
            rv = self.last + bytes([self.last[0]])
        # insert code
        if b'' == self.last:
            pass
        else:
            self.code_dict[self.next_code] = self.last + bytes([rv[0]])
            self.next_code = self.next_code + 1
        if self.next_code >= 2**self.code_len and self.code_len < 12:
            self.code_len = self.code_len + 1
        self.last = rv
        return rv

def decode(data,code_size):
    d = LZWDict(code_size)
    idx = 0
    bidx = 0
    try:
        while idx < len(data):
            code = 0
            for i in range(d.code_len):
                code = code + (((data[idx]>>bidx) & 0x01) << i)
                bidx = bidx + 1
                if bidx == 8: bidx, idx = 0, idx+1
            #print("code",code)
            yield d.decode(code)
            # start new code
    except EndOfImage:
        pass



