from __future__ import division

import math
import os
import sys
from collections import Counter
from math import exp


class Sentence:
    def __init__(self, line):
        line = line.strip()
        self.line = line
        self.words = self.line.split()

    def ngram(self, n):
        return Counter(zip(*[self.words[i:] for i in range(n)]))

    def size(self):
        return len(self.words)

    def ngram_length(self, n):
        return sum(self.ngram(n).values())

    def __str__(self):
        return self.line


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
    def calculate(self, candidate, references):
        precision = 0
        for n in range(1, 5):
            precision += 1 / 4 * math.log(self.precision(candidate, references, n))
        return self.breverity_penality(candidate, references) * exp(precision)

    def breverity_penality(self, c, rs):
        len_c = c.size
        len_r = min(map(lambda r: r.size, rs))
        if len_c > len_r:
            return 1
        else:
            return exp(1 - (len_r / len_c))

    def precision(self, candidate, references, n):
        numerator = 0
        denominator = 0
        for i in range(len(candidate)):
            candidate_sentence = candidate.get(i)
            numerator += max(map(lambda r: self.counts(candidate_sentence, r.get(i), n), references))
            denominator += candidate_sentence.ngram_length(n)
        return numerator / denominator

    def counts(self, candidate, reference, n):
        c_ngrams = candidate.ngram(n)
        r_ngrams = reference.ngram(n)
        count = 0
        for c_ngram, c_count in c_ngrams.iteritems():
            if c_ngram in r_ngrams:
                count += min(c_count, r_ngrams[c_ngram])
        return count


candidate_file_path = sys.argv[1]
reference_path = sys.argv[2]
candidate = TranslationFile(candidate_file_path)
references = []
if os.path.isdir(reference_path):
    for dirpath, dirs, files in os.walk(reference_path):
        for file in files:
            references.append(TranslationFile(os.path.join(dirpath, file)))
else:
    references.append(TranslationFile(reference_path))

calculator = BleuCalculator()
with open("bleu_out.txt", "w") as fout:
    fout.truncate()
    answer = calculator.calculate(candidate, references)
    print answer
    fout.write(str(answer))
