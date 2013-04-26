import sys
import math
import numpy
import scipy.cluster.vq
import common_txrx as common
from numpy import linalg as LA
import receiver_mil3

class Receiver:
    def __init__(self, carrier_freq, samplerate, spb):
        '''
        The physical-layer receive function, which processes the
        received samples by detecting the preamble and then
        demodulating the samples from the start of the preamble 
        sequence. Returns the sequence of received bits (after
        demapping)
        '''
        self.fc = carrier_freq
        self.samplerate = samplerate
        self.spb = spb 
        print 'Receiver: '

    def detect_threshold(self, demod_samples):
        '''
        Calls the detect_threshold function in another module.
        No need to touch this.
        ''' 
        return receiver_mil3.detect_threshold(demod_samples)
 
    def detect_preamble(self, demod_samples, thresh, one):
        '''
        Find the sample corresp. to the first reliable bit "1"; this step 
        is crucial to a proper and correct synchronization w/ the xmitter.
        '''

        '''
        First, find the first sample index where you detect energy based on the
        moving average method described in the milestone 2 description.
        '''
        # Fill in your implementation of the high-energy check procedure

        energy_offset = -1 
        for offset in range(len(demod_samples)):
             curr_samples= samples[offset: offset+self.spb]
             average = 0
             #IGNORE FIRST SPB/4 AND LAST SPB/4 BITS OF SAMPLE 
             central_samples= curr_samples[(self.spb/4) : (self.spb*3)/4 ]
             for sample in central_samples:
                average += sample
             average/= len(central_samples)
             #if this average is greater than average of mean_one and threshold, then this use this offset
             if average > ((one + threshold)/2):
                energy_offset=offset
                break 

        if energy_offset < 0:
            print '*** ERROR: Could not detect any ones (so no preamble). ***'
            print '\tIncrease volume / turn on mic?'
            print '\tOr is there some other synchronization bug? ***'
            sys.exit(1)

        '''
        Then, starting from the demod_samples[offset], find the sample index where
        the cross-correlation between the signal samples and the preamble 
        samples is the highest. 
        '''
        # Fill in your implementation of the cross-correlation check procedure
        
        preamble_offset = 0
        preamble_bits= [1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1]
        preamble_samples=[]
        for bit in preamble_bits:
            for x in range(self.spb):
                if bit==0:
                    preamble_samples.append(0)
                else:
                    preamble_samples.append(one)

        correlation=0
        largest = 0
        preamble_offset= 0 

        #Calculate the correlation between preamble and demodulated bits in order to find preamble start in demod_bits
        for k in range (energy_offset,energy_offset+ 3*len(preamble_samples)):
            for x in range (len (preamble_samples)):
                correlation+= (preamble_samples[x]* demod_samples[x+k]
            if correlation > largest : 
                preamble_offset= k 

        
        '''
        [preamble_offset] is the additional amount of offset starting from [offset],
        (not a absolute index reference by [0]). 
        Note that the final return value is [offset + pre_offset]
        '''

        return energy_offset + preamble_offset
        
    #Need to do this one 
    def demap_and_check(self, demod_samples, preamble_start):
        '''
        Demap the demod_samples (starting from [preamble_start]) into bits.
        1. Calculate the average values of midpoints of each [spb] samples
           and match it with the known preamble bit values.
        2. Use the average values and bit values of the preamble samples from (1)
           to calculate the new [thresh], [one], [zero]
        3. Demap the average values from (1) with the new three values from (2)
        4. Check whether the first [preamble_length] bits of (3) are equal to
           the preamble. If it is proceed, if not terminate the program. 
        Output is the array of data_bits (bits without preamble)
        '''

        preamble_bits= [1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1]
        mean_vals=[]
        curr_index = preamble_start
        for x in range (len(preamble_bits)):
            middle_bits = demod_samples[curr_index+ (self.spb/4) : curr_index+ (self.spb*3)/4]
            mean = 0
            for bit in middle_bits:
                mean+= bit
            mean/= len(middle_bits)
            mean_vals.append(mean)
            curr_index+= self.spb
        mean_1 = 0 
        mean_0 = 0 
        for i in range len(preamble_bits):
            if preamble_bits[i]:
                mean_0+= preamble_bits[i]
            else : 
                mean_1+= preamble_bits[i]
        # There are 9 zeros in the preamble
        mean_0/=9
        # There are 15 ones in the preamble 
        mean_1/=15
        new_threshold = (mean_1+ mean_0)/2

        data_bits=[]

        for x in range ((len(demod_samples) - preamble_start)/self.spb):
            middle_bits = demod_samples[curr_index+ (self.spb/4) : curr_index+ (self.spb*3)/4]
            mean = 0
            for bit in middle_bits:
                mean+= bit
            mean/= len(middle_bits)
            if mean > new_threshold:
                data_bits.append(1)
            else: 
                data_bits.append(0)

        demod_preamble = data_bits(:len(preamble_bits))
        if demod_preamble equal preamble_bits:
            data_bits=data_bits[len(preamble_bits):]
        else : 
            print '*** ERROR: Preamble was not detected. ***'
            sys.exit(1)

        return data_bits # without preamble

    def demodulate(self, samples):
        return common.demodulate(self.fc, self.samplerate, samples)
