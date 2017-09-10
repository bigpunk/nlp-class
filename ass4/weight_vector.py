#! /usr/bin/python

import sys

class WeightVector(object):

    def __init__(self):
        self.weights = {}
        return

    def __str__(self):
        return repr(self.weights)

    def value(self, key):
        ret = 0
        if key in self.weights:
            ret = self.weights[key]

        return ret

class WeightVectorFromFile(WeightVector):

    def __init__(self, filename):
        super(WeightVectorFromFile, self).__init__()

        with open(filename) as f:
            training_data = f.readlines()

        for l in training_data:
            [rule, score] = l.strip().split(" ")
            self.weights[rule] = float(score)

def usage():
    print """python weight_vector [model_file] > [weight_vectors]
             Reads data from model file and outputs trigram and
             tag weight vectors.
          """

if __name__ == "__main__":

    if len(sys.argv) != 2:
        usage()
        sys.exit(2)

    model_file = sys.argv[1]

    wv = WeightVectorFromFile(model_file)

    print wv