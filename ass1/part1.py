#! /usr/bin/python

import sys

#
# computes emission parameter from data.
# expects data list with elements of the form:
# count WORDTAG label word
# (ex)
# 16 WORDTAG O extraction
# 5 WORDTAG I-GENE SMRT
#
def emission_param(data, write_rares):
  tracker = {}
  out = {}

  label_counts = {}

  for item in data:
      l = item.split(" ")
      count = l[0]
      label = l[2]
      word = l[3].strip()

      if word not in tracker:
        tracker[word] = {}

      if label not in tracker[word]:
        tracker[word][label] = 0

      if label not in label_counts:
        label_counts[label] = 0

      label_counts[label] += int(count)
      tracker[word][label] += int(count)

  # Write out file of infrequent(<5) words.
  rare_words = []
  for w, lc in tracker.iteritems():
      count = reduce(lambda c,tot: tot+c, lc.values(), 0)
      if count < 5:
        rare_words.append(w + "\n")

  if write_rares:
    with open("rare_words.txt", 'w') as f:
        f.writelines(rare_words)

  # for each word find the label with the highest emission param
  for w,lc in tracker.iteritems():
      emissions = 0.0
      l = ""
      for k,v in lc.iteritems():
          em = (float(v)/label_counts[k])
          if em > emissions:
              emissions = em
              l = k
      out[w] = l

  return ["%s %s" % (w, l) for w,l in out.iteritems()]


def usage():
    print """python part1.py [input_file] write_rares > [output_file]
                Read in count file and return training file for tagging.
          """

if __name__ == "__main__":

    if len(sys.argv)!=2 and len(sys.argv)!=3:
        usage()
        sys.exit(2)

    with open(sys.argv[1]) as f:
        data = f.readlines()

    # filter non-WORDTAG lines.
    data = filter(lambda x: x.find("WORDTAG") >= 0, data)

    trained = emission_param(data, len(sys.argv)==3 and sys.argv[2] == "write_rares")

    for item in trained:
        print item