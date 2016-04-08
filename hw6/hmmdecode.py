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
        probability = {(state, 0): self.e(state, words[0]) for state in self.states}
        backpointers = {(state, 0): "" for state in self.states}
        for t in range(1, len(words)):
            for state in self.states:
                (prob, prev) = self.find_max_prev_probability(probability, state, t, words)
                probability[(state, t)] = prob
                backpointers[(state, t)] = prev
        tags = [0] * len(words)
        final_state_probabilities = {state: probability[(state, len(words) - 1)] for state in self.states}
        tags[len(words) - 1] = max(final_state_probabilities, key=final_state_probabilities.get)
        for i in reversed(range(1, len(words))):
            tags[i - 1] = backpointers[(tags[i], i)]
        return zip(words, tags)

    def find_max_prev_probability(self, probability, state, t, words):
        # p = {}
        # for prev in self.states:
        #     prev_probability = probability[(prev, t - 1)]
        #     transition = self.t(prev, state)
        #     emission = self.e(state, words[t])
        #     p[prev] = prev_probability + transition + emission
        # return p
        return max([(probability[(prev, t - 1)] * self.t(prev, state) * self.e(state, words[t]), prev) for prev in
                self.states])

    def e(self, current, next):
        return mod_log(self.probability_for(self.emission, current, next))

    def t(self, current, next):
        return mod_log(self.probability_for(self.transition, current, next))

    def probability_for(self, matrix, current, next):
        if current in matrix and next in matrix[current]:
            return matrix[current][next]
        else:
            return 0


file_path = sys.argv[1]
params = pickle.load(open("hmmmodel.txt", "rb"))
hmmTagger = HMMTagger(params['transition'], params['emission'])
output_lines = []
with open(file_path, "r") as f:
    for line in f:
        result = hmmTagger.process(line)
        join = " ".join(map(lambda r: r[0] + "/" + r[1], result))
        print join
        output_lines.append(join)
print "done"
with open("hmmoutput.txt", "w") as f:
    f.truncate()
    for output in output_lines:
        f.write(output)
        f.write("\n")
