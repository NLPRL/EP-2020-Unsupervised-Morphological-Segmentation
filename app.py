
#### TRACE FUNCTION ####
# def tracefunc(frame, event, arg, indent=[0]):
#       if event == "call":
#           indent[0] += 2
#           print("-" * indent[0] + "> call function", frame.f_code.co_name)
#       elif event == "return":
#           print("<" + "-" * indent[0], "exit function", frame.f_code.co_name)
#           indent[0] -= 2
#       return tracefunc

# import sys
# sys.setprofile(tracefunc)
########################



FOLDER = ''

SETTINGS = ''

WORD_LIST_PATH = ''

STD_GRAMMAR_PATH = ''

SS_GRAMMAR_PATH = ''
SS_KNOWLEDGE_PATH = ''
CASCADED_GRAMMAR_PATH_1 = ''
CASCADED_GRAMMAR_PATH_2 = ''
PREFIX_NONTERMINAL = ''
SUFFIX_NONTERMINAL = ''
PREFIX_NONTERMINAL_1 = ''
SUFFIX_NONTERMINAL_2 = ''

PYAG_PATH = ''
PYAG_GRAMMAR_INPUT_PATH = ''
PYAG_WORDLIST_INPUT_PATH = ''
ITERATIONS = '0'
DEBUGLVL = '10'
R_SEED = '123'

SEPARATE_SEGMENTS_BY = ' '

PYAG_PARSE_OUTPUT_PATH = ''
NONTERMINALS_TO_PARSE = ''



############################################################################
#
#								GUI App
#
############################################################################

import subprocess
import timeit
from main import *

import sys
import itertools
from layout import *


# backporting subprocess.run() for python2.7
# https://stackoverflow.com/a/40590445/6663620
def run(*popenargs, **kwargs):
	input = kwargs.pop("input", None)
	check = kwargs.pop("handle", False)

	if input is not None:
		if 'stdin' in kwargs:
			raise ValueError('stdin and input arguments may not both be used.')
		kwargs['stdin'] = subprocess.PIPE

	process = subprocess.Popen(*popenargs, **kwargs)
	try:
		stdout, stderr = process.communicate(input)
	except:
		process.kill()
		process.wait()
		raise
	retcode = process.poll()
	if check and retcode:
		raise subprocess.CalledProcessError(
			retcode, process.args, output=stdout, stderr=stderr)
	return retcode, stdout, stderr


try:
	_encoding = QtGui.QApplication.UnicodeUTF8
	def _translate(context, text, disambig):
		return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
	def _translate(context, text, disambig):
		return QtGui.QApplication.translate(context, text, disambig)


