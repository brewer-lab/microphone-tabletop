import os
import sys
import numpy as np
from scipy.io.wavfile import read, write

class integrator:
    def __init__(self):
        self.state = 0
        self.threshold = 0
        self.integrated_charge = 0
        self.voltage_threshold = -1.2
        self.voltage_resting = 0
        self.tau = 5e-5
        self.timestep = 1e-6
        self.voltage_updated = 0.0
        
    def time(self, analog_voltage):
        self.integrated_charge = self.integrated_charge +  (-1/self.tau)*(analog_voltage-self.voltage_resting)
        if (self.state == 1):
            self.state = 0
        if (self.integrated_charge < self.voltage_threshold):
            self.integrated_charge = 0
            self.state = 1
        return self.integrated_charge

def list_files(dir):
    r = []
    #print( dir)
    for root, dirs, files in os.walk(dir):
    	#print(root, files)
    	for name in files:
        	r.append(os.path.join(root, name))
    return r

def process(data):
	data_abs = []
	data_sqrd = []
	data_shift = []
	try:
	    i = 0
	    while i < len(data[0]):
	        #print('i', i)
	        data_abs.append(np.abs(data[:,i].astype(dtype='float32')))
	        data_sqrd.append(np.square(data[:,i].astype(dtype='float32')))
	        data_shift.append(data[:,i].astype(dtype='float32')+np.max(data[:,i]))
	        i += 1
	except:
	    data_abs.append(np.abs(data.astype(dtype='float32')))
	    data_sqrd.append(np.square(data.astype(dtype='float32')))
	    data_shift.append(data.astype(dtype='float32')+np.max(data))
	    
	return data_sqrd,data_abs, data_shift




def write_event_string(data,num_data_channels,tau,starting_index,file_path_and_name):
	i = 0
	sav = ""
	#print ("channel ID \t event time")
	n = 0
	channels = []
	while n < num_data_channels:
	    channels.append(integrator())
	    n += 1

	s= starting_index
	j = s
	rate = np.zeros(num_data_channels)
	print(file_path_and_name)
	if num_data_channels > 1:
		#print( 'len(data)', len(data), len(data[0]) )
		while j < len(data[0]):
			i = 0
			#print('j',j)
			while i < num_data_channels:
				#print("i,j",i,j)
				channels[i].time(data[i][j]*tau)
				#print ('channels[i] mc', channels[i].integrated_charge)
				if (channels[i].state == 1):
					#print("multi channel chanel spike")
					sav += str(i) + '\t'+str(j-s) + '\n'
					#print(rate)
					rate[i] += 1
				i += 1
			j += 1
	elif (num_data_channels == 1):
		j = 0
		while j < len(data[0]):
			channels[0].time(data[0][j]*tau)
			#print(channels[0].integrated_charge)
			if (channels[0].state == 1):
				#print("spike")
				sav += '0' + '\t'+str(j-s) + '\n'
				rate[0] += 1
			j += 1
	#print(sav)
	#print(file_path_and_name)
	f = open(file_path_and_name,"w")
	f.write(sav)
	if num_data_channels >	1:
		i = 0
		while i < len(rate):
			rate[i] = rate[i] / len(data[i])
			i += 1
	elif (num_data_channels == 1):
		i = 0
		while i < len(rate):
			rate[i][0] = rate[i][0] / len(data[0])
			print('rate i', rate[i], len(data[0]))

			i += 1
	return rate

dataset = list_files('..\\..\\..\\Documents\\datasets\\microphone_array')
#print (list_files('../../../Documents/datasets/DOI-10-13012-b2idb-6216881_v1/'))
i = 1
for wav in dataset:
	sys.stdout.flush()
	print (wav)
	label = wav.split('\\')
	#print(wav.find('wav'))
	if (wav.find('wav') != -1):
		if ( i > 192):
			Fs, data = read(wav)
			print(data.shape, len(data))
			d_sqrd, d_abs, d_shift = process(data)
			print("length of data", len(d_sqrd) )
			#print( d_sqrd)
			n_channels = 0
			try:
				len(data[:,0])
				n_channels = len(d_sqrd)
			except:
				n_channels = 1
			file_name = ''
			j = 0
			while j < len(label):
				if (j > 6) and (j < len(label)-1):
					file_name += (label[j] + '\\') 
				if j == len(label)-1:
					file_name_abs = file_name + 'abs_' + label[j].split('.')[0]+'.dat'
					file_name_sqr = file_name + 'sqr_' + label[j].split('.')[0]+'.dat'
					file_name_shift = file_name + 'shift_' + label[j].split('.')[0]+'.dat'
					print("i",i)
					if (i > 12):
						print('num channels', n_channels)
						rate = write_event_string(d_abs,n_channels,1e-9,0,file_name_abs)
						print(rate)
						rate = write_event_string(d_sqrd,n_channels,1e-12,0,file_name_sqr)
						print(rate)
						rate = write_event_string(d_shift,n_channels,1e-9,0,file_name_shift)
						print(rate)
				j += 1
	#		write_event_string(d_sqrd,n_channels,1e-9,0,'sqr_'+wav.split('\\')[6:-1])

	#		write_event_string(d_shift,n_channels,1e-7,0,'shift_'+wav.split('\\')[6:-1])
			#print (Fs)
		i += 1


