#! /usr/bin/python

import sys

def usage():
    print """python replace_rare.py [input_file] > [output_file]
            Replace words from rare_words_file in input_file with _RARE_
          """

if __name__ == "__main__":

    if len(sys.argv)!=3:
        usage()
        sys.exit(2)

    with open(sys.argv[1]) as f:
        input = f.readlines()

    with open(sys.argv[2]) as f:
        rare = f.readlines()

    rare_dict = dict( (k.strip(), True) for k in rare)

    out = [];

    for l in input:
        words = l.split(" ")

        if words[0].strip() in rare_dict:
            s = "_RARE_"
        else:
            s = words[0]

        if len(words) != 2:
            out.append("")
        else:
            out.append(s + " " + words[1].strip())

    for item in out:
        print item