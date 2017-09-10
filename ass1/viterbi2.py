#! /usr/bin/python

import sys

#
# return emissions dict from counts.
#
def make_emissions_dict(word_counts):
    tracker = {}
    label_counts = {}

    for line in word_counts:
        l = line.split(" ")
        count = l[0]
        label = l[2]
        word = l[3].strip()

        if word not in tracker:
            tracker[word] = {}

        if label not in tracker[word]:
            tracker[word][label] = 0

        if label not in label_counts:
            label_counts[label] = 0

        label_counts[label] += float(count)
        tracker[word][label] += float(count)

    ret = {}

    for word,lcs in tracker.iteritems():
        for label,count in lcs.iteritems():

            key = "%s|%s" % (word, label)
            ret[key] = count / label_counts[label]

    return ret

#
# make ngram dict from input strings (ex) "11804 3-GRAM O O I-GENE"
#
def make_q_dict(ngrams):
    ret = {}

    two_grams = {}
    three_grams = {}
    labels = []

    for item in ngrams:
        l = item.split(" ", 2)
        count = l[0]
        type = l[1]
        key = l[2].strip()

        if type == "3-GRAM":
            three_grams[key] = float(count)

        elif type == "2-GRAM":
            two_grams[key] = float(count)

        # save labels for generating q values.
        ks = key.split(" ")
        for k in ks:
            if k not in labels:
                labels.append(k)

    # compute q values.
    for i in labels:
        for i_minus_1 in labels:
            for i_minus_2 in labels:
                three_key = "%s %s %s" % (i_minus_2, i_minus_1, i)
                two_key = "%s %s" % (i_minus_2, i_minus_1)

                # skip the few invalid keys that we generate.
                if two_key not in two_grams or three_key not in three_grams:
                    continue

                q_key = "%s|%s,%s" % (i, i_minus_2, i_minus_1)
                ret[q_key] = three_grams[three_key] / two_grams[two_key]

    return ret

#
# Make a list of sentences from input data.
#
def get_sentences_from_input(data):
    ret = []
    temp = []

    # each sentences ends with a newline so just check for length 1 word.
    for word in data:
        if len(word) == 1:
            ret.append(temp)
            temp = []
        else:
            temp.append(word.strip())

    return ret

def viterbi(q_dict, em_dict, sentences):

    ret = []

    for words in sentences:
        k_tags = ["O", "I-GENE"]
        k_one_tags = ["*"]
        k_two_tags = ["*"]
        pi = {"0,*,*" : 1}
        bp = {}
        i = 1

        print "em_dict[':|O']: %s  em_dict[':|I-GENE']: %s" % (em_dict[':|O'], em_dict[':|I-GENE'])

        for word in words:
            for u in k_one_tags:
                for v in k_tags:

                    max_pi = -1
                    for w in k_two_tags:
                        pi_key = "%d,%s,%s" % (i-1,w,u)
                        q_key = "%s|%s,%s" % (v,w,u)

                        e_key = "%s|%s" % (word, v)
                        if e_key not in em_dict:
                            temp_e_key = "%s|%s" % (word, "I-GENE" if v =="O" else "O")
                            if temp_e_key in em_dict:
                                em_dict[e_key] = 0
                            else:
                                e_key = "_RARE_|%s" % (v)
                        print "Using pi_key: %s" % pi_key
                        prob = pi[pi_key] * q_dict[q_key] * em_dict[e_key]

                        if prob > max_pi:
                            max_pi = prob
                            new_key = "%d,%s,%s" % (i,u,v)
                            bp[new_key] = w
                            pi[new_key] = prob

            k_two_tags = k_one_tags
            k_one_tags = k_tags
            i += 1

        # now that we are out of words find labels that max prob at end.
        temp_pi = 0
        yn = 0
        yn1 = 0
        for v in k_tags:
            for u in k_one_tags:

                q_key = "STOP|%s,%s" % (u, v)
                pi_key = "%d,%s,%s" % (i-1, u, v)
                prob = pi[pi_key] * q_dict[q_key]

                if prob > temp_pi:
                    yn = v
                    yn1 = u
                    temp_pi = prob

        ys = [yn, yn1]
        yp1 = yn1
        yp2 = yn

        for k in range(1, i - 2):
            bp_key = "%d,%s,%s" % (i - k, yp1, yp2)
            y = bp[bp_key]
            ys.append(y)

            yp2 = yp1
            yp1 = y

        ys.reverse()
        for i in range(len(words)):
            ret.append("%s %s" % (words[i], ys[i]))

        # add a newline after each sentence during output.
        ret.append("")

    return ret

def usage():
    print """python viterbi.py [training_file] [input_to_label] > [output_file]
              Read in training file and file to label.  output file with labels.
          """

if __name__ == "__main__":

    if len(sys.argv) != 3:
        usage()
        sys.exit(2)

    with open(sys.argv[1]) as f:
        training_data = f.readlines()

    # filter lines with WORDTAG so we get things like:
    # 3491 3-GRAM I-GENE O I-GENE
    ngrams = filter(lambda x: x.find("WORDTAG") == -1, training_data)

    # filter lines without WORDTAG so we get counts like:
    # 15 WORDTAG O cartilage
    word_counts = filter(lambda x: x.find("WORDTAG") >= 0, training_data)

    # get a dict of q values from ngram counts.
    q_dict = make_q_dict(ngrams)

    # make a dict that we can use to compute emissions values.
    em_dict = make_emissions_dict(word_counts)

    # read input file and get a list of sentences to label.
    with open(sys.argv[2]) as f:
        input_data = f.readlines()

    input_sentences = get_sentences_from_input(input_data)

    output = viterbi(q_dict, em_dict, input_sentences)

    for item in output:
        print item