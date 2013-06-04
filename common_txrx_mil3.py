import numpy
import math
import operator

pi = 3.14159265359

# Methods common to both the transmitter and receiver
def modulate(fc, samplerate, samples):
  '''
  A modulator that multiplies samples with a local carrier 
  of frequency fc, sampled at samplerate
  '''
  for n in xrange (len(samples)):
    samples[n] *=math.cos((2*pi * fc *n )/ samplerate)
  return samples

def demodulate(fc, samplerate, samples):
  '''
  A demodulator that performs quadrature demodulation
  '''
  for n in range (0,len(samples)):
    samples[n]*=math.cos((2*pi*fc*n)/samplerate)
  
  demod_samples = lpfilter(samples,(pi *fc)/ samplerate)
  return demod_samples

def lpfilter(samples_in, omega_cut):
  print "ENTERING LPF"
  '''
  A low-pass filter of frequency omega_cut.
  '''
  # set the filter unit sample response
  samples_in = numpy.array(samples_in)
  for n in xrange(0,len(samples_in)):
    sample=0
    for x in xrange(-50,50):
      if x == 0 :
         weight = (omega_cut/pi)
      else:
         weight = math.sin(omega_cut*x)/(pi*x)
      if (n-x>=0 and n-x < len(samples_in)):
        sample += (weight*samples_in[n-x]) 
    samples_in[n]=sample

  print "EXITING LPF"
  return samples_in

