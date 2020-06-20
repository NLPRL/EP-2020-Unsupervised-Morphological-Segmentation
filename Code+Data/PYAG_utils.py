import io
from utils import *

'''
Takes a morph tree such as:
"(Word (Prefix#151 ^^^) (Stem#2 (SubMorphs (SubMorph#22 (Chars (Char 0075)
(Chars (Char 006e)))) (SubMorphs (SubMorph#11 (Chars (Char 0064)))))) (Suffix#2 $$$))"
And convert it to a list of affixes and their respective morph type.

    :param word_nonterminals: List of all nonterminals in the grammar morph tree of a word.
    (ex: ["Word", "Prefix#1", ...])
    :param nonterminals_to_parse: string specifiying which nonterminals to parse by (ex: "Prefix|Stem|Suffix").
    :return: a list of affixes and their respective morph type
'''
def convert_morph_tree_to_word(word_nonterminals, nonterminals_to_parse):
    if nonterminals_to_parse == "Char":
        nonterminals_to_parse = "Chars"

    curr_morph = "" # Keeps track of current morph in word_nonterminals list when iterating.
    global_nonterminal = [] # Keeps track of nonterminal being searched for.
    inner_children = [] # Keeps tracks of nonterminal children in
    all_morphs = [] # Keeps tracks of affixes and their respective morph type
    morph = ""
    last_popped_morph = ""
    to_parse = nonterminals_to_parse.split('|')
    # Search for a nonterminal match with a morph RegEx given as input.
    for curr_nonterminal in to_parse:
        for nonterminal in word_nonterminals:
            m = nonterminal.split()
            # Keep track of children and current morph.
            rgx = r'^' + curr_nonterminal + r'(#[0-9]+)?$'
            r = re.search(rgx, m[0])
            # Store information of current morph if necessary.
            if morph and (len(global_nonterminal) == 0 or r):
                new_morph = (curr_morph, morph)
                all_morphs.append(new_morph)
                if len(global_nonterminal) > 0:
                    global_nonterminal.pop()
                inner_children = []
                morph = ""
                curr_morph = ""
            # Update current morph to search for if different from previous iteration.
            if r:
                curr_morph = m[0]
            if curr_morph is not "":
                if m[0] == curr_morph:
                    global_nonterminal.append(m[0])
                else:
                    inner_children.append(m[0])
                # Pop all ")".
                if ")" in nonterminal:
                    f = list(nonterminal)
                    f.pop()  # Pop '/n' character.
                    while ")" in f:
                        last_ch = f.pop()
                        if len(inner_children):
                            last_popped_morph = inner_children.pop()
                        else:
                            global_nonterminal.pop()
                            curr_morph = ""
                            break
                        if last_popped_morph == "Char":
                            # Parse to hex value and convert.
                            h = nonterminal.split()[1]
                            e = h.find(")")
                            ch = convert_hex_to_string(h[:e])
                            # Add character to word.
                            morph += ch

                        if 'Seeded' in last_popped_morph:
                            # Parse to hex value and convert.
                            xxx = nonterminal.split()[1:]
                            for h in xxx:
                                h = h.replace(')', '')
                                h = h.replace('$$$', '')
                                h = h.replace('^^^', '')
                                if len(h) == 0:
                                    continue
                                ch = convert_hex_to_string(h)
                                # Add character to word.
                                morph += ch

                        if last_ch == '$' or len(inner_children) == 0:
                            if ")" in f and global_nonterminal:
                                global_nonterminal.pop()
                            break
    if morph:
        new_morph = (curr_morph, morph)
        all_morphs.append(new_morph)
    return all_morphs



'''
This function parses the output of the segmented_word morphologies into
a human-readable format that denotes a segmented_word split into its morphemes
separated by a "+" character and converting hex denoted characters
into their respective unicode symbol. It writes these conversions
into 2 files: one file contains only the word segmentations, the other contains
the segmentation along with its respective word.

:param file: a txt file that contains each words' morphology trees
:param min_stem_length: integer that represents the minimum length of a
Stem morph in characters
:param nonterminals_to_parse: a string that denotes the nontermials and the order that will
be parsed and returned in the final output
:param segmented_text_file: file location to write all word segmentations
:param segmented_dictionary_file: file location to write all word segmentations
and their respective word
:return map of words and their respective parsings by affix
(example: "irreplaceables" : "ir+re+(place)+able+s")
'''
def parse_PYAGS_segmentation_output(file, min_stem_length, nonterminals_to_parse, segmented_text_file,
                      segmented_dictionary_file):
    word_segmentation_map = {}
    segmented_word_list = []
    to_parse = nonterminals_to_parse[1:len(nonterminals_to_parse) - 1]  # Remove parentheses.

    for line in io.open(file, 'r', encoding='utf-8'):
        fields = line.split('(')
        # Search for a field match with a morph RegEx given as input.
        all_morphs = convert_morph_tree_to_word(fields[1:], to_parse)
        # Append affixes together separated by a "+".
        segmented_word = ""
        full_word = ""
        contains_stem = "Stem" in nonterminals_to_parse
        stem_morph = ""
        for morph in all_morphs:
            full_word += morph[1]
            # Append "+".
            if segmented_word != "":
                segmented_word += '+'
            # Enclose "Stem#[0-9]+" type morphs in "( ... )"
            morph_type = morph[0]
            is_stem = re.match(r'^Stem#[0-9]+', morph_type)
            if is_stem:
                segmented_word += "("
                stem_morph = morph[1]
            segmented_word += morph[1]
            if is_stem:
                segmented_word += ")"

        # If Stem length is less than min_stem_length, then do not segment word at all.
        if contains_stem and len(stem_morph) < min_stem_length:
            segmented_word = "(" + full_word + ")" # between parentheses
        if word_segmentation_map.get(full_word) is None:
            word_segmentation_map[full_word] = segmented_word
        segmented_word_list.append((full_word, segmented_word))

    # Write all segmented words to segmented_text_file.
    include_word = False
    write_word_segmentations_to_file(segmented_text_file, include_word, segmented_word_list)

    # Write words and their respective segmentation to segmented_text_and_word_file.
    include_word = True
    write_word_segmentations_to_file(segmented_dictionary_file, include_word, word_segmentation_map.items())

    return word_segmentation_map
