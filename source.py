# audiocom library: Source and sink functions
import common_srcsink as common
import Image
from graphs import *
import binascii
import random




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
            if self.fname is not None:
                if self.fname.endswith('.png') or self.fname.endswith('.PNG'):
                    payload = self.bits_from_image(self.fname)
                    srctype = '00'
                else:           
                    payload = self.text2bits(self.fname)
                    srctype = '01'
            else:               
                length = self.monotone
                for i in range (0, length):
                    payload.append(1)
                srctype='11'
           

            hdr=self.get_header (len(payload), srctype)
            for bit in hdr: 
                databits.append(int(bit))
            for bit in payload:
                databits.append(int(bit))
            
            return payload, databits

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



    def get_header(self, payload_length, srctype): 
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
        print '\tSource type: ', type
        print '\tPayload Length: ', str(payload_length)
        print '\tHeader:  [' + ', '.join(header) + ']'

        return header 
