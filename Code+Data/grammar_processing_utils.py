import io
import operator
from PYAG_utils import *
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



'''
:param file: file containing grammar morph tree for each word.
:param n: number indicating how many of the top affixes to return.
:param prefix_marker: name of the prefix nonterminal to search for
:param suffix_marker: name of the suffix nonterminal to search for
:return: top n affixes, all prefixes, and all suffixes
'''
def analyze_affixes(file, n, prefix_marker, suffix_marker):
    prefix_counter = {}
    suffix_counter = {}

    for line in io.open(file, 'r'):
        fields = line.split('(')
        # Search for a nonterminal match with a morph RegEx given as input.
        nonterminals_to_parse = prefix_marker + "|" + suffix_marker
        all_morphs = convert_morph_tree_to_word(fields[1:], nonterminals_to_parse)
        # Separate into respective affix counter.
        for morph in all_morphs:
            morph_type = morph[0]
            is_prefix = re.match(prefix_marker, morph_type)
            if is_prefix:
                if prefix_counter.get(morph[1]):
                    prefix_counter[morph[1]] += 1
                else:
                    prefix_counter[morph[1]] = 1
            else:
                if suffix_counter.get(morph[1]):
                    suffix_counter[morph[1]] += 1
                else:
                    suffix_counter[morph[1]] = 1

    # Return highest n affixes.
    # Sort prefixes.
    prefix_list_sorted = sorted(prefix_counter.items(), key=lambda x: x[1], reverse=True)
    suffix_list_sorted = sorted(suffix_counter.items(), key=lambda x: x[1], reverse=True)

    n_affixes = []
    p = 0  # index for prefix_list_sorted
    s = 0  # index for suffix_list_sorted

    # Final list of x prefixes and y suffixes such that x+y=n
    prefix_x = []
    suffix_y = []

    # If prefix and suffix lists were empty, return empty lists
    if len(prefix_list_sorted) == len(suffix_list_sorted) == 0:
        return n_affixes, prefix_x, suffix_y

    while n > 0:
        if len(prefix_list_sorted) > 0 and (len(suffix_list_sorted) == 0 or
                                            prefix_list_sorted[p][1] > suffix_list_sorted[s][1]):
            try:
                n_affixes.append(prefix_list_sorted[p][0])
                prefix_x.append(prefix_list_sorted[p][0])
            except:
                pass
            p += 1
        else:
            try:
                n_affixes.append(suffix_list_sorted[s][0])
                suffix_y.append(suffix_list_sorted[s][0])
            except:
                pass
            s += 1
        n -= 1

    return n_affixes, prefix_x, suffix_y


'''
:param grammar: grammar dictionary
:param file: file containing grammar morph tree for each word.
:param number_of_affixes: number indicating how many of the top affixes to return.
:param nonterminal_regex: regex to copy the affixes from
:prefix_nonterminal: prefix nonterminal to seed into
:suffix_nonterminal: suffix nonterminal to seed into
'''
def prepare_cascaded_grammar(grammar, file, number_of_affixes, nonterminal_regex, prefix_nonterminal, suffix_nonterminal):
    to_parse = nonterminal_regex[1:len(nonterminal_regex) - 1]  # Remove parentheses.
    prefix_marker, suffix_marker = to_parse.split('|')

    n_affixes, prefix_x, suffix_y = analyze_affixes(file, number_of_affixes, prefix_marker, suffix_marker)

    # Seed the grammar with the prefiexes.
    grammar['1 1 ' + prefix_nonterminal].extend([convert_string_to_hex_chars(prefix) for prefix in prefix_x])
    # Seed the grammar with the suffixes.
    grammar['1 1 ' + suffix_nonterminal].extend([convert_string_to_hex_chars(suffix) for suffix in suffix_y])
    return grammar

    # the code below this self-implemented which has now been replaced by a modified version
    # of an pre-implemented function from https://github.com/rnd2110/MorphAGram, so the code below is now obsolete
    prefix_cnts = {}
    suffix_cnts = {}
    for line in io.open(file, 'r', encoding='utf-8'):
        fields = line.split('(')
        # Search for a field match with a morph RegEx given as input.
        all_morphs = convert_morph_tree_to_word(fields[1:], to_parse)
        for morph in all_morphs:
            if pp in morph[0]:
                if morph[1] + 'P' not in prefix_cnts:
                    prefix_cnts[morph[1] + 'P'] = 0
                prefix_cnts[morph[1] + 'P'] += 1

            if ss in morph[0]:
                if morph[1] + 'S' not in suffix_cnts:
                    suffix_cnts[morph[1] + 'S'] = 0
                suffix_cnts[morph[1] + 'S'] += 1
    
    sorted_prefix_cnts = sorted(prefix_cnts.items(), key=operator.itemgetter(1), reverse=True)
    sorted_suffix_cnts = sorted(suffix_cnts.items(), key=operator.itemgetter(1), reverse=True)
    sorted_cnts = sorted(sorted_prefix_cnts + sorted_suffix_cnts, key=operator.itemgetter(1), reverse=True)

    prefixes = []
    suffixes = []

    for affix in sorted_cnts:
        if number_of_affixes == 0:
            break
        number_of_affixes -= 1
        if affix[0][-1] == 'P':
            prefixes.append(affix[0][:-1])
        if affix[0][-1] == 'S':
            suffixes.append(affix[0][:-1])

    # Seed the grammar with the prefiexes.
    grammar['1 1 ' + prefix_nonterminal].extend([convert_string_to_hex_chars(prefix) for prefix in prefixes])
    # Seed the grammar with the suffixes.
    grammar['1 1 ' + suffix_nonterminal].extend([convert_string_to_hex_chars(suffix) for suffix in suffixes])
    return grammar
