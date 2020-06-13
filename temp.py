import sys
print(sys.version)
from main import *
x = convert_string_to_hex_chars("a")
print(x)

y = convert_hex_to_string(x)
print(y)

grammar = {'a':'b', 'c':'d'}
print(grammar)
grammar_file = 'temp.txt'
write_grammar(grammar, grammar_file)