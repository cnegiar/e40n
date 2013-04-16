import numpy
import math
import operator

# Methods common to both the transmitter and receiver.
def hamming(s1,s2):
    # Given two binary vectors s1 and s2 (possibly of different 
    # lengths), first truncate the longer vector (to equalize 
    # the vector lengths) and then find the hamming distance
    # between the two. Also compute the bit error rate  .
    # BER = (# bits in error)/(# total bits )
    len_1 = len(s1)
    len_2= len(s2)
    min_len = min(len_1, len_2)
    hamming_d = 0 
    for i in range (min_len): 
    	if s1[i] != s2[i]: 
    		hamming_d+=1
    ber = float(hamming_d)/ min_len
    return hamming_d, ber
