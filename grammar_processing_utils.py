import io
from utils import *

'''
This function reads a grammar file and returns a map of the grammar rules.
The keys represent the unique LHS terms
The values are a list of the RHS terms of the corresponding keys
'''
def read_grammar(grammar_file):
    grammar = defaultdict(list)
    # Loop over the file and process rule by rule.
    for line in open(grammar_file):
        line = line.strip()
        # Ignore comment lines.
        if not line or line.startswith('#') or line.startswith('//'):
            continue
        # Read the current rule.
        columns = line.partition('-->')
        key = columns[0].strip()
        value = columns[2].strip()
        # Convert terminal chcratcers within "(" and ")" into their HEX representation.
        match = re.search(r'(\(.*?\))', value)
        while match:
            value = convert_string_to_hex_chars(match.group(0)[1:-1])
            value = line.replace(match.group(0), replacement)
            match = re.search(r'(\(.*?\))', value)
        grammar[key].append(value)
    return grammar



'''
This function writes a grammar map into a file.
'''
def write_grammar(grammar, grammar_file):
    grammar_writer = io.open(grammar_file, 'w', encoding="utf-8")
    for key in grammar:
        for value in grammar[key]:
            grammar_writer.write(key + u' --> ' + value + '\n')



'''
This function adds hex_chars to the grammar map
'''
def add_chars_to_grammar(grammar, hex_chars):
    grammar['1 1 Char'].extend(hex_chars)
    return grammar



'''
This function seeds a grammar tree with prefixes and suffixes read from a file (lk_file where lk stands for Linguistic Knowledge).
The nonterminals under which the affixes are inserted are denoted by prefix_nonterminal and suffix_nonterminal for prefixes and suffixes, respectively.
'''
def prepare_scholar_seeded_grammar(grammar, lk_file, prefix_nonterminal, suffix_nonterminal):
    # Read the prefixes and suffixe from the file.
    prefixes, suffixes = read_linguistic_knowledge(lk_file)
    # Seed the grammar with the prefiexes.
    grammar['1 1 ' + prefix_nonterminal].extend([convert_string_to_hex_chars(prefix) for prefix in prefixes])
    # Seed the grammar with the suffixes.
    grammar['1 1 ' + suffix_nonterminal].extend([convert_string_to_hex_chars(suffix) for suffix in suffixes])
    return grammar



'''
This function reads the prefixes and suffixes in an lk_file (lk stands for Linguistic Knowledge).
'''
def read_linguistic_knowledge(lk_file):
    prefixes = []
    suffixes = []
    read_prefixes = False
    read_suffixes = False
    # Loop over the lines in the file.
    for line in open(lk_file):
        line = line.strip()
        if line == '':
            continue
        # Read prefixes.
        if line == '###PREFIXES###':
            read_prefixes = True
            read_suffixes = False
        # Read suffixes.
        elif line == '###SUFFIXES###':
            read_prefixes = False
            read_suffixes = True
        elif line.startswith('###'):
            break
        else:
            # Read a merker line.
            if read_prefixes:
                prefixes.append(line)
            elif read_suffixes:
                suffixes.append(line)
    return prefixes, suffixes
