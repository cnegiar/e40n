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
                    payload= self.bits_from_image(self.fname)
                    srctype= '00'
                else:           
                    payload = self.text2bits(self.fname) 
                    srctype='01'                   
            else:               
                length = len(self.monotone)
                for i in xrange (length):
                    payload[i]=1
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
        data = list(img.getdata())
        
        for coords in data: 
            x =coords[0]
            y= coords[1]
            if (x==255):
                bits.append(1)
            else: 
                bits.append(0)

            if (y==255):
                bits.append(1)
            else: 
                bits.append(0) 

        return bits 



    def get_header(self, payload_length, srctype): 
        # Given the payload length and the type of source 
        # (image, text, monotone), form the header
        header =''
        length= '{0:010b}'.format(payload_length)
        header = srctype + length
      
        return header 
