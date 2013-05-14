import numpy
import math
import operator

# Methods common to both the transmitter and receiver
def modulate(fc, samplerate, samples):
  '''
  A modulator that multiplies samples with a local carrier 
  of frequency fc, sampled at samplerate
  '''
  for n in xrange len(samples):
    samples[n] *=math.cos(2*math.pi * fc *n/ samplerate)
  return samples

def demodulate(fc, samplerate, samples):
  '''
  A demodulator that performs quadrature demodulation
  '''
  demod_samples=[]
  lp_filter_samples=lpfilter(samples, math.pi * fc* / samplerate)
  for n in range (0, len(samples)):
    demod_samples[n] = samples[n]* math.cos(2*math.pi * fc*n / samplerate) *lpfilter[n]
  return demod_samples

def lpfilter(samples_in, omega_cut):
  '''
  A low-pass filter of frequency omega_cut.
  '''
  # set the filter unit sample response
  L = 50
  lp_filter_samples = samples_in
  for n in range (-1*L , L):
    if not n:
      lp_filter_samples[n]=omega_cut/math.pi
    else:
      lp_filter_samples[n]= math.sin(omega_cut*n/(math.pi*n))

  return lp_filter_samples

