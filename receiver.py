import sys
import math
import numpy
import scipy.cluster.vq
import common_txrx as common
from numpy import linalg as LA
import receiver_mil3
import hamming_db as ham

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

    # Computes the syndromes and checks to see if a correction needs to be made.
    # If so, make the correction and return the correct bits and 1 as the error count.
    # Else return the original bits and 0 as the error count.
    def correct(self, chunk, n, k, H):
        cols = numpy.hsplit(H, n)
        syndrome = numpy.dot(H, numpy.transpose(chunk))
        # account for xor
        for x in xrange(len(syndrome)):
            if syndrome[x]%2 == 0: syndrome[x] = 0
            else: syndrome[x] = 1
        # check if correct
        correct = True
        for x in xrange(len(syndrome)):
            if syndrome[x] != 0: correct = False
        if correct: return 0, chunk[:k]
        # correct error
        for x in xrange(k):
            if not numpy.array_equal(syndrome, cols[x]):
                chunk[x] = 1 if chunk[x] == 0 else 0
                return 1, chunk[:k]

    def hamming_decoding(self, coded_bits, index):
        decoded_bits = []
        num_errors = 0
        n, k, H = ham.parity_lookup(index)
        coding_rate = float(k)/n
        while len(coded_bits)%n != 0:
            coded_bits = numpy.append(coded_bits, 0)
        for x in xrange(0, len(coded_bits), n):
            chunk = coded_bits[x:x+n]
            corrected, correct_chunk  = self.correct(chunk, n, k, H)
            num_errors += corrected
            decoded_bits = numpy.append(decoded_bits, correct_chunk)
        decoded_bits = ''.join(numpy.char.mod('%d', decoded_bits))
        return decoded_bits, coding_rate, num_errors

    def decode(self, rcd_bits):
        encoding_options = [[3,1],[7,4],[15,11],[31,26]]
        header = rcd_bits[0:32*3] #length of encoded header
        decoded_header, temp_cr, temp_ne = self.hamming_decoding(header, 0)
        data_len = int(str(decoded_header[:30]), 2) 
        index = int(str(decoded_header[30:]), 2)
        # print "Len = " + str(data_len)
        # print "Ind = " + str(index)
        data = rcd_bits[32*3:32*3+data_len]
        print data
        decoded_data, coding_rate, num_errors = self.hamming_decoding(data, index)
        print "channel coding rate: " + str(coding_rate)
        print 'errors corrected: ' + str(num_errors)
        return list(int(x) for x in decoded_data)

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
        energy_offset = -1 
        for offset in range(len(demod_samples)):
             curr_samples= demod_samples[offset:offset+self.spb]
             average = 0
             #IGNORE FIRST SPB/4 AND LAST SPB/4 BITS OF SAMPLE 
             central_samples= curr_samples[(self.spb/4):(self.spb*3)/4]
             for sample in central_samples:
                average += sample

             average = average/ len(central_samples)

             #if this average is greater than average of mean_one and threshold, then this use this offset
             if average > ((one + thresh)/2):
                energy_offset = offset
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
        preamble_offset = 0
        #preamble_bits = [1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1]
        preamble_bits= [1,1,1,1,1,0,1,1,1,1,0,0,1,1,1,0,1,0,1,1,0,0,0,0,1,0,1,1,1,0,0,0,1,1,0,1,1,0,1,0,0,1,0,0,0,1,0,0,1,1,0,0,1,0,1,0,1,0,0,0,0,0,0]
        preamble_samples = []
        for bit in preamble_bits:
            for x in range(self.spb):
                if bit == 0:
                    preamble_samples.append(0)
                else:
                    preamble_samples.append(one)

        largest = 0
        preamble_offset= 0

        #Calculate the correlation between preamble and demodulated bits in order to find preamble start in demod_bits
        for x in xrange(0, 3*len(preamble_samples)):
            offset = energy_offset + x
            norm = numpy.linalg.norm(demod_samples[offset:offset+len(preamble_samples)])
            correlation = numpy.dot(demod_samples[offset:offset+len(preamble_samples)], preamble_samples)/norm
            if correlation >= largest:
                preamble_offset = offset
                largest = correlation
        
        '''
        [preamble_offset] is the additional amount of offset starting from [offset],
        (not a absolute index reference by [0]). 
        Note that the final return value is [offset + pre_offset]
        '''
        return preamble_offset
        
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
        #preamble_bits = [1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1]
        preamble_bits = [1,1,1,1,1,0,1,1,1,1,0,0,1,1,1,0,1,0,1,1,0,0,0,0,1,0,1,1,1,0,0,0,1,1,0,1,1,0,1,0,0,1,0,0,0,1,0,0,1,1,0,0,1,0,1,0,1,0,0,0,0,0,0]
        mean_vals = []
        curr_index = preamble_start
        for x in range(len(preamble_bits)):
            middle_bits = demod_samples[curr_index+(self.spb/4):curr_index+((self.spb*3)/4)]
            mean = 0
            for bit in middle_bits:
                mean += bit
            mean = float(mean)/len(middle_bits)
            mean_vals.append(mean)
            curr_index += self.spb
        mean_1 = 0
        mean_0 = 0
        for i in xrange (len(preamble_bits)):
            if preamble_bits[i]:
                mean_1 += mean_vals[i]
            else :
                mean_0 += mean_vals[i]
        # There are 9 zeros in the  short preamble
        #There are 32 zeros in the long preamble
        mean_0 = float(mean_0)/32
        # There are 15 ones in the short preamble 
        # There are 31 ones in the long preamble 
        mean_1 = float(mean_1)/31
        new_threshold = (mean_1+ mean_0)/2
        data_bits = []

        curr_index = preamble_start
        while(curr_index + self.spb < len(demod_samples)):
            middle_bits = demod_samples[curr_index+(self.spb/4):curr_index+ (self.spb*3)/4]
            
            mean = 0
            for bit in middle_bits:
                mean += bit
            mean /= len(middle_bits)
            if mean > new_threshold:
                data_bits.append(1)
            else: 
                data_bits.append(0)
            curr_index += self.spb
        demod_preamble = data_bits[:len(preamble_bits)]

        print demod_preamble
        
      #  if demod_preamble == preamble_bits:
        data_bits = data_bits[len(preamble_bits):]
       # else : 
         #   print '*** ERROR: Preamble was not detected. ***'
         #   sys.exit(1)

      

        return data_bits # without preamble

    def demodulate(self, samples):
        return common.demodulate(self.fc, self.samplerate, samples)
