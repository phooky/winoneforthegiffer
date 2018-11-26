use std::vec::Vec;
use std::iter::Iterator;
use std::cmp::max;
use std::fs::File;
use std::io::BufReader;
use std::io::Read;
use std::io::ReadExt;

struct Color {
    r : u8,
    g : u8,
    b : u8
}

struct ImageBuffer {
    x : u16,
    y : u16,
    d : Vec<Color>
}

impl ImageBuffer {
    fn new(x : u16, y : u16) {
        ImageBuffer { x:x, y:y, d:Vec::new() }
    }
}
    
struct VariableBitStream<'a> {
    src : &'a mut Iterator<Item=u8>,
    cur : u8,
    bits : usize,
}

impl<'a> VariableBitStream<'a> {
    fn new(src : &'a mut Iterator<Item=u8>) -> VariableBitStream<'a> {
        VariableBitStream { src : src, cur: 0, bits: 0 }
    }
    fn read_bits(&mut self, count : usize) -> Option<u16> {
        let mut v = 0u16;
        let mut so_far = 0;
        while so_far < count {
            if self.bits == 0 {
                match self.src.next() {
                    None => return None,
                    Some(n) => { self.bits = 8; self.cur = n; },
                }
            }
            let transfer_sz = max(self.bits, count - so_far);
            let transfer_mask = 0xffu8 >> (8-transfer_sz);
            v = v | (((self.cur & transfer_mask) as u16) << so_far);
            so_far = so_far + transfer_sz; self.bits = self.bits - transfer_sz;
            self.cur = self.cur >> transfer_sz;
        }
        Some(v)
    }
}
 
struct LzwTable {
    code_size : u8,
    code_len : u8,
    clear_code : u16,
    eoi_code : u16,
    last : Vec<u8>,
    dict : Vec<Vec<u8>>,
}

enum DecodeResult {
    Data(Vec<u8>),
    None,
    EndOfImage
}

impl LzwTable {
    fn new(code_size : u8) -> LzwTable {
        let mut l = LzwTable {
            code_size : code_size,
            code_len : code_size + 1,
            clear_code : 1 << code_size,
            eoi_code : (1 << code_size) + 1,
            last : Vec::new(),
            dict : Vec::with_capacity(0x1000),
        };
        for idx in 0..(1<<code_size) {
            l.dict.push(vec![idx as u8])
        };
        // Empty entries for clear code and eoi code
        l.dict.push(Vec::new());
        l.dict.push(Vec::new());
        l
    }
    fn clear(&mut self) {
        self.dict.truncate(self.eoi_code as usize);
        self.last = Vec::new();
        self.code_len = self.code_size + 1;
    }
    fn decode(&mut self,code : u16) -> DecodeResult {
        if code == self.clear_code { self.clear(); DecodeResult::None }
        else if code == self.eoi_code { DecodeResult::EndOfImage }
        else {
            let rv = if (code as usize) < self.dict.len() {
                &self.dict[code as usize]
            } else {
                let first_elem = self.last[0];
                self.last.push(first_elem); &self.last
            };
            DecodeResult::Data(rv.clone())
        }
    }
}

struct GifFileBlock {
    f : File,
    remains_in_block : u8,
    done : bool,
}

impl GifFileBlock {
    fn new(f) -> GifFileBlock {
        GifFileBlock(f,0,false)
    }
}


impl Iterator for GifFileBlock {
    type Item = u8;
    fn next(&mut self) -> Option<u8> {
        if remains_in_block > 0 {
            match self.f.read(&mut self.buf) {
            Err(error) => panic!("Can't read: {}", error),
            Ok(0) => None,
            Ok(result) => Some(str::from_utf8(&self.buf[0..result]).unwrap().to_string()),
        }
    }

    
}

fn process(f : File) {

    let mut bytes = f.bytes();
}

fn main() {
    match (File::open("~/winoneforthegiffer/example.gif")) {
        Ok(f) => process(f),
        Err(e) => panic!("Could not open gif"),
    } 
    let mut lzw = LzwTable::new(8);
    lzw.decode(255);
    lzw.decode(15);
    println!("Hello, world!");
}
