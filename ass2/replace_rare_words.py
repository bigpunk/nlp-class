#! /usr/bin/python

import sys
import tree_utils
import json

MIN_WORD_COUNT = 5

def usage():
    print """python replace_rare_words.py [training_file] > output_file
             uses counts from count_cfg_freq to replace words in
             trees that occur <5 times with _RARE_
          """

def words_to_replace():

    ret = []

    unary_counts = tree_utils.get_unary_counts()
    counts = tree_utils.word_count_dict(unary_counts)

    for w,c in counts.iteritems():
        if c < MIN_WORD_COUNT:
            ret.append(w)

    return ret

def remove_words_in_tree(tree, words):

    # base case
    if len(tree) == 2:
        if tree[1] in words:
            return [tree[0].encode("utf-8"), '_RARE_']
        else:
            return [tree[0].encode("utf-8"), tree[1].encode("utf-8")]

    elif len(tree) == 3:
        left = remove_words_in_tree(tree[1], words)
        right = remove_words_in_tree(tree[2], words)
        return [tree[0].encode("utf-8"), left, right]

    else:
        # all nodes should be of length 2 or 3 so we should never be here.
        raise Exception("tree node of wrong length: %d" % len(tree))



if __name__ == "__main__":

    if len(sys.argv) != 2:
        usage()
        sys.exit(2)

    training_file = sys.argv[1]

    tree_utils.run_count_cfg_freq(training_file)

    words = words_to_replace()

    trees = tree_utils.build_trees_from_file(training_file)

    output_trees = []

    for t in trees:
        output_trees.append(remove_words_in_tree(t, words))

    for t in output_trees:
        print json.dumps(t)

