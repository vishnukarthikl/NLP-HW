import sys
from itertools import izip, islice


class ProbabilityMatrix:
    def __init__(self, add_smoothing=False):
        self.counts = {}
        self.smoothing = add_smoothing

    def update_counts(self, current, next):
        if current in self.counts:
            if next in self.counts[current]:
                self.counts[current][next] += 1
            else:
                self.counts[current][next] = 1
        else:
            self.counts[current] = {next: 1}

    def set_vocabulary_size(self, size):
        self.vocabulary_size = size

    def probability(self, current, next):
        if current in self.counts and next in self.counts[current]:
            return 1. * (self.counts[current][next] + 1) / self.vocabulary_size
        else:
            if self.smoothing:
                return 1. / self.vocabulary_size
            else:
                return 1


class HMMLearner:
    def __init__(self):
        self.transition = ProbabilityMatrix(True)
        self.emission = ProbabilityMatrix()
        self.all_words = set()

    def process(self, tagged_sentence):
        word_tags = self.split_word_tags(tagged_sentence)
        words = map(lambda x: x[0], word_tags)
        self.all_words = self.all_words.union(words)
        for current, next in izip(words, islice(words, 1, None)):
            self.transition.update_counts(current, next)
        for word, tag in word_tags:
            self.emission.update_counts(word, tag)

    def learn(self):
        self.transition.set_vocabulary_size(len(self.all_words))

    def split_word_tags(self, tagged_sentence):
        all_word_tags = []
        word_tags = tagged_sentence.split()
        for word_tag in word_tags:
            tag = word_tag[-2:]
            word = word_tag[:-3]
            all_word_tags.append((word, tag))
        return all_word_tags


file_path = sys.argv[1]
hmmLearner = HMMLearner()
with open(file_path, "r") as f:
    for line in f:
        hmmLearner.process(line)
hmmLearner.learn()
hmmLearner.transition.probability('base', 'decimal')
