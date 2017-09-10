#! /usr/bin/python

import sys
import re

def get_rare_word_dict(data):
    tracker = {}

    for item in data:
        l = item.split(" ")
        count = int(l[0])
        word = l[3].strip()

        if word not in tracker:
            tracker[word] = 0

        tracker[word] += count

    ret = {}

    for w,c in tracker.iteritems():
        if c < 5:
            ret[w] = True

    return ret

def determine_class(w):

    if re.match("[A-Za-z]+\d+", w):
        return "_NUMERIC_"

    if  w.isupper() and w.isalpha():
        return "_ALL_CAPS_"

    if w[len(w)-1] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        return "_LAST_CAP_"

    return "_RARE_"

def usage():
    print """python classify_rare_words.py [input_file] [counts_file] > [output_file]
            Replace words that occur <5 times in counts_file with a class word:
            _NUMERIC_, _ALL_CAPS_, _LAST_CAP_ or _RARE_
            """

if __name__ == "__main__":

    if len(sys.argv) != 3:
        usage()
        sys.exit(2)

    with open(sys.argv[2]) as f:
        counts_data = f.readlines()
    counts = filter(lambda x: x.find("WORDTAG") >= 0, counts_data)

    rare_dict = get_rare_word_dict(counts)

    with open(sys.argv[1]) as f:
        input_file = f.readlines()

    out = [];

    for l in input_file:
        words = l.split(" ")
        word = words[0].strip()

        if word in rare_dict:
            s = determine_class(word)
        else:
            s = word

        if len(words) != 2:
            out.append("")
        else:
            out.append(s + " " + words[1].strip())

    for item in out:
        print item


