
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
PREFIX_NONTERMINAL = ''
SUFFIX_NONTERMINAL = ''

STD_GRAMMAR_OUTPUT_PATH = ''
SS_GRAMMAR_OUTPUT_PATH = ''

PYAG_PATH = ''
PYAG_GRAMMAR_INPUT_PATH = ''
PYAG_WORDLIST_INPUT_PATH = ''
ITERATIONS = '0'
DEBUGLVL = '0'

SEPARATE_SEGMENTS_BY = ' '

PYAG_PARSE_OUTPUT_PATH = ''
NONTERMINALS_TO_PARSE = ''



# def debug():
# 	print("inside debug")
# 	print('SETTINGS', SETTINGS)
# 	print('WORD_LIST_PATH', WORD_LIST_PATH)
# 	print('STD_GRAMMAR_PATH', STD_GRAMMAR_PATH)
# 	print('SS_GRAMMAR_PATH', SS_GRAMMAR_PATH)
# 	print('SS_KNOWLEDGE_PATH', SS_KNOWLEDGE_PATH)


import subprocess
from main import *

import sys
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
		self.pushButtonPreprocess.clicked.connect(self.preprocess)

		# training
		validator = QtGui.QIntValidator(0, 9999)
		self.lineEditRunID.setValidator(validator)
		self.browsePYAG.clicked.connect(self.open_pyag_binary)
		self.browsePYAGGrammar.clicked.connect(self.open_pyag_grammar_input)
		self.browsePYAGWordList.clicked.connect(self.open_pyag_wordlist_input)
		self.pushButtonTrain.clicked.connect(self.train)

		# parsing
		self.browseParseFile.clicked.connect(self.open_parse_file)
		self.pushButtonParse.clicked.connect(self.parse)

		# segmentation
		self.browseSegmentationFile.clicked.connect(self.open_segmentation_file)
		self.pushButtonSegmentWords.clicked.connect(self.segment)


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
		elif SETTINGS == "Scholar Seeded":
			self.widgetStdGrammar.setEnabled(False)
			self.widgetScholarSeededOnly.setEnabled(True)
		else:
			self.widgetStdGrammar.setEnabled(True)
			self.widgetScholarSeededOnly.setEnabled(True)

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

	def preprocess(self):
		print('PREPROCESSING ...')

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

		'''
		words 			- A list of unique words.
		encoded_words 	- A list of unique words in the HEX representation
		hex_chars 		- A list of unique characters in the HEX representation
		'''
		words, encoded_words, hex_chars = process_words(WORD_LIST_PATH)

		word_list_output_path = FOLDER + '/' + WORD_LIST_PATH.split('/')[-1] + '.processed'

		print("# The following files were generated:")
		write_encoded_words(encoded_words, word_list_output_path)
		print('\t' + word_list_output_path)

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

		if SETTINGS == 0 or SETTINGS == 2:
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

		if SETTINGS == 1:
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
		print("\n________________PREPROCESSING COMPLETE________________\n\n")



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

		# assign the paths
		RUN_ID = str(int(self.lineEditRunID.text()))
		FOLDER = str(self.edit_directory_path.text())
		if len(FOLDER) == 0:
			FOLDER = '.'
		PYAG_PATH = str(self.edit_PYAG_binary_path.text())
		PYAG_GRAMMAR_INPUT_PATH = str(self.edit_pyag_input_grammar_path.text())
		PYAG_WORDLIST_INPUT_PATH = str(self.edit_pyag_input_wordlist.text())
		ITERATIONS = str(int(self.spinBoxNumberofIterations.value()))

		# a file that contains each words' morphology trees
		pyags_parse_output_path = FOLDER + '/' + RUN_ID + 'parse.prs'
		# generated grammar for the run
		pyags_grammar_output_path = FOLDER + '/' + RUN_ID + 'grammar.wlt'
		# PYAGS trace file
		pyags_trace_output_path = FOLDER + '/' + RUN_ID + 'tracefile.trace'

		bashCommand = PYAG_PATH + " -A " + pyags_parse_output_path + \
		" -r 123 -d " + DEBUGLVL + \
		" -F " + pyags_trace_output_path + \
		" -G " + pyags_grammar_output_path + \
		" -D -E -a 1e-4 -b 1e4 -e 1 -f 1 -g 10 -h 0.1 -w 1 -T 1 -m 0 -n " + ITERATIONS + " -R -1 " + \
		PYAG_GRAMMAR_INPUT_PATH + " < " + PYAG_WORDLIST_INPUT_PATH

		process = run(bashCommand, shell=True)
		retcode, output, error = process
		if retcode != 0:
			print('Error!! Breaking')
			return
		print("# The following files were generated:")
		print('\t' + pyags_parse_output_path)
		print('\t' + pyags_grammar_output_path)
		print('\t' + pyags_trace_output_path)

		print("\n________________TRAINING COMPLETE________________\n\n")
		return


	def open_parse_file(self):
		name = str(QtGui.QFileDialog.getOpenFileName(self, 'Select PYAG parse output file'))
		if name:
			self.edit_pyags_output_path.setText(name)

	def parse(self):
		SEPARATE_SEGMENTS_BY = str(self.lineEditSeparateSegmentsBy.text())
		if len(SEPARATE_SEGMENTS_BY) == 0:
			SEPARATE_SEGMENTS_BY = ' '
		PYAG_PARSE_OUTPUT_PATH = str(self.edit_pyags_output_path.text())
		NONTERMINALS_TO_PARSE = str(self.lineEditNonTerminalsToParse.text())


	def open_segmentation_file(self):
		name = str(QtGui.QFileDialog.getOpenFileName(self, 'Select the file to segment words from'))
		if name:
			self.edit_segmentation_file_path.setText(name)

	def segment(self):		
		SEPARATE_SEGMENTS_BY = str(self.lineEditSeparateSegmentsBy.text())
		if len(SEPARATE_SEGMENTS_BY) == 0:
			SEPARATE_SEGMENTS_BY = ' '
		SEGMENTATION_FILE_PATH = str(self.edit_segmentation_file_path.text())


def main():

	app = QtGui.QApplication(sys.argv)

	#Style
	# app.setStyle('windows')
	# app.setStyle('cde')
	app.setStyle('motif')
	# app.setStyle('plastique')
	# app.setStyle('cleanlooks')

	app.setWindowIcon(QtGui.QIcon('icon.png'))

	GUI = Window()

	sys.exit(app.exec_())

if __name__ == '__main__':
	main()