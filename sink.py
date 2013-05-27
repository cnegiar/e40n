# audiocom library: Source and sink functions
import common_srcsink
import Image
from graphs import *
import binascii
import random
from heapq import heappush, heappop, heapify
from collections import defaultdict



class Sink:
    def __init__(self):
        # no initialization required for sink 
        print 'Sink:'

    def process(self, recd_bits):
        # Process the recd_bits to form the original transmitted
        # file. 
        # Here recd_bits is the array of bits that was 
        # passed on from the receiver. You can assume, that this 
        # array starts with the header bits (the preamble has 
        # been detected and removed). However, the length of 
        # this array could be arbitrary. Make sure you truncate 
        # it (based on the payload length as mentioned in 
        # header) before converting into a file.
        
        # If its an image, save it as "rcd-image.png"
        # If its a text, just print out the text
        
        # Return the received payload for comparison purposes

        header_bits=[]
        rcd_payload=[]
        huffman_stats={}

        #Since payload size is forced into a 16-bit binary number and srctype is two digits + 160 for the huff stats
        for i in range (0, 178):
            header_bits.append(recd_bits[i])

        srctype, payload_length = self.read_header(header_bits)

        print recd_bits

        if srctype !=2 : 
            #Start at 178 since that's where header ends, and go for payload length counts (so to payload length +178)
            for i in range (178,payload_length+178):
                rcd_payload.append(recd_bits[i])
            huffman_stats=self.read_stats(header_bits[18:])
            huff_decoded_bits= self.huff_decode(rcd_payload, huffman_stats)
        else : 
            for i in range(18, payload_length+18):
                rcd_payload.apend(recd_bits[i])

        if srctype == 0:
            self.image_from_bits(huff_decoded_bits, 'rcd-image.png')
        elif srctype==1: 
            text= self.bits2text(huff_decoded_bits)
            print "\tText recd:", text
           
        return rcd_payload


    def read_stats(self,header_stats):
        i=0
        pattern_index=0
        huff_stats={}
        patterns = self.generate_patterns()
        while i< len(header_stats):
            freq= ''
            for x in xrange(10):
                freq+= str(header_stats[i+x])
            freq=int(freq,2)
            pattern = patterns[pattern_index]
            if freq != 0 : 
                huff_stats[pattern]= freq
            i+=10
            pattern_index+=1
        return huff_stats

    def generate_patterns(self):
        patterns=[]
        for x in xrange(0, 16):
            bin= '{0:04b}'.format(x)
            patterns.append(bin)
        return patterns


    def rebuild_tree(self, huff_map):
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

    def huff_decode(self, payload, huff_stats):
        decoded_bits=[]
        huff_map = dict(self.rebuild_tree(huff_stats))
        x = 0
        chunk=''
        while x< len(payload):
            i=1
            val = str(payload[x])
            while val not in huff_map.values():
                val+= str(payload[x+i])
                i+=1
            chunk=val
            decoded=''
            for key, value in huff_map.iteritems():
               if value == chunk:
                decoded=key
            for bit in decoded:
                decoded_bits.append(int(bit))
            x+=i
        return decoded_bits


    def bits2text(self, bits):
        text = ''
        i=0
        # Since there are 8 bits per character encoding (see source)
        for index in range(len(bits)/8):
            curr = ''
            for i in range(i, i+8):
                curr += str(bits[i])
            ascii_val= int(curr,2)
            char = chr(ascii_val)
            text+=char
            i+=1

        return  text

    def image_from_bits(self, bits,filename):
        # Convert the received payload to an image and save it
        # No return value required .
        coord_arr=[]
        i=0
        encoding = 0
        
        while (i < len(bits)):
            enc_raw = ''.join(str(x) for x in bits[i:i+8])
            encoding = int(enc_raw, 2)
            coord_arr.append(encoding)
            i += 8
        img = Image.new('L', [32,32])

        img.putdata(coord_arr)
        img.save(filename, 'PNG')

      


    def read_header(self, header_bits): 
        # Given the header bits, compute the payload length
        # and source type (compatible with get_header on source)
	srctype = header_bits[0]+ header_bits[1]
        payload_length = ''
        for i in xrange (2,18):
            payload_length += str(header_bits[i])
        payload_length = int(payload_length, 2)

        print '\tRecd header: [' + ', '.join(str(x) for x in header_bits) + ']'
        type = ''
        if srctype == 0: type = 'image' 
        elif srctype == 1: type = 'text'
        elif srctype == 2: type = 'monotone'
        else: type = 'unknown'

        print '\tSource type: ', type
        print '\tLength from header: ', payload_length
        print '\tRecd', payload_length, 'data bits:'

        return srctype, payload_length
