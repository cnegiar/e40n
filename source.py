# audiocom library: Source and sink functions
import common_srcsink as common
import Image
from graphs import *
import binascii
import random
from heapq import heappush, heappop, heapify
from collections import defaultdict



class Source:
    def __init__(self, monotone, filename=None):
        # The initialization procedure of source object
        self.monotone = monotone
        self.fname = filename
        print 'Source: '

    def process(self):
            # Form the databits, from the filename 
            databits =[]
            payload=[]
            srctype=0 
            huff_databits=[]
            if self.fname is not None:
                if self.fname.endswith('.png') or self.fname.endswith('.PNG'):
                    payload = self.bits_from_image(self.fname)
                    srctype = '00'
                else:           
                    payload = self.text2bits(self.fname)
                    srctype = '01'
                huff_databits, huffman_stats = self.huffman_encode(payload)
                hdr=self.get_header (len(huff_databits), len(payload) , srctype, huffman_stats)
            else:               
                length = self.monotone
                for i in range (0, length):
                    huff_databits.append(1)
                srctype='11'
                hdr= self.get_header(len(huff_databits), len(huff_databits),srctype, None)

           
            for bit in hdr: 
                databits.append(int(bit))
            for bit in huff_databits:
                databits.append(int(bit))

            return huff_databits, databits


 
    def encode(self, huff_map):
        heap = [[node, [symbol, ""]] for symbol, node in huff_map.items()]
        heapify(heap)
        while len(heap) > 1:
            low = heappop(heap)
            high = heappop(heap)
            for pair in low[1:]:
                pair[1] = '0' + pair[1]
            for pair in high[1:]:
                pair[1] = '1' + pair[1]
            heappush(heap, [low[0] + high[0]] + low[1:] + high[1:])
        return sorted(heappop(heap)[1:], key=lambda p: (len(p[-1]), p))
 

    def huffman_encode(self, payload):

        #Number of occurrences of each chunk of four
        huff_stats=defaultdict(int)
        huff_stat_arr=[]

        #Chunk of 4 to code
        huff_map={}
        huff_bits=[]

        databits =[]
        curr_index=0
        while curr_index<len(payload):
            chunk = ''
            arr=payload[curr_index:curr_index+4]
            for x in arr:
                chunk+=str(x)
            if chunk in huff_stats.keys():
                val=huff_stats.get(chunk)+1
                huff_stats[chunk]=val
            else:
                huff_stats[chunk]=1
            curr_index+=4

        
        huff_map= self.encode(huff_stats)
        huff_map=dict(huff_map)

        curr_index=0
        while curr_index<len(payload):
            chunk = ''
            arr=payload[curr_index:curr_index+4]
            for x in arr:
                chunk+=str(x)
            code = huff_map[chunk]

            for bit in code:
                databits.append(int(bit))
            curr_index+=4

        return databits, dict(huff_stats)    

    def text2bits(self, filename):
        bits =[]
        for line in open(filename, 'r'):
            for char in line: 
                bit = ord(char)
                binary = '{0:08b}'.format(bit)
                for bit in binary: 
                  bits.append(int(bit))

        return bits

    def bits_from_image(self, filename):
        bits=[]
        img = Image.open(filename,'r')
        img = img.convert('L')
        data = list(img.getdata())
        for coord in data:
            binCoord = '{0:08b}'.format(coord)
            for bit in binCoord:
              bits.append(int(bit))
        return bits


    def generate_patterns(self):
        patterns=[]
        for x in xrange(0, 16):
            bin= '{0:04b}'.format(x)
            patterns.append(bin)
        return patterns


    def get_header(self, payload_length, old_payload_len, srctype, huff_map): 
        # Given the payload length and the type of source 
        # (image, text, monotone), form the header
        header =''
        length= '{0:016b}'.format(payload_length)
        header = srctype + length
        type = "" 
        if srctype == '00': type = 'image' 
        elif srctype == '01': type = 'text'
        elif srctype == '11': type = 'monotone'
        else: type = 'unknown'
       
        four_bit_patterns=self.generate_patterns()

        if not (type=='monotone' or type=='unknown') :
            for pattern in four_bit_patterns:
                if pattern in huff_map.keys() :
                    occurrences = huff_map[pattern]
                    binary = format(occurrences, '011b')
                    header+=binary
                else:
                    for x in range(11):
                      header+='0'

        print '\tSource type: ', type
        print '\tCompressed Payload Length: ', str(payload_length)
        print '\tCompression Rate: ', str(float(payload_length)/old_payload_len)
        print '\tHeader:  [' + ', '.join(header) + ']'
        return header 
