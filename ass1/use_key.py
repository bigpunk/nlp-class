#! /usr/bin/python

import sys

def usage():
    print """python use_key [key_file] [input_file] > [output_file]
                Use key file to tag words from input file.
          """

def make_key_dict(key_data):
    ret = {}

    for item in key_data:
        l = item.split(" ")
        word = l[0].strip()
        label = l[1].strip()

        ret[word] = label

    return ret

def tag_words(key, words):
    ret = []

    for word in words:
        if word == "\n":
            ret.append("")

        else:
            w = word.strip()
            if w in key:
                l = key[w]
            else:
                l = key["_RARE_"]

            ret.append("%s %s" % (w, l))

    return ret

if __name__ == "__main__":

    if len(sys.argv) != 3:
        usage()
        sys.exit(2)

    with open(sys.argv[1]) as f:
        key_data = f.readlines()

    with open(sys.argv[2]) as f:
        words = f.readlines()

    key = make_key_dict(key_data)
    out = tag_words(key, words)

    for item in out:
        print item