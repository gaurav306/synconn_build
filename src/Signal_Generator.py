import sys
from random import choice, randint

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import signal
from scipy.stats import truncnorm


def plot_df_acf(df, cat1, name):
	# from statsmodels.graphics.tsaplots import plot_acf
	# from scipy import signal
	df = np.array(df)
	u1 = signal.correlate(df, df)

	# Plot the original df and the autocorrelation
	fig = plt.figure(0, figsize=(40, 8))
	#plt.subplots_adjust(hspace=0.3)
	ax1 = fig.add_subplot(2, 1, 1)
	ax1.plot(df, drawstyle='steps', label='df', lw=1)
	ax1.margins(x=0)    
	ax1.title.set_text('SIGNAL: %s' % name)

	ax2 = fig.add_subplot(2, 1, 2)
	ax2.plot(u1, drawstyle='steps', label='df corr')
	ax2.legend()
	ax2.margins(x=0)
	ax2.title.set_text('SIGNAL.CORRELATE')
	
	plt.savefig('%s_%s.png' % (name, cat1), dpi=300, bbox_inches='tight')
	plt.close()

def calc_avg_prob(list):
	print('Average: %f' % (sum(list)/len(list)))
	unique_all, counts_all = np.unique(list, return_counts=True)
	for unique, counts in zip(unique_all, counts_all):
		print('Probability(in percentage) of %s: %s' % (unique, round(counts/len(list) * 100, 2)))

