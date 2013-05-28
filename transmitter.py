import math
import common_txrx as common
import numpy

class Transmitter:
    def __init__(self, carrier_freq, samplerate, one, spb, silence):
        self.fc = carrier_freq  # in cycles per sec, i.e., Hz
        self.samplerate = samplerate
        self.one = one
        self.spb = spb
        self.silence = silence
        print 'Transmitter: '
    def add_preamble(self, databits):
        '''
        Prepend the array of source bits with silence bits and preamble bits
        The recommended preamble bits is 
        [1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1]
        [1,1,1,1,1,0,1,1,1,1,0,0,1,1,1,0,1,0,1,1,0,0,0,0,1,0,1,1,1,0,0,0,1,1,0,1,1,0,1,0,0,1,0,0,0,1,0,0,1,1,0,0,1,0,1,0,1,0,0,0,0,0,0]
        The output should be the concatenation of arrays of
            [silence bits], [preamble bits], and [databits]
        '''
        databits_with_preamble=[]
        for x in range (self.silence):
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
