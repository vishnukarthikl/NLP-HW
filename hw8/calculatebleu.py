from __future__ import division

import math
import sys
from math import exp
from collections import Counter


class Sentence:
    def __init__(self, line):
        line = line.translate(None, "!@#$%^&*(){},./?<>\";")
        self.line = line
        self.words = self.line.split()

    def ngram(self, n):
        return Counter(zip(*[self.words[i:] for i in range(n)]))

    def size(self):
        return len(self.words)


class TranslationFile:
    def __init__(self, file_name):
        self.sentences = []
        self.size = 0
        with open(file_name, "r") as f:
            for line in f:
                sentence = Sentence(line)
                self.add(sentence)
                self.size += sentence.size()

    def add(self, sentence):
        self.sentences.append(sentence)

    def get(self, i):
        return self.sentences[i]

    def __len__(self):
        return len(self.sentences)


class BleuCalculator:
    def calculate(self, candidate, reference):
        precision = 0
        for n in range(1, 5):
            precision += math.log(self.precision(candidate, reference, n))
        return 1 / 4 * self.breverity_penality(candidate, reference) * exp(precision)

    def breverity_penality(self, c, r):
        len_c = c.size
        len_r = r.size
        if len_c > len_r:
            return 1
        else:
            return exp(1 - (len_r / len_c))

    def precision(self, candidate, reference, n):
        numerator = 0
        denominator = 0
        for i in range(len(candidate)):
            clip_count, total = self.counts(candidate.get(i), reference.get(i), n)
            numerator += clip_count
            denominator += total
        return numerator / denominator

    def counts(self, candidate, reference, n):
        c_ngrams = candidate.ngram(n)
        r_ngrams = reference.ngram(n)
        count = 0
        for c_ngram, c_count in c_ngrams.iteritems():
            if c_ngram in r_ngrams:
                count += min(c_count, r_ngrams[c_ngram])
        return count, len(c_ngrams)


candidate = TranslationFile(sys.argv[1])
reference = TranslationFile(sys.argv[2])
calculator = BleuCalculator()
with open("bleu_out.txt", "w") as fout:
    fout.truncate()
    answer = calculator.calculate(candidate, reference)
    print answer
    fout.write(str(answer))
