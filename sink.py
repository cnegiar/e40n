# audiocom library: Source and sink functions
import common_srcsink
import Image
from graphs import *
import binascii
import random


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

        #Since header is forced into a 10-bit binary number and srctype is two digits
        for i in range (0, 12):
            header_bits.append(recd_bits[i])

        srctype, payload_length = self.read_header(header_bits)
       
        #Start at 12 since that's where header ends, and go for payload length counts (so to payload length +12)
        for i in range (12,payload_length+12):
            rcd_payload.append(recd_bits[i])

        if srctype == 0:
            self.image_from_bits(rcd_payload, 'rcd-image.png')
        elif srctype==1: 
            text= self.bits2text(rcd_payload)
            print text
           
        return rcd_payload

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
        encoding_2 = 0
        while (i < len(bits)-17):
            encoding = bits[i:i+8]
            encoding_2 = bits[i+8:i+16]
            # if (bits[i]):
            #     encoding = 255
            # else: 
            #     encoding = 0
            # if (bits[i+1] ): 
            #     encoding_2= 255
            # else : 
            #     encoding_2 = 0
            i+=16
            coord_tuple= (encoding, encoding_2)
            coord_arr.append(coord_tuple)
        img = Image.new('LA', [32,32])
        img.putdata(coord_arr)
        img.save(filename, 'PNG')

      

    def read_header(self, header_bits): 
        # Given the header bits, compute the payload length
        # and source type (compatible with get_header on source)


        srctype= header_bits[0]+ header_bits[1]
        payload_length=''
        for i in range (2,len(header_bits)):
            payload_length += str(header_bits[i])
      
        payload_length = int(payload_length, 2)
 
        print '\tRecd header: ', header_bits
        print '\tLength from header: ', payload_length
        print '\tSource type: ', srctype
        return srctype, payload_length