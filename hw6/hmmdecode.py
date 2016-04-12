import cPickle as pickle
import sys
from collections import Counter
from math import log


def mod_log(num):
    if num == 0:
        return float('-inf')
    else:
        return log(num)


class HMMTagger:
    def __init__(self, initial, transition, emission):
        self.initial = initial
        self.emission = emission
        self.transition = transition
        self.states = transition.keys()
        self.count = Counter()

    def process(self, line):
        words = line.split()
        probability = [{}] * len(words)
        backpointers = [{}] * len(words)
        probability[0] = self.start_state_probabilities(words)
        backpointers[0] = {state: "" for state in self.states}
        for t in range(1, len(words)):
            probability[t] = {}
            backpointers[t] = {}
            possible_prev_states = self.probable_states(probability, backpointers, t - 1)
            for state in self.states:
                (prob, prev) = self.find_max_prev_probability(probability, state, t, words, possible_prev_states)
                probability[t][state] = prob
                backpointers[t][state] = prev
            if len(self.probable_states(probability, backpointers, t)) == 0:
                for state in self.states:
                    (prob, prev) = self.find_max_prev_probability_without_emission(probability, state, t, words,
                                                                                   possible_prev_states)
                    probability[t][state] = prob
                    backpointers[t][state] = prev

        tags = self.tag_sequence(backpointers, probability, words)
        return zip(words, tags)

    def probable_states(self, probability, backpointer, t):
        return {k: v for k, v in probability[t].iteritems() if v > float('-inf')}.keys()

    def start_state_probabilities(self, words):
        probabilities = {state: self.i(state) + self.e(state, words[0]) for state in self.states}
        non_zero = filter(lambda (s, p): p > float('-inf'), probabilities.iteritems())
        if not non_zero:
            return {state: self.i(state) for state in self.states}
        return probabilities

    def tag_sequence(self, backpointers, probability, words):
        tags = [0] * len(words)
        final_state_probabilities = max(
                [(probability[len(words) - 1][final_state], final_state) for final_state in self.states])
        tags[len(words) - 1] = final_state_probabilities[1]
        for i in reversed(range(1, len(words))):
            tags[i - 1] = backpointers[i][tags[i]]
        return tags

    def find_max_prev_probability(self, probability, state, t, words, previous_states):
        emission = self.e(state, words[t])
        if emission == float('-inf'):
            return emission, '-'
        return max([(probability[t - 1][prev] + self.t(prev, state) + emission, prev) for prev in
                    previous_states])

    def find_max_prev_probability_without_emission(self, probability, state, t, words, previous_states):
        return max([(probability[t - 1][prev] + self.t(prev, state), prev) for prev in previous_states])

    def e(self, current, next):
        return mod_log(self.probability_for(self.emission, current, next))

    def t(self, current, next):
        return mod_log(self.transition[current][next])

    def probability_for(self, matrix, current, next):
        if current in matrix and next in matrix[current]:
            return matrix[current][next]
        else:
            return 0

    def i(self, initial_state):
        return mod_log(self.probability_for(self.initial, "START", initial_state))


def make_string(result):
    return " ".join(map(lambda r: r[0] + "/" + r[1], result))


file_path = sys.argv[1]
params = pickle.load(open("hmmmodel.txt", "rb"))
hmmTagger = HMMTagger(params['initial'], params['transition'], params['emission'])

with open("hmmoutput.txt", "w") as fout:
    fout.truncate()
    with open(file_path, "r") as fin:
        for line in fin:
            result = hmmTagger.process(line)
            fout.write(make_string(result) + "\n")
