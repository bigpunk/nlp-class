#! /usr/bin/python

import json
import os

TMP_COUNT_FILE = 'count_tmp.txt'

def build_trees_from_file(filename):

    ret = []

    with open(filename) as f:
        data = f.readlines()

    for d in data:
        ret.append(json.loads(d))

    return ret

def run_count_cfg_freq(input_file):
    cmd = "python count_cfg_freq.py %s > %s" % (input_file, TMP_COUNT_FILE)
    os.system(cmd)

def nonterminal_list(total_rule_counts):
    return total_rule_counts.keys()

def rule_list(binary_rule_counts):
    return binary_rule_counts.keys()

def rule_starts_with(x, rule):
    return x == (rule.split(" ")[0])

#
# lines of the form: 121 BINARYRULE SQ+VP VERB NP
#
def get_binary_counts():

    ret = {}

    with open(TMP_COUNT_FILE) as f:
        training_data = f.readlines()

    binary_counts = filter(lambda x: x.find("BINARYRULE") >= 0, training_data)

    for c in binary_counts:
        l = c.strip().split(" ", 2)
        count = float(l[0])
        rule = l[2]

        if rule not in ret:
            ret[rule] = 0

        ret[rule] += count

    return ret

#
# lines of the form: 2 UNARYRULE NOUN tax
#
def get_unary_counts():

    ret = {}

    with open(TMP_COUNT_FILE) as f:
        training_data = f.readlines()

    unary_counts = filter(lambda x: x.find("UNARYRULE") >= 0, training_data)

    for c in unary_counts:
        l = c.strip().split(" ", 3)
        count = float(l[0])
        type = l[2]
        word = l[3]

        if word not in ret:
            ret[word] = {}

        if type not in ret[word]:
            ret[word][type] = 0

        ret[word][type] += count

    return ret

#
# creates dict with word counts from UNARYRULE dict.
#
def word_count_dict(unary_counts):

    ret = {}

    for word,type_count in unary_counts.iteritems():
        ret[word] = sum(type_count.values())

    return ret

#
# lines of the form: 656 NONTERMINAL NP+NOUN
#
def get_nonterminal_counts():

    ret = {}

    with open(TMP_COUNT_FILE) as f:
        training_data = f.readlines()

    non_t_counts = filter(lambda x: x.find("NONTERMINAL") >= 0, training_data)

    for c in non_t_counts:
        l = c.strip().split(" ", 2)
        count = float(l[0])
        rule = l[2]

        if rule not in ret:
            ret[rule] = 0

        ret[rule] += count

    return ret

