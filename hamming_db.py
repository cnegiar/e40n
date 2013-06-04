import numpy
import math
import operator
import common_txrx_mil3
import binascii
import sys

generating_matrices = [numpy.array([1, 1, 1]),
                       numpy.array([1,    1,    0,    1,    0,    0,    0,
                                    0,    1,    1,    0,    1,    0,    0,
                                    1,    1,    1,    0,    0,    1,    0,
                                    1,    0,    1,    0,    0,    0,    1]),
                       numpy.array([1,     1,     0,     0,     1,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
                                    0,     1,     1,     0,     0,     1,     0,     0,     0,     0,     0,     0,     0,     0,     0,
                                    0,     0,     1,     1,     0,     0,     1,     0,     0,     0,     0,     0,     0,     0,     0,
                                    1,     1,     0,     1,     0,     0,     0,     1,     0,     0,     0,     0,     0,     0,     0,
                                    1,     0,     1,     0,     0,     0,     0,     0,     1,     0,     0,     0,     0,     0,     0,
                                    0,     1,     0,     1,     0,     0,     0,     0,     0,     1,     0,     0,     0,     0,     0,
                                    1,     1,     1,     0,     0,     0,     0,     0,     0,     0,     1,     0,     0,     0,     0,
                                    0,     1,     1,     1,     0,     0,     0,     0,     0,     0,     0,     1,     0,     0,     0,
                                    1,     1,     1,     1,     0,     0,     0,     0,     0,     0,     0,     0,     1,     0,     0,
                                    1,     0,     1,     1,     0,     0,     0,     0,     0,     0,     0,     0,     0,     1,     0,
                                    1,     0,     0,     1,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     1]),
                       numpy.array([ 1,    0,     1,     0,     0,     1,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
                                     0,    1,    0,    1,     0,     0,     1,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
                                     0,    0,    1,    0,     1,     0,     0,     1,     0,     0,     0,     0,     0,     0,     0,     0,     0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     1,    0,    1,    1,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     0,    1,    0,    1,    1,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     1,    0,    0,    0,    1,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     1,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     0,    1,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     0,    0,    1,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     1,    0,    1,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     1,    1,    1,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     1,    1,    0,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     1,    1,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     0,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     0,    0,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     0,    0,    0,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,
                                     1,    0,    1,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,
                                     1,    1,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,
                                     0,    1,    1,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,    0,
                                     1,    0,    0,    1,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,    0,
                                     1,    1,    1,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,    0,
                                     1,    1,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,    0,
                                     0,    1,    1,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,    0,
                                     1,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1,    0,
                                     0,    1,    0,    0,    1,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    1])]

parameters = [[3,1],[7,4],[15,11],[31,26]]

def gen_lookup(cc_len):
    ''' 
    returns
    (1) n (=cc_len, codeword length)
    (2) k (length of data bit in each codeword)
    (3) index (index of the corresponding code in the above lookup table)
    (4) generator matrix
    for Hamming code with n = cc_len
    '''
    closest_matrix = min(parameters, key=lambda x:abs(x[0]-cc_len))
    n = closest_matrix[0]
    k = closest_matrix[1]
    index = parameters.index(closest_matrix)
    G = numpy.eye(k)
    temp = numpy.reshape(generating_matrices[index], (k, n))
    cols = numpy.hsplit(temp, n)
    for x in xrange(n-k):
        G = numpy.concatenate((G, cols[x]), axis=1)
    return n, k, index, G

def parity_lookup(index):
    '''
    returns the
    (1) n (=cc_len, codeword length)
    (2) k (length of data bit in each codeword)
    (3) parity check matrix
    matched by the lookup table above given the index
    The reason why this takes the index as the input while gen_lookup takes cc_len
    is, because containing index is efficient than containing n in the header.
    The decoder reads the header to pick the right parity check matrix.
    '''  
    n = parameters[index][0]
    k = parameters[index][1]
    temp = numpy.reshape(generating_matrices[index], (k, n))
    cols = numpy.hsplit(temp, n)
    A = cols[0]
    for x in xrange(1, n-k):
          A = numpy.concatenate((A, cols[x]), axis=1)
    A = A.transpose()
    H = numpy.eye(n-k)
    H = numpy.concatenate((A, H), axis=1)
    return n, k, H