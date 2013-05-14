import numpy
import math
import operator
import random
import scipy.cluster.vq
import common_txrx as common

def detect_threshold(demod_samples): 
        # Now, we have a bunch of values that, for on-off keying, are
        # either near amplitude 0 or near a positive amplitude
        # (corresp. to bit "1").  Because we don't know the balance of
        # zeroes and ones in the input, we use 2-means clustering to
        # determine the "1" and "0" clusters.  In practice, some
        # systems use a random scrambler to XOR the input to balance
        # the zeroes and ones. We have decided to avoid that degree of
        # complexity in audiocom (for the time being, anyway).

	# initialization
  center1 = min(demod_samples)
  center2 = max(demod_samples) 
  new_1=0
  new_2=0
  num_1 = 0
  num_2 = 0 

  while True :
    center_assignments=[]
    for x in xrange (len(demod_samples)):
      sample=demod_samples[x]
      center1_diff = (sample-center1)**2
      center2_diff = (sample-center2)**2
      center_assignments[x]= math.min(center1_diff,center2_diff)

    cluster_1_vals=[]
    cluster_2_vals =[]
    for x in xrange (len(center_assignments)):
      if (center_assignments[x] == center1):
        new_1 +=demod_samples[x]
        num_1+=1
      else : 
        new_2 += demod_samples[x]
        num_2+=1

    new_1 = new_1/num_1
    new_2= new_2/num_2
    if new_1== center1 and new_2==center2:
      break
    else : 
      center1=new_1
      center2=new_2

 
  # insert code to associate the higher of the two centers 
  # with one and the lower with zero

  zero = math.min(center1, center2)
  one = math.max(center1,center2)
  
  print "Threshold for 1:"
  print one
  print " Threshold for 0:"
  print zero

  # insert code to compute thresh

  thresh = (one + zero) / 2
  
  return one, zero, thresh

    
