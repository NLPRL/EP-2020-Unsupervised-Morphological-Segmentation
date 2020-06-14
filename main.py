import string
import sys
import argparse
import re
import os

from os import path
from collections import defaultdict

from utils import *
from grammar_processing_utils import *
from PYAG_utils import *



'''
Function to insert "+" in word count times. Returns every solution that does not have an empty stem.
'''
def insert_splits(word, count, solutions):
    # If count == 0, no more insertions necessary. Append current solution and return.
    if count == 0:
        solutions.append(word)
        return solutions
    # Add a "+" in all possible places
    for i in range(len(word)):
        # Construct new split.
        new_split = word[:i] + "+" + word[i:]
        # Ignore instances of empty morphs. (for example: "e++xample" will be ignored)
        if "++" in new_split:
            continue
        # Call recursively with a decremented count.
        insert_splits(new_split, count-1, solutions)

    return solutions



'''
This function calculates the Maximum Likelihood Estimator for every segmented word candidate.
:param candidate: Segmented word candidate. Always in form of 2 segments, where middle segment is a stem.
    ex. +(kid)+s or k+(id)+s
:param affix_counts: A list of total numbers (one for each Prefix, Stem, and Suffix) of all affixes.
:param affix_totals: A list of dictionaries (one for each Prefix, Stem, and Suffix) containing total counts for each
    affix.
:return: MLE integer
'''
def calculate_MLE(candidate, affix_counts, affix_totals):
    MLE = 1
    EMPTY = "empty"

    morphs = candidate.split("+")
    for x in range(3):
        # x = 0 --> Prefix; x = 1 --> Stem; x = 2 --> Suffix
        affix_morphs = morphs[x]
        #if x == 1:
        #    affix_morphs = affix_morphs[1:len(affix_morphs)-1] # Remove parentheses if necessary.
        affix_count = affix_counts[x]
        affix_total = affix_totals[x]
        if affix_morphs is "":
            affix_morphs = EMPTY
        if affix_morphs in affix_count:
            p_count = affix_count[affix_morphs]
        else: # candidate morph is not in the affix map
            p_count = 0
        MLE *= (p_count / affix_total)
    return MLE



'''
Helper function that takes a segmented_word (separated into Prefix, Stem, Suffix) and splits each affix into
submorphs if it exists.
:param segmented_word: String sequence of morphs separated by "+".
:param affix_maps: List of dictionaries (one for each Prefix, Stem, Suffix) that contains subdivisions of morphs
:return: segmented_word where each morph has been split into submorphs
'''
def split_morphs_into_submorphs(segmented_word, affix_maps):
    morphs = segmented_word.split("+")
    new_morph = []
    start = 0
    end = len(affix_maps)
    if len(morphs) <= 1:
        return segmented_word
    elif len(morphs) == 2:
        if "+(" in segmented_word:
            end = 2
        elif ")+" in segmented_word:
            start = 1
        else:
            return segmented_word
    for x in range(start, end):
        affix_map = affix_maps[x]
        morph = morphs[x]
        if x == 1:
            morph = morph[1:len(morph)-1]
        if morph in affix_map:
            if type(affix_map[morph]) == int:
                new_morph.append(morphs[x])
                continue
            else:
                all_splits = affix_map[morph]
                all_splits_sorted = sorted(all_splits.items(), key=lambda x: x[1], reverse=True)
                new_morph.append(all_splits_sorted[0][0])
    return "+".join(new_morph)




'''
This function morphologically segments all words in a given plaintext file.
:param dic: dictionary containing a list of words in the given language.
It is assumed to be a comprehensive dictionary of the language.
:param txt_file: plaintext file containing a tokenized sequence of words.
(All punctuation marks are separated from words by whitespace such as:
"The dog ' s bowl is empty . ")
:param output_file: file to write output to
:param multiway_segmentaion: boolean value;
    if value is false, the segmented word will contain a three-way split
    (Prefix+Stem+Suffix)
    if value is true, the segmented word will contain a multi-way split
    if applicable (for example: PrefixMorph+Stem+SuffixMorph+SuffixMorph)
:return:
'''
def segment_file(dic, txt_file, output_file, multiway_segmentaion):
    SEGMENT_COUNT = 2
    f_output = open(output_file, "w", encoding='utf-8')

    # Pre-process dictionary to count all affixes (Prefix, Stem, and Suffix).
    prefix_map, stem_map, suffix_map = count_affixes_from_dictionary(dic)
    prefix_total, prefix_counts = count_total_affixes(prefix_map)
    suffix_total, suffix_counts = count_total_affixes(suffix_map)
    stem_total = sum(stem_map.values())
    affix_maps = [prefix_map, stem_map, suffix_map]
    affix_counts = [prefix_counts, stem_map, suffix_counts]
    affix_totals = [prefix_total, stem_total, suffix_total]

    for line in open(txt_file, "r", encoding='utf-8'):
        words = line.split()
        new_line = [] # List containing all the segmented replacements of word in original line.
        for word in words:
            # Save casing of all characters in a word.
            casing = [ch.islower() for ch in word]
            word_low = word.lower()
            # If word already exists in dictionary, replace with existing segmentation.
            if word_low in dic:
                segmented_word = dic[word_low]
                segmented_word = restore_casing(segmented_word, casing)
                new_line.append(segmented_word)
                continue
            elif len(word_low) == 1 and word_low in string.punctuation:
                punctuation = "("
                punctuation += word_low + ")"
                new_line.append(punctuation)
                continue

            # Deduce segmentation from existing affixes.
            all_possible_splits = insert_splits(word_low, SEGMENT_COUNT, [])
            candidate_score_tracker = {}
            for candidate in all_possible_splits:
                score = calculate_MLE(candidate, affix_counts, affix_totals)
                candidate_score_tracker[candidate] = score
            candidate_list_sorted = sorted(candidate_score_tracker.items(), key=lambda x: x[1], reverse=True)

            # Choose highest-scoring candidate and return to original casing.
            if len(candidate_list_sorted) == 0 or candidate_list_sorted[0][1] == 0.0:
                segmented_word = "(" + word_low + ")"
            else:
                segmented_word = candidate_list_sorted[0][0]
            segmented_word = insert_parentheses(segmented_word)
            segmented_word = restore_casing(segmented_word, casing)

            # If multiway_segmentation is True, further split prefixes and affixes into sub-affixes if applicable.
            # For example: irre+(place)+ables --> ir+re+(place)+able+s
            if multiway_segmentaion:
                segmented_word = split_morphs_into_submorphs(segmented_word, affix_maps)

            new_line.append(segmented_word)
        full_line = " ".join(new_line)
        full_line += '\n'
        f_output.write(full_line)

    f_output.close()
    return



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
def segment_words(word_morph_tree_file, morph_pattern, segmented_text_file,
                  segmented_dictionary_file, to_parse_file, output_file,
                  min_stem_length=2, multiway_segmentation=False):
    map = parse_PYAGS_segmentation_output(word_morph_tree_file, min_stem_length, morph_pattern, segmented_text_file,
                            segmented_dictionary_file)
    segment_file(map, to_parse_file, output_file, multiway_segmentation)
    return


# if __name__ == '__main__':
#     main()