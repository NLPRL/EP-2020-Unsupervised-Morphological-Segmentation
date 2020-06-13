#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string
import sys
import argparse
import re
import os
import io

from os import path
from collections import defaultdict



# Convert a string to HEX
def convert_string_to_hex_chars(string):
    hex_chars = []
    for char in list(string):
        hex_char = char.encode("utf-16").encode("hex")
        hex_char = '0' * (4 - len(hex_char)) + hex_char
        hex_chars.append(hex_char)
    return ' '.join(hex_chars)

# Convert HEX to a string
def convert_hex_to_string(hex):
    s = hex.decode("hex").decode('utf-16')
    # Remove trailing new line character if necessary.
    if list(s)[0] == '\x00':
        return str(list(s)[1])
    else:
        return s



'''
This function reads a file of words and produces three lists:
1- A list of unique words.
2- A list of unique words in the HEX representation
3- A list of unique characters in the HEX representation
'''
def process_words(word_list_file):
    words = []
    encoded_words = []
    hex_chars = []
    # Loop over the file and process word by word.
    for line in io.open(word_list_file, encoding="utf-8"):
        line = line.strip()
        # Ignore comment lines.
        if not line or line.startswith('#') or line.startswith('//'):
            continue
        word = line
        words.append(word)
        # Convert the word to its HEX representation.
        encoded_word = convert_string_to_hex_chars(word)
        encoded_words.append(encoded_word)
        # Keep track of the unique characters (in the HEX representation).
        hex_chars.extend(encoded_word.split())
    # Sort the outputs.
    words.sort()
    encoded_words.sort()
    hex_chars.sort()
    return set(words), set(encoded_words), set(hex_chars)



'''
This function writes a list of encoded words (in the HEX representation) into a file.
'''
def write_encoded_words(encoded_words, word_list_file):
    word_list_writer = open(word_list_file, 'w')
    word_list_writer.writelines('^^^ %s $$$\n' % word for word in encoded_words)



'''
Writes word segmentations to file provided as input.
:param file: File to write to
:param include_word: Boolean whether to write non-segmented word to file
:param word_list: list of words to write
'''
def write_word_segmentations_to_file(file, include_word, word_list):
    f = io.open(file, "w", encoding='utf-8')
    for w in sorted(word_list):
        if len(w[0]) == 0:
            continue
        new_line = ""
        if include_word:
            new_line += w[0] + "\t"
        new_line += w[1] + '\n'
        f.write(new_line)
    f.close()



'''
This method is a helper function that keeps track of all instances of morphs. Used to pre-process text.
:param affix_morphs: String sequence of morphs to be counted.
:param affix_count: Dictionary of all seen morphs and their counts.
'''
def count_affixes_from_segmented_word(affix_morphs, affix_count):
    if affix_morphs == "":
        if "empty" in affix_count:
            affix_count["empty"] += 1
            return
        else:
            affix_count["empty"] = 1
            return
    all_affixes = affix_morphs.split("+")  # List of affixes ex. ['over', 're'].
    joint_affixes = "".join(all_affixes)  # Join all prefixes ex. overre.
    if affix_count.get(joint_affixes):
        if affix_count[joint_affixes].get(affix_morphs):
            affix_count[joint_affixes][affix_morphs] += 1
        else:
            affix_count[joint_affixes][affix_morphs] = 1
    else:
        affix_count[joint_affixes] = {affix_morphs: 1}
    return



'''
Helper function that counts all instances of seen stems.
:param segmented_word: String sequence of morphs separated by "+".
:param stem_count: Dictionary of all instances of stems and their counts.
'''
def count_stems_from_segmented_word(segmented_word, stem_count):
    if segmented_word == "":
        if "empty" in stem_count:
            stem_count["empty"] += 1
        else:
            stem_count["empty"] = 1
    while "(" in segmented_word:  # There may be multiple stems in a word. If so, they are all separate entries in map.
        p_open = segmented_word.find("(")
        p_close = segmented_word.find(")")
        stem_morph = segmented_word[p_open+1:p_close]
        if stem_morph in stem_count:
            stem_count[stem_morph] += 1
        else:
            stem_count[stem_morph] = 1
        segmented_word = segmented_word[p_close+1:]
    return



'''
Helper function that pre-processes all counts of all affixes in language dictionary.
:param dic: Dictionary of all words (presumably a comprehensive dictionary of a language) and their corresponding
morphs (ex: {"irreplaceables": "ir+re+place+able+s"}
:return: 3 dictionaries: 1) All prefix instances and their counts 2) All stem instances and their counts 3) All
suffix instances and their counts.
'''
def count_affixes_from_dictionary(dic):
    prefix_count = {}
    stem_count = {}
    suffix_count = {}

    for item in dic.items():
        segmented_word = item[1]
        full_word = item[0]

        # If prefix exists, count and store prefixes.
        if "+(" in segmented_word:
            morphs = segmented_word.split("+(")
            prefix_morphs = morphs[0] # morphs[0] contains sequence of prefixes ex. over+re+(act) --> over+re.
            count_affixes_from_segmented_word(prefix_morphs, prefix_count)
        else:
            count_affixes_from_segmented_word("", prefix_count)

        # If stem exists, count and store stems.
        if "(" in segmented_word:
            count_stems_from_segmented_word(segmented_word, stem_count)
        else:
            count_stems_from_segmented_word(segmented_word, stem_count)

        # If suffix exists, count and store suffixes.
        if ")+" in segmented_word:
            morphs = segmented_word.split(")+")
            # If there are multiple stems, you want to take the last found instance ex. (abc)+(def)+xyz.
            suffix_morphs = morphs[len(morphs)-1]
            if ")" in suffix_morphs: # No suffix exists. ex. (abc)+(def).
                continue
            count_affixes_from_segmented_word(suffix_morphs, suffix_count)
        else:
            count_stems_from_segmented_word("", suffix_count)

    return prefix_count, stem_count, suffix_count



'''
Helper that counts the total number of affixes.
:param affix_count: A dictionary containing all counts of all instances of an affix sequence
(ex: "redis": {"re+dis": 5, "red+is": 1})
:return: an integer total of all affix sequences seen, a dictionary containing just the total counts of a given
sequence (Using the above example:  6, {"redis": 6})
'''
def count_total_affixes(affix_count):
    TOTAL = 0
    total_affix_count = {}
    for affix, dic in affix_count.items():
        if affix == "empty":
            continue
        affix_sum = sum(dic.values())
        total_affix_count[affix] = affix_sum
        TOTAL += affix_sum

    return TOTAL, total_affix_count



'''
Helper function that restores the casing seen in plaintext file.
:param segmented_word: String morph sequence separated by "+".
:param casing: List of booleans for all characters in segmented_word; True = lowercase False = uppercase
:return: segmented_word with proper casings
'''
def restore_casing(segmented_word, casing):
    n = 0 # casing index
    restored_segmented_word = ""
    for ch in segmented_word:
        if ch == "+" or ch == "(" or ch == ")" or ch == '̇':
            restored_segmented_word += ch
            # Do not increment n.
            continue
        if not casing[n]:
            new_ch = ch.upper()
            restored_segmented_word += new_ch
        else:
            restored_segmented_word += ch
        n += 1

    return restored_segmented_word



'''
Helper function that takes segmented_word and adds a parentheses around the middle morph=Stem
:param segmented_word: String sequence of morphs
:return: segmented_word with parentheses around stem
'''
def insert_parentheses(segmented_word):
    if "(" not in segmented_word:
        # Find first "+" and add "(" at the end.
        p_op = segmented_word.find("+")
        new_segmented_word = segmented_word[:p_op+1]
        new_segmented_word += "("
        # Find second "+" and add ")" at the end.
        next_segment = segmented_word[p_op+1:]
        p_cl = next_segment.find("+")
        new_segmented_word += next_segment[:p_cl]
        new_segmented_word += ")"
        # Add remainder of the word.
        new_segmented_word += next_segment[p_cl:]
        return new_segmented_word
    else:
        return segmented_word
