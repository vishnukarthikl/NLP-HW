import math
import operator
import re
import sys

from param_reader_writer import ParameterReader
from review_loader import ReviewLoader


class NaiveClassifier:
    def __init__(self, parameters, label_probabilities, to_classify):
        self.parameters = parameters
        self.label_probabilities = label_probabilities
        self.to_classify = to_classify

    def classify_all(self):
        return map(self.classify, self.to_classify)

    def classify(self, data):
        post_probability = {}
        for label, probability in self.label_probabilities.iteritems():
            words = re.compile('\w+').findall(data.text)
            post_probability[label] = reduce(
                    lambda acc, word: acc + math.log(self.parameters.probability(word, label), 10), words,
                    math.log(probability))

        return data, max(post_probability.iteritems(), key=operator.itemgetter(1))[0]


test_data_dir = sys.argv[1]

loader = ReviewLoader()
truthful = loader.load(test_data_dir + "/negative/truthful", 'truthful') \
           + loader.load(test_data_dir + "/positive/truthful", 'truthful')
deceptive = loader.load(test_data_dir + "/negative/deceptive", 'deceptive') \
            + loader.load(test_data_dir + "/positive/deceptive", 'deceptive')
test_data = truthful + deceptive
label_parameters, prior_label_probability = ParameterReader('nbmodel.txt').read()
classifier = NaiveClassifier(label_parameters, prior_label_probability, test_data)
result = classifier.classify_all()

correct = reduce(lambda acc, x: acc + 1 if x[1] == x[0].label else acc, result, 0)
print 1.0 * correct / len(test_data)
