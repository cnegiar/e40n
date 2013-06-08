We implemented both options for Milestone 3.

A couple of notes:

Because sendrecv.py is still based on the non-channel coded model of transmission, there is a runtime error when trying to create a transmitter object. Since the constructor for the transmitter has been modified to take an extra parameter (-H cc_len), running sendrecv.py throws an error when creating the constructor. To run only the mod/demod code, please modify the constructor in transmitter.py to remove the references to cc_len, or use the transmitter.py submitted in Milestone 2.

When we do channel encoding, there is sometimes a corruption in the header of the databits sent that leads to an error in the sink. Usually this is caused by an error in the encoded data length which leads to an index out of bounds exception. However the BER is still able to be calculated even without the ability to decode the text.

Following a correspondence with TA Raejoon Jung, we were told to move the BER calculation/print statement in sendrecv_coding.py to BEFORE the decoding in the sink. This allowed us to get numbers for our BERs and to calculate the required averages (please see results.txt).