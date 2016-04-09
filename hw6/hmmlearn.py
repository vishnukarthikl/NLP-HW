import cPickle as pickle
import sys
from itertools import izip, islice


class ProbabilityMatrix:
    def __init__(self, add_smoothing=False):
        self.counts = {}
        self.smoothing = add_smoothing
        self.probability = {}

    def update_counts(self, current, next):
        if current in self.counts:
            if next in self.counts[current]:
                self.counts[current][next] += 1
            else:
                self.counts[current][next] = 1
        else:
            self.counts[current] = {next: 1}

    def vocabulary_size(self):
        return len(self.counts.keys())

    def calculate_transition_probability(self):
        for current in self.counts.keys():
            self.probability[current] = {}
            next_count = self.counts[current]
            total = sum(next_count.values())
            for next in self.counts.keys():
                if next in self.counts[current]:
                    count = self.counts[current][next]
                    if self.smoothing:
                        self.probability[current][next] = (count + 1.) / (total + self.vocabulary_size())
                    else:
                        self.probability[current][next] = 1. * count / total
                else:
                    if self.smoothing:
                        self.probability[current][next] = 1. / self.vocabulary_size()
                    else:
                        self.probability[current][next] = 0

    def calculate_emission_probability(self):
        for current, next_count in self.counts.iteritems():
            self.probability[current] = {}
            total = sum(next_count.values())
            for next in next_count:
                count = self.counts[current][next]
                if self.smoothing:
                    self.probability[current][next] = (count + 1.) / (total + self.vocabulary_size())
                else:
                    self.probability[current][next] = 1. * count / total

    def calculate_initial_probability(self, tags):
        start_state = "START"
        counts = self.counts[start_state]
        self.probability[start_state] = {}
        total = sum(counts.values())
        for tag in tags:
            if tag in counts:
                self.probability[start_state][tag] = 1. * counts[tag] / total
            else:
                self.probability[start_state][tag] = 0


class HMMLearner:
    def __init__(self):
        self.transition = ProbabilityMatrix(True)
        self.emission = ProbabilityMatrix()
        self.initial = ProbabilityMatrix(False)
        self.all_tags = set()

    def process(self, tagged_sentence):
        word_tags = self.split_word_tags(tagged_sentence)
        tags = map(lambda x: x[1], word_tags)
        self.all_tags = self.all_tags.union(tags)
        self.initial.update_counts("START", tags[0])
        for current, next in izip(tags, islice(tags, 1, None)):
            self.transition.update_counts(current, next)
        for word, tag in word_tags:
            self.emission.update_counts(tag, word)

    def learn(self):
        self.all_tags = self.emission.counts.keys()
        self.initial.calculate_initial_probability(self.all_tags)
        self.transition.calculate_transition_probability()
        self.emission.calculate_emission_probability()

    def split_word_tags(self, tagged_sentence):
        all_word_tags = []
        word_tags = tagged_sentence.split()
        for word_tag in word_tags:
            tag = word_tag[-2:]
            word = word_tag[:-3]
            all_word_tags.append((word, tag))
        return all_word_tags

    def states(self):
        return self.all_tags

    def to_dump(self):
        return {'transition': self.transition.probability, 'emission': self.emission.probability,
                'initial': self.initial.probability}


file_path = sys.argv[1]
hmmLearner = HMMLearner()
with open(file_path, "r") as f:
    for line in f:
        hmmLearner.process(line)
hmmLearner.learn()
pickle.dump(hmmLearner.to_dump(), open("hmmmodel.txt", "wb"))
