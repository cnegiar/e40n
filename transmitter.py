import math
import common_txrx as common
import numpy
import hamming_db as ham

class Transmitter:

    def __init__(self, carrier_freq, samplerate, one, spb, silence):#, cc_len):
        self.fc = carrier_freq  # in cycles per sec, i.e., Hz
        self.samplerate = samplerate
        self.one = one
        self.spb = spb
        self.silence = silence
        #self.cc_len = cc_len
        print 'Transmitter: '

    def hamming_encoding(self, databits, is_header):
        coded_bits = []
        coding_len = 3 if is_header is True else self.cc_len
        n, k, index, G = ham.gen_lookup(coding_len)
        while len(databits)%k != 0:
            databits.append(0)
        for x in xrange(0, len(databits), k):
            chunk = databits[x:x+k]
            coded_chunk = numpy.dot(chunk, G)
            for y in xrange(len(coded_chunk)):
                if coded_chunk[y]%2 == 0: coded_chunk[y] = 0
                else: coded_chunk[y] = 1
            coded_bits = numpy.append(coded_bits, coded_chunk)
        return index, coded_bits

    def encode(self, databits):
        encoding_options = [[3,1],[7,4],[15,11],[31,26]]
        index, coded_data = self.hamming_encoding(databits, False)
        # header is 32 bits:
        # first 30 bits = length of databits+header, last 2 bits = encoding tyoe
        closest_encode = min(encoding_options, key=lambda x:abs(x[0]-self.cc_len))
        encoding_index = numpy.binary_repr(encoding_options.index(closest_encode), width=2)
        length = numpy.binary_repr(len(coded_data), width=30)
        header_str = length + encoding_index
        header = []
        for bit in header_str:
            header.append(int(bit,2))
        index, coded_header = self.hamming_encoding(header, True)
        ##### TEST #####
        print "ORIGINAL HEAD: " + str(list(int(x) for x in header))
        #print "ORIGINAL DATA: " + str(list(int(x) for x in databits))
        ##### END TEST #####
        return numpy.append(coded_header, coded_data)

    def add_preamble(self, databits):
        '''
        Prepend the array of source bits with silence bits and preamble bits
        The recommended preamble bit sequences are 
        [1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1]
        OR
        [1,1,1,1,1,0,1,1,1,1,0,0,1,1,1,0,1,0,1,1,0,0,0,0,1,0,1,1,1,0,0,0,1,1,0,1,1,0,1,0,0,1,0,0,0,1,0,0,1,1,0,0,1,0,1,0,1,0,0,0,0,0,0]
        The output should be the concatenation of arrays of
        [silence bits], [preamble bits], and [databits]
        '''
        databits_with_preamble=[]
        for x in xrange (self.silence):
            databits_with_preamble.append(0)
        preamble_bits = [1,1,1,1,1,0,1,1,1,1,0,0,1,1,1,0,1,0,1,1,0,0,0,0,1,0,1,1,1,0,0,0,1,1,0,1,1,0,1,0,0,1,0,0,0,1,0,0,1,1,0,0,1,0,1,0,1,0,0,0,0,0,0]
        #preamble_bits= [1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1]
        for bit in preamble_bits:
            databits_with_preamble.append(bit)
        for bit in databits:
            databits_with_preamble.append(bit)
        print "\tSent Preamble:  " + str(preamble_bits)
        return databits_with_preamble

    def bits_to_samples(self, databits_with_preamble):
        '''
        Convert each bits into [spb] samples. 
        Sample values for bit '1', '0' should be [one], 0 respectively.
        Output should be an array of samples.
        '''
        samples=[]
        for bit in databits_with_preamble:
            if bit==0:
                for x in range (self.spb):
                    samples.append(0)
            else: 
                for x in range (self.spb):
                    samples.append(self.one)
        print "\tNumber of samples being sent: " + str(len(samples))
        return samples

    def modulate(self, samples):
        '''
        Calls modulation function. No need to touch it.
        '''
        return common.modulate(self.fc, self.samplerate, samples)