class Window(Ui_MainWindow, QtGui.QMainWindow):

	def __init__(self):
		super(Window, self).__init__()
		self.setupUi(self)
		self.home()

	def home(self):

		# directory
		self.browseDirectory.clicked.connect(self.open_folder)

		# settings
		self.comboBoxSelectSettings.activated[str].connect(self.select_settings)

		# preprocessing
		self.browseWordList.clicked.connect(self.open_word_list)
		self.browseGrammarStd.clicked.connect(self.open_std_grammar)
		self.browseGrammarSS.clicked.connect(self.open_ss_grammar)
		self.browseScholarKnowledgeFile.clicked.connect(self.open_ss_input)
		self.browseGrammarCascaded_1.clicked.connect(self.open_cascaded_grammar_1)
		self.browseGrammarCascaded_2.clicked.connect(self.open_cascaded_grammar_2)
		self.pushButtonPreprocess.clicked.connect(self.preprocess)

		# training
		validator = QtGui.QIntValidator(0, 9999)
		self.lineEditRunID.setValidator(validator)
		self.browsePYAG.clicked.connect(self.open_pyag_binary)
		self.browsePYAGGrammar.clicked.connect(self.open_pyag_grammar_input)
		self.browsePYAGWordList.clicked.connect(self.open_pyag_wordlist_input)
		self.pushButtonTrain.clicked.connect(self.train)

		# parsing
		# self.browseParseFile.clicked.connect(self.open_parse_file)
		# self.pushButtonParse.clicked.connect(self.parse)

		# segmentation
		self.browseParseFile.clicked.connect(self.open_parse_file)
		self.browseSegmentationFile.clicked.connect(self.open_segmentation_file)
		self.pushButtonProcess.clicked.connect(self.segment)


		self.show()



	def open_folder(self):
		name = str(QtGui.QFileDialog.getExistingDirectory(self, 'Select the Directory to store files in'))
		if name:
			self.edit_directory_path.setText(name)

	def select_settings(self, text):
		SETTINGS = text
		if SETTINGS == "Standard":
			self.widgetStdGrammar.setEnabled(True)
			self.widgetScholarSeededOnly.setEnabled(False)
			self.widgetCascadedOnly.setEnabled(False)
			self.widgetCascadedSettings.setEnabled(False)
		elif SETTINGS == "Scholar Seeded":
			self.widgetStdGrammar.setEnabled(False)
			self.widgetScholarSeededOnly.setEnabled(True)
			self.widgetCascadedOnly.setEnabled(False)
			self.widgetCascadedSettings.setEnabled(False)
		else:
			self.widgetStdGrammar.setEnabled(False)
			self.widgetScholarSeededOnly.setEnabled(False)
			self.widgetCascadedOnly.setEnabled(True)
			self.widgetCascadedSettings.setEnabled(True)

	def open_word_list(self):
		name = str(QtGui.QFileDialog.getOpenFileName(self, 'Select Word List file'))
		if name:
			self.edit_word_list_path.setText(name)

	def open_std_grammar(self):
		name = str(QtGui.QFileDialog.getOpenFileName(self, 'Select Standard Grammar file'))
		if name:
			self.edit_std_grammar_path.setText(name)

	def open_ss_grammar(self):
		name = str(QtGui.QFileDialog.getOpenFileName(self, 'Select SS Grammar file'))
		if name:
			self.edit_ss_grammar_path.setText(name)

	def open_ss_input(self):
		name = str(QtGui.QFileDialog.getOpenFileName(self, 'Select Scholar Knowledge file'))
		if name:
			self.edit_scholar_seeded_path.setText(name)

	def open_cascaded_grammar_1(self):
		name = str(QtGui.QFileDialog.getOpenFileName(self, 'Select Cascaded Grammar 1 file'))
		if name:
			self.edit_cascaded_grammar_path_1.setText(name)

	def open_cascaded_grammar_2(self):
		name = str(QtGui.QFileDialog.getOpenFileName(self, 'Select Cascaded Grammar 2 file'))
		if name:
			self.edit_cascaded_grammar_path_2.setText(name)

	def preprocess(self):
		print('PREPROCESSING ...')
		# start the timer
		start_time = timeit.default_timer()

		# assign the respective paths
		FOLDER = str(self.edit_directory_path.text())
		if len(FOLDER) == 0:
			FOLDER = '.'
		SETTINGS = self.comboBoxSelectSettings.currentIndex()
		WORD_LIST_PATH = str(self.edit_word_list_path.text())
		STD_GRAMMAR_PATH = str(self.edit_std_grammar_path.text())
		SS_GRAMMAR_PATH = str(self.edit_ss_grammar_path.text())
		SS_KNOWLEDGE_PATH = str(self.edit_scholar_seeded_path.text())
		PREFIX_NONTERMINAL = str(self.edit_prefix_nonterminal.text())
		SUFFIX_NONTERMINAL = str(self.edit_suffix_nonterminal.text())
		CASCADED_GRAMMAR_PATH_1 = str(self.edit_cascaded_grammar_path_1.text())
		CASCADED_GRAMMAR_PATH_2 = str(self.edit_cascaded_grammar_path_2.text())
		PREFIX_NONTERMINAL_2 = str(self.edit_prefix_nonterminal_2.text())
		SUFFIX_NONTERMINAL_2 = str(self.edit_suffix_nonterminal_2.text())

		'''
		words 			- A list of unique words.
		encoded_words 	- A list of unique words in the HEX representation
		hex_chars 		- A list of unique characters in the HEX representation
		'''
		words, encoded_words, hex_chars = process_words(WORD_LIST_PATH)

		word_list_output_path = FOLDER + '/' + WORD_LIST_PATH.split('/')[-1] + '.processed'
		write_encoded_words(encoded_words, word_list_output_path)
		'''
		<word_list_output_path> and <grammar_output_path> are the inputs to PYAGS.
		'''
		self.edit_pyag_input_wordlist.setText(_translate("MainWindow", word_list_output_path, None))
		
		# output things
		print("# The following files were generated:")
		print('\t' + word_list_output_path)

		if SETTINGS == 0:
			'''
			grammar - a map of the grammar rules.
					The keys represent the unique LHS terms
					The values are a list of the RHS terms of the corresponding keys
			for example - {
						'1 1 Word': ['Prefix Stem Suffix'], 
						'Prefix': ['^^^ Chars', '^^^'], 
						'Stem': ['Chars'], 
						'Suffix': ['Chars $$$', '$$$'], 
						'1 1 Chars': ['Char', 'Char Chars']
						}
			'''
			grammar = read_grammar(STD_GRAMMAR_PATH)
			
			'''
			appended_grammar - grammar map with hex_chars
			'''
			appended_grammar = add_chars_to_grammar(grammar, hex_chars)

			'''
			Note: The appended characters and seeded affixes are non-adapted by default, where the parameters
			of their corresponding production rules are set to 1.
			'''
			grammar_output_path = FOLDER + '/' + STD_GRAMMAR_PATH.split('/')[-1] + '.processed'
			write_grammar(appended_grammar, grammar_output_path)
			print('\t' + grammar_output_path)
			'''
			<word_list_output_path> and <grammar_output_path> are the inputs to PYAGS.
			'''
			self.edit_pyag_input_grammar_path.setText(_translate("MainWindow", grammar_output_path, None))


		if SETTINGS == 1:
			'''
			grammar - a map of the grammar rules.
					The keys represent the unique LHS terms
					The values are a list of the RHS terms of the corresponding keys
			for example - {
						'1 1 Word': ['Prefix Stem Suffix'], 
						'Prefix': ['^^^ Chars', '^^^'], 
						'Stem': ['Chars'], 
						'Suffix': ['Chars $$$', '$$$'], 
						'1 1 Chars': ['Char', 'Char Chars']
						}
			'''
			grammar = read_grammar(SS_GRAMMAR_PATH)
			
			'''
			appended_grammar - grammar map with hex_chars
			'''
			appended_grammar = add_chars_to_grammar(grammar, hex_chars)
			
			'''
			This function seeds a grammar tree with prefixes and suffixes read from a file (scholar_seeded_path).
			The nonterminals under which the affixes are inserted are denoted by
			prefix_nonterminal and suffix_nonterminal for prefixes and suffixes, respectively.
			'''
			appended_grammar = prepare_scholar_seeded_grammar(appended_grammar, SS_KNOWLEDGE_PATH, PREFIX_NONTERMINAL, SUFFIX_NONTERMINAL)

			'''
			Note: The appended characters and seeded affixes are non-adapted by default, where the parameters
			of their corresponding production rules are set to 1.
			'''
			grammar_output_path = FOLDER + '/' + SS_GRAMMAR_PATH.split('/')[-1] + '.processed'
			write_grammar(appended_grammar, grammar_output_path)
			print('\t' + grammar_output_path)
			'''
			<word_list_output_path> and <grammar_output_path> are the inputs to PYAGS.
			'''
			self.edit_pyag_input_grammar_path.setText(_translate("MainWindow", grammar_output_path, None))


		# only grammar 1 is processed for now, 2 is processed after first run
		if SETTINGS == 2:
			'''
			grammar - a map of the grammar rules.
					The keys represent the unique LHS terms
					The values are a list of the RHS terms of the corresponding keys
			for example - {
						'1 1 Word': ['Prefix Stem Suffix'], 
						'Prefix': ['^^^ Chars', '^^^'], 
						'Stem': ['Chars'], 
						'Suffix': ['Chars $$$', '$$$'], 
						'1 1 Chars': ['Char', 'Char Chars']
						}
			'''
			grammar = read_grammar(CASCADED_GRAMMAR_PATH_1)
			
			'''
			appended_grammar - grammar map with hex_chars
			'''
			appended_grammar = add_chars_to_grammar(grammar, hex_chars)

			'''
			Note: The appended characters and seeded affixes are non-adapted by default, where the parameters
			of their corresponding production rules are set to 1.
			'''
			grammar_output_path = FOLDER + '/' + CASCADED_GRAMMAR_PATH_1.split('/')[-1] + '.processed'
			write_grammar(appended_grammar, grammar_output_path)
			print('\t' + grammar_output_path)
			'''
			<word_list_output_path> and <grammar_output_path> are the inputs to PYAGS.
			'''
			self.edit_pyag_input_grammar_path.setText(_translate("MainWindow", grammar_output_path, None))


		# calculate elapsed time
		elapsed = timeit.default_timer() - start_time
		print("\n# Time Taken (in seconds): " + str(elapsed))
		print("________________PREPROCESSING COMPLETE________________\n\n")



	def open_pyag_binary(self):
		name = str(QtGui.QFileDialog.getOpenFileName(self, 'Select PYAG Binary file'))
		if name:
			self.edit_PYAG_binary_path.setText(name)

	def open_pyag_grammar_input(self):
		name = str(QtGui.QFileDialog.getOpenFileName(self, 'Select PYAG Grammar Input file'))
		if name:
			self.edit_pyag_input_grammar_path.setText(name)

	def open_pyag_wordlist_input(self):
		name = str(QtGui.QFileDialog.getOpenFileName(self, 'Select PYAG Wordlist Input file'))
		if name:
			self.edit_pyag_input_wordlist.setText(name)

	def train(self):
		print('TRAINING ...')
		# start the timer
		start_time = timeit.default_timer()

		# assign the paths
		SETTINGS = self.comboBoxSelectSettings.currentIndex()
		FOLDER = str(self.edit_directory_path.text())
		if len(FOLDER) == 0:
			FOLDER = '.'

		RUN_ID = str(int(self.lineEditRunID.text()))
		PYAG_PATH = str(self.edit_PYAG_binary_path.text())
		PYAG_GRAMMAR_INPUT_PATH = str(self.edit_pyag_input_grammar_path.text())
		PYAG_WORDLIST_INPUT_PATH = str(self.edit_pyag_input_wordlist.text())
		ITERATIONS = str(int(self.spinBoxNumberofIterations.value()))

		# a file that contains each words' morphology trees
		pyags_parse_output_path = FOLDER + '/' + RUN_ID + 'parse.prs'
		# generated grammar for the run
		pyags_grammar_output_path = FOLDER + '/' + RUN_ID + 'grammar.grmr'
		# PYAGS trace file
		pyags_trace_output_path = FOLDER + '/' + RUN_ID + 'tracefile.trace'

		bashCommand = PYAG_PATH + " -A " + pyags_parse_output_path + \
		" -r " + R_SEED + " -d " + DEBUGLVL + \
		" -F " + pyags_trace_output_path + \
		" -G " + pyags_grammar_output_path + \
		" -D -E -a 1e-4 -b 1e4 -e 1 -f 1 -g 10 -h 0.1 -w 1 -T 1 -m 0 -n " + ITERATIONS + " -R -1 " + \
		PYAG_GRAMMAR_INPUT_PATH + " < " + PYAG_WORDLIST_INPUT_PATH

		retcode = subprocess.call(bashCommand, shell=True)

		# output things
		if retcode != 0:
			print('Error!! Terminated\n')
			return

		# output things
		print("# The following files were generated:")
		print('\t' + pyags_parse_output_path)
		print('\t' + pyags_grammar_output_path)
		print('\t' + pyags_trace_output_path)

		'''
		<pyags_parse_output_path> is the input to parse.
		'''
		self.edit_pyags_output_path.setText(_translate("MainWindow", pyags_parse_output_path, None))

		# if cascaded: do round 2
		if SETTINGS == 2:
			# calculate elapsed time before round 2
			elapsed = timeit.default_timer() - start_time
			print("\n# Time elapsed (in seconds): " + str(elapsed) + '\n')

			print("# Round 2")
			CASCADED_GRAMMAR_PATH_2 = str(self.edit_cascaded_grammar_path_2.text())
			PREFIX_NONTERMINAL_2 = str(self.edit_prefix_nonterminal_2.text())
			SUFFIX_NONTERMINAL_2 = str(self.edit_suffix_nonterminal_2.text())
			WORD_LIST_PATH = str(self.edit_word_list_path.text())
			NUMBER_OF_AFFIXES = int(self.spinBoxNumberofAffixes.value())

			'''
			words 			- A list of unique words.
			encoded_words 	- A list of unique words in the HEX representation
			hex_chars 		- A list of unique characters in the HEX representation
			'''
			words, encoded_words, hex_chars = process_words(WORD_LIST_PATH)			

			'''
			grammar - a map of the grammar rules.
					The keys represent the unique LHS terms
					The values are a list of the RHS terms of the corresponding keys
			for example - {
						'1 1 Word': ['Prefix Stem Suffix'], 
						'Prefix': ['^^^ Chars', '^^^'], 
						'Stem': ['Chars'], 
						'Suffix': ['Chars $$$', '$$$'], 
						'1 1 Chars': ['Char', 'Char Chars']
						}
			'''
			grammar = read_grammar(CASCADED_GRAMMAR_PATH_2)

			'''
			appended_grammar - grammar map with hex_chars
			'''
			appended_grammar = add_chars_to_grammar(grammar, hex_chars)
			
			file = pyags_parse_output_path
			nonterminal_regex = str(self.edit_nonterminal_regex.text())

			'''
			:param grammar: grammar dictionary
			:param file: file containing grammar morph tree for each word.
			:param number_of_affixes: number indicating how many of the top affixes to return.
			:param nonterminal_regex: regex to copy the affixes from
			:prefix_nonterminal: prefix nonterminal to seed into
			:suffix_nonterminal: suffix nonterminal to seed into
			'''
			appended_grammar = prepare_cascaded_grammar(appended_grammar, file, NUMBER_OF_AFFIXES, nonterminal_regex, PREFIX_NONTERMINAL_2, SUFFIX_NONTERMINAL_2)

			grammar_output_path = FOLDER + '/' + CASCADED_GRAMMAR_PATH_2.split('/')[-1] + '.cascaded.processed'
			write_grammar(appended_grammar, grammar_output_path)

			'''
			<word_list_output_path> and <grammar_output_path> are the inputs to PYAGS.
			'''
			self.edit_pyag_input_grammar_path_2.setText(_translate("MainWindow", grammar_output_path, None))

			PYAG_GRAMMAR_INPUT_PATH = str(self.edit_pyag_input_grammar_path_2.text())

			# a file that contains each words' morphology trees
			pyags_parse_output_path = FOLDER + '/' + RUN_ID + '.1' + 'parse.prs'
			# generated grammar for the run
			pyags_grammar_output_path = FOLDER + '/' + RUN_ID + '.1' + 'grammar.grmr'
			# PYAGS trace file
			pyags_trace_output_path = FOLDER + '/' + RUN_ID + '.1' + 'tracefile.trace'

			bashCommand = PYAG_PATH + " -A " + pyags_parse_output_path + \
			" -r " + R_SEED + " -d " + DEBUGLVL + \
			" -F " + pyags_trace_output_path + \
			" -G " + pyags_grammar_output_path + \
			" -D -E -a 1e-4 -b 1e4 -e 1 -f 1 -g 10 -h 0.1 -w 1 -T 1 -m 0 -n " + ITERATIONS + " -R -1 " + \
			PYAG_GRAMMAR_INPUT_PATH + " < " + PYAG_WORDLIST_INPUT_PATH

			retcode = subprocess.call(bashCommand, shell=True)
			
			# output things
			if retcode != 0:
				print('Error!! Terminated\n')
				return

			print('\t' + grammar_output_path)
			print('\t' + pyags_parse_output_path)
			print('\t' + pyags_grammar_output_path)
			print('\t' + pyags_trace_output_path)

			'''
			<pyags_parse_output_path> is the input to parse.
			'''
			self.edit_pyags_output_path.setText(_translate("MainWindow", pyags_parse_output_path, None))

		# settings == 2 ends

		# calculate elapsed time
		elapsed = timeit.default_timer() - start_time
		print("\n# Time Taken (in seconds): " + str(elapsed))
		print("________________TRAINING COMPLETE________________\n\n")



	def open_parse_file(self):
		name = str(QtGui.QFileDialog.getOpenFileName(self, 'Select PYAG parse output file'))
		if name:
			self.edit_pyags_output_path.setText(name)

	# now removed (covered in segmentation)
	# (the function has been reimplemented and merged with segmentation block)
	# ignore this commented block
	# def parse(self):
	# 	print('PARSING ...')
	# 	# start the timer
	# 	start_time = timeit.default_timer()

	# 	# assigning the values
	# 	PYAG_PARSE_OUTPUT_PATH = str(self.edit_pyags_output_path.text())
	# 	NONTERMINALS_TO_PARSE = str(self.lineEditNonTerminalsToParse.text())

	# 	word_output_path = PYAG_PARSE_OUTPUT_PATH + ".segmented_text"
	# 	dic_output_path = PYAG_PARSE_OUTPUT_PATH + ".segmented_dictionary"

	# 	file = PYAG_PARSE_OUTPUT_PATH
	# 	segmented_text_file = word_output_path
	# 	segmented_dictionary_file = dic_output_path

	# 	min_stem_length = 2  # can be tuned

	# 	word_segmentation_map = parse_PYAGS_segmentation_output(file, min_stem_length, NONTERMINALS_TO_PARSE,
	# 	segmented_text_file, segmented_dictionary_file)

	# 	print("# The following files were generated:")
	# 	print('\t' + word_output_path)
	# 	print('\t' + dic_output_path)

	# 	# calculate elapsed time
	# 	elapsed = timeit.default_timer() - start_time
	# 	print("\n# Time Taken (in seconds): " + str(elapsed))
	# 	print("________________PARSING COMPLETE________________\n\n")



	def open_segmentation_file(self):
		name = str(QtGui.QFileDialog.getOpenFileName(self, 'Select the file to segment words from'))
		if name:
			self.edit_segmentation_file_path.setText(name)

	def segment(self):
		print('SEGMENTING ...')
		# start the timer
		start_time = timeit.default_timer()

		# assigning the values
		FOLDER = str(self.edit_directory_path.text())
		if len(FOLDER) == 0:
			FOLDER = '.'

		SEPARATE_SEGMENTS_BY = ' '	# in accordance with the format required by evaluators
		PYAG_PARSE_OUTPUT_PATH = str(self.edit_pyags_output_path.text())
		NONTERMINALS_TO_PARSE = str(self.lineEditNonTerminalsToParse.text())
		SEGMENTATION_FILE_PATH = str(self.edit_segmentation_file_path.text())
		MULTIWAY_SEGMENTATION = self.checkBoxMultiwaySegmentation.isChecked()

		word_morph_tree_file = PYAG_PARSE_OUTPUT_PATH
		morph_pattern = NONTERMINALS_TO_PARSE
		segmented_text_file = PYAG_PARSE_OUTPUT_PATH + ".seg_text"
		segmented_dictionary_file = PYAG_PARSE_OUTPUT_PATH + ".seg_dic"

		to_parse_file = SEGMENTATION_FILE_PATH
		output_file = FOLDER + '/' + to_parse_file.split('/')[-1] + '.seg_text'
		min_stem_length = 2		# can be tuned
		multiway_segmentation = MULTIWAY_SEGMENTATION

		'''
		Function that takes the output of a word grammar file, creates a segmented
		word dictionary from its output, and uses these to replace the words in a
		text file with their segmented version. This function is a wrapper to the
		functions: parse_PYAGS_segmentation_output and segment_file
		:param word_morph_tree_file: a txt file that contains each words' morphology trees
		:param morph_pattern: a string that denotes the nontermials that will be parsed
		and returned in the final output e.g., "(Prefix|Stem|Suffix)"
		:param segmented_text_file: file location to write all word segmentations
		:param segmented_dictionary_file: file location to write all word segmentations
		and their respective word
		:param to_parse_file: plaintext file containing a tokenized sequence of words.
		(All punctuation marks are separated from words by whitespace such as:
		"The dog ' s bowl is empty . ")
		:param output_file: file to write output to
		:param min_stem_length: integer that represents the minimum length of a
		Stem morph (in characters)
		:param multiway_segmentation: boolean value;
			if value is false, the segmented word will contain a three-way split
			(Prefix+Stem+Suffix)
			if value is true, the segmented word will contain a multi-way split
			if applicable (for example: PrefixMorph+Stem+SuffixMorph+SuffixMorph)
		:return:
		'''
		segment_words(word_morph_tree_file, morph_pattern, segmented_text_file,
				  segmented_dictionary_file, to_parse_file, output_file,
				  min_stem_length, multiway_segmentation)

		prediction_ouput_path = FOLDER + '/' + to_parse_file.split('/')[-1] + ".prediction"
		pred_file = io.open(prediction_ouput_path, "w", encoding='utf-8')

		for line1, line2 in itertools.izip(io.open(to_parse_file, "r", encoding='utf-8'), io.open(output_file, "r", encoding='utf-8')):
			line1 = line1.replace(')', '')
			line1 = line1.replace('(', '')
			line1 = line1.replace('+', SEPARATE_SEGMENTS_BY)
			line2 = line2.replace(')', '')
			line2 = line2.replace('(', '')
			line2 = line2.replace('+', SEPARATE_SEGMENTS_BY)
			pred_file.write(line1[:-1] + '\t' + line2[:-1] + '\n')

		print("# The following files were generated:")
		print('\t' + segmented_text_file)
		print('\t' + segmented_dictionary_file)
		print('\t' + output_file)
		print('\t' + prediction_ouput_path)

		# calculate elapsed time
		elapsed = timeit.default_timer() - start_time
		print("\n# Time Taken (in seconds): " + str(elapsed))
		print("________________SEGMENTATION COMPLETE________________\n\n")


def main():
	print('\n')

	app = QtGui.QApplication(sys.argv)

	# Styles
	# app.setStyle('windows')
	# app.setStyle('cde')
	# app.setStyle('motif')
	# app.setStyle('plastique')
	# app.setStyle('cleanlooks')

	app.setWindowIcon(QtGui.QIcon('icon.png'))

	GUI = Window()

	sys.exit(app.exec_())

if __name__ == '__main__':
	main()