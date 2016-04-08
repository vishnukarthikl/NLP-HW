import cPickle as pickle
import sys
from math import log


def mod_log(num):
    if num == 0:
        return float('-inf')
    else:
        return log(num)


class HMMTagger:
    def __init__(self, transition, emission):
        self.emission = emission
        self.transition = transition
        self.states = transition.keys()
        self.initial_probability = {state: 1. / len(self.states) for (state) in self.states}

    def process(self, line):
        words = line.split()
        probability = [{}] * len(words)
        backpointers = [{}] * len(words)
        probability[0] = {state: self.e(state, words[0]) for state in self.states}
        backpointers[0] = {state: "" for state in self.states}
        for t in range(1, len(words)):
            probability[t] = {}
            backpointers[t] = {}
            for state in self.states:
                (prob, prev) = self.find_max_prev_probability(probability, state, t, words)
                probability[t][state] = prob
                backpointers[t][state] = prev
        tags = [0] * len(words)
        final_state_probabilities = max(
                [(probability[len(words) - 1][final_state], final_state) for final_state in self.states])
        tags[len(words) - 1] = final_state_probabilities[1]
        for i in reversed(range(1, len(words))):
            tags[i - 1] = backpointers[i][tags[i]]
        return zip(words, tags)

    def find_max_prev_probability(self, probability, state, t, words):
        p = []
        for prev in self.states:
            prev_probability = probability[t - 1][prev]
            transition = self.t(prev, state)
            emission = self.e(state, words[t])
            p.append((prev_probability + transition + emission, prev))
        return max(p)
        # return max([(probability[(prev, t - 1)] * self.t(prev, state) * self.e(state, words[t]), prev) for prev in
        #         self.states])

    def e(self, current, next):
        p = self.probability_for(self.emission, current, next)
        return mod_log(p)

    def t(self, current, next):
        return mod_log(self.probability_for(self.transition, current, next))

    def probability_for(self, matrix, current, next):
        if current in matrix and next in matrix[current]:
            return matrix[current][next]
        else:
            return 1e-20


def make_string(result):
    return " ".join(map(lambda r: r[0] + "/" + r[1], result))

file_path = sys.argv[1]
params = pickle.load(open("hmmmodel.txt", "rb"))
hmmTagger = HMMTagger(params['transition'], params['emission'])


with open("hmmoutput.txt", "w") as fout:
    fout.truncate()
    with open(file_path, "r") as fin:
        for line in fin:
            result = hmmTagger.process(line)
            fout.write(make_string(result) + "\n")