class SignalGenerator:
	def __init__(self, signal_type, configs, plot_ident):
		self.configs = configs
		self.plot_ident = plot_ident
		self.frequency_categories = self.configs['signal_generator_details']['frequency_categories']
		self.signal_type = signal_type
		self.timestep = self.configs['energyplus_init']['timestep']
	
	def __call__(self):
		self.length = 8760*self.timestep
		self.if_multiple_frequency_signal 	= self.configs['signal_generator_details'][self.signal_type][
												'if_multiple_frequency_signal']
		if self.if_multiple_frequency_signal:
			self.minmax_splits	= self.configs['signal_generator_details'][self.signal_type]['minmax_splits']
			random_no_splits = np.random.randint(self.minmax_splits[0], self.minmax_splits[1])
			all_chunks = self._split_range_in_equal_chunks(0, self.length, random_no_splits)
			prbs_list = []
			for i in range(0, random_no_splits):
				steps_i = all_chunks[i][1]-all_chunks[i][0]
				self.length = steps_i
				self.frequency = choice(self.frequency_categories)
				prbs_list.extend(self._generator_type_frequency())
		else:
			self.frequency 	= self.configs['signal_generator_details'][self.signal_type]['frequency']
			if self.frequency not in self.frequency_categories:
				print('Wrong frequency')
				sys.exit(1)
			prbs_list = self._generator_type_frequency()

		self.ifplotornot = self.configs['signal_generator_details']['if_plot']
		if self.ifplotornot:
			if self.if_multiple_frequency_signal:
				self.plot_ident = self.plot_ident + '_MIXED_FREQ'
			else:
				self.plot_ident = self.plot_ident + '_' + self.frequency
			plot_df_acf(prbs_list, self.plot_ident, self.signal_type)
			#calc_avg_prob(prbs_list)
		print(self.signal_type)
		return prbs_list
	 
	def _generator_type_frequency(self):
		self.possible 					= self.configs['signal_generator_details'][self.signal_type]['possible_bits']
		self.stay_steps_possible 		= self.configs['signal_generator_details'][self.signal_type]['stay_steps_possible']
		self.tightness_for_frequencies 	= self.configs['signal_generator_details'][self.signal_type]['tightness_for_frequencies']
		self.tightness_for_frequencies 	= [int(x * self.timestep) for x in self.tightness_for_frequencies]
		#print(self.tightness_for_frequencies)

		if self.signal_type == 'mprs_setpoints':
			for i in range(0, len(self.frequency_categories)):
				if self.frequency == self.frequency_categories[i]:
					self.minimum = self.tightness_for_frequencies[i]
					self.maximum = self.minimum + self.tightness_for_frequencies[i]
			if self.configs['signal_generator_details'][self.signal_type]['normal_or_uniform_distribution'] == 'normal':
				return self._make_random_sequence_normal()
			elif self.configs['signal_generator_details'][self.signal_type]['normal_or_uniform_distribution'] == 'uniform':
				return self._make_random_sequence_uniform()
		
		if self.signal_type == 'mprs_hvac_mode':
			for i in range(0, len(self.frequency_categories)):
				if self.frequency == self.frequency_categories[i]:
					self.minimum = self.timestep * self.configs['signal_generator_details'][self.signal_type]['minimum_one_mode']
					self.maximum = self.tightness_for_frequencies[i]
			return self._make_random_sequence_hvac_mode(startbit = 3)
		
		if self.signal_type == 'prbs_win_0_1':
			for i in range(0, len(self.frequency_categories)):
				if self.frequency == self.frequency_categories[i]:
					self.minimum = self.timestep * self.configs['signal_generator_details']['minimum_window_opening_frequency']
					self.maximum = self.tightness_for_frequencies[i]*2			
			return self._make_random_signal_singlestep(startbit = 0)
		
		if self.signal_type == 'prbs_win_multiple':
			for i in range(0, len(self.frequency_categories)):
				if self.frequency == self.frequency_categories[i]:
					self.minimum = self.timestep * self.configs['signal_generator_details']['minimum_window_opening_frequency']
					self.maximum = self.tightness_for_frequencies[i]*2	
			return self._make_random_signal_singlestep(startbit = 0)
		
		if self.signal_type == 'prbs_win_0_1_multistep':
			for i in range(0, len(self.frequency_categories)):
				if self.frequency == self.frequency_categories[i]:
					self.minimum = self.timestep * self.configs['signal_generator_details']['minimum_window_opening_frequency']
					self.maximum = self.tightness_for_frequencies[i]*2	
			return self._make_random_signal_multistep(startbit = 0)
		
		if self.signal_type == 'prbs_win_multiple_multistep':
			for i in range(0, len(self.frequency_categories)):
				if self.frequency == self.frequency_categories[i]:
					self.minimum = self.timestep * self.configs['signal_generator_details']['minimum_window_opening_frequency']
					self.maximum = self.tightness_for_frequencies[i]*2	
			return self._make_random_signal_multistep(startbit = 0)
		
		if self.signal_type == 'noise_for_setpoints':
			self.noise_or_all_zero = self.configs['signal_generator_details'][self.signal_type]['noise_or_all_zero']
			return self._make_noisy_signal_setpoints(self.noise_or_all_zero)
	
	def _make_random_sequence_normal(self): # MPRS or PRBS sequence generator with gaussian distribution
		sequence = []
		seq = truncnorm(a=-2/3., b=2/3., loc=0, scale=6).rvs(size=self.length)
		random_possible = [round(i) for i in seq]  # uniques values are [-4 -3 -2 -1  0  1  2  3  4]
		random_possible = [i + 4 for i in random_possible] # uniques values are [0 1 2 3 4 5 6 7 8]
		for i in range(self.length):
			rand_value = self.possible[random_possible[i]]
			sequence.append(rand_value)
			for j in range(randint(self.minimum, self.maximum)):
				sequence.append(rand_value)
		sequence = sequence[:self.length]
		return sequence

	def _make_random_sequence_uniform(self): 
		# sequence generator from multiple possible values
		sequence = []
		while len(sequence) < self.length:
			rand_value = choice(self.possible)
			sequence.append(rand_value)
			for j in range(randint(self.minimum, self.maximum)):
				sequence.append(rand_value)
		sequence = sequence[:self.length]
		return sequence

	def _make_random_sequence_hvac_mode(self, startbit): # MPRS or PRBS sequence generator
		sequence = []
		#for _ in range(self.timestep * 24):
		sequence.append(startbit)
		while len(sequence) < self.length:
			rand_value = choice(self.possible)
			sequence.append(rand_value)
			for j in range(randint(self.minimum, self.maximum)):
				sequence.append(rand_value)
		sequence = sequence[:self.length]
		return sequence
	
	def _make_random_signal_singlestep(self, startbit): # randomly goes from 0 to certain value for one timestep and then back to 0
		sequence = []
		sequence.append(startbit)
		while len(sequence) < self.length:
			rand_value = choice(self.possible)
			if rand_value > 0:
				sequence.append(rand_value)
				for j in range(randint(self.minimum, self.maximum)):
					sequence.append(0)
		sequence = sequence[:self.length]
		return sequence

	def _make_random_signal_multistep(self, startbit): # randomly goes from 0 to certain value and stays there for random umber of timestep and then back to 0
		sequence_singlestep = self._make_random_signal_singlestep(startbit)
		sequence_multistep = []
		for ix in range(len(sequence_singlestep)):
			if sequence_singlestep[ix] == 0:
				sequence_multistep.append(sequence_singlestep[ix])
			else:
				for _ in range(choice(self.stay_steps_possible)):
					sequence_multistep.append(sequence_singlestep[ix])
		sequence_multistep = sequence_multistep[:self.length]
		return sequence_multistep
	
	def _make_noisy_signal_setpoints(self, noise_or_all_zero):
		
		def give_random_list_gaussian(length_1):
			mu		= self.configs['signal_generator_details']['noise_for_setpoints']['mean_of_noise']
			sigma 	= self.configs['signal_generator_details']['noise_for_setpoints']['std_dev_of_noise']
			s = np.random.normal(mu, sigma, length_1) / 5
			return s
		
		if noise_or_all_zero:
			min_value, max_value = -1, 1 
			rndm_list = give_random_list_gaussian(int(self.length*1.5))  # 1.5 is a safety factor to make sure that the list is long enough
			smooth_list = [0]
			flag = 0
			rolling_avg_error = 96*1
			switch_to_zero = int(96*3.5)
			for i in range(rolling_avg_error, int(self.length*1.5)):
				if i%switch_to_zero == 0:
					smooth_list.append(0)
				else:
					smoothed = np.sum(rndm_list[i-rolling_avg_error:i])
					next_entry = np.clip((smoothed/rolling_avg_error + smooth_list[flag]), min_value, max_value)
					smooth_list.append(next_entry)
				flag = flag + 1
			
			df = pd.DataFrame(smooth_list)
			smooth_list = df.rolling(rolling_avg_error).mean()
			
			return smooth_list[:self.length]
		else:
			return [0]*self.length

	def _split_range_in_equal_chunks(self, start, end, num_chunks):
		"""
		Splits a range into equal chunks.
		"""
		chunks = []
		for i in range(num_chunks):
			if i == 0:
				chunks.append((start, start + (end - start) // num_chunks))
			else:
				chunks.append((chunks[i-1][1], chunks[i-1][1] + (end - start) // num_chunks))
		if num_chunks > 0:
			chunks[-1] = (chunks[-1][0], end)
		return chunks


def generate_signal_for_EP(filename, configs):
	all_signal_type = ['mprs_setpoints', 
						'mprs_hvac_mode', 
						'prbs_win_0_1', 
						'prbs_win_0_1_multistep', 
						'prbs_win_multiple', 
						'prbs_win_multiple_multistep',
						'noise_for_setpoints']	
	
	configs['signal_generator_details']['if_plot'] = 0
	df = pd.DataFrame()
	for i in range(1,1+5):
		df[all_signal_type[0]+'_'+str(i)] = SignalGenerator(all_signal_type[0], configs, 'Zone_%s' %str(i))()
	if configs['ep_simualtion_data_details']['random_HVAC_mode']:
		for i in range(1,1+5):	
			df[all_signal_type[1]+'_'+str(i)] = SignalGenerator(all_signal_type[1], configs, 'Zone_%s' %str(i))()
	else:
		for i in range(1,1+5):	
			df[all_signal_type[1]+'_'+str(i)] = [3] * configs['energyplus_init']['timestep'] * 8760

	for i in range(1,1+4):	# 4 zones with windows
		df[all_signal_type[5]+'_'+str(i)] = SignalGenerator(all_signal_type[5], configs, 'Zone_%s' %str(i))()
	
	for i in range(1,1+5):
		df[all_signal_type[6]+'_'+str(i)] = SignalGenerator(all_signal_type[6], configs, 'Zone_%s' %str(i))()
	#df.to_csv('src/Signals_inputs.csv', index=False)
	df.to_csv(filename, index=False)
	
if __name__ == '__main__':
	import yaml
	with open(r'../../config.yaml', 'r') as file:
		yaml_configs = yaml.safe_load(file) 
	
	#SignalGenerator('mprs_setpoints', yaml_configs, 'test')()
	#SignalGenerator('mprs_hvac_mode', yaml_configs, 'test')()
	#SignalGenerator('prbs_win_multiple_multistep', yaml_configs, 'test')()
	#SignalGenerator('noise_for_setpoints', yaml_configs, 'test')()
	generate_signal_for_EP('data.csv', yaml_configs)
	