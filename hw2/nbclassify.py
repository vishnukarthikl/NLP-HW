import math
import operator
import re
import sys

from param_reader_writer import ParameterReader
from review_loader import ReviewLoader


class ResultWriter:
    def __init__(self, classification_result):
        self.classification_result = classification_result

    def write(self, file_name):
        with open(file_name, 'w') as file:
            file.truncate()
            for path, labels in self.classification_result.iteritems():
                file.write(labels[0] + " " + labels[1] + " " + path)
                file.write('\n')


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


test_dir = sys.argv[1]

loader = ReviewLoader()
# truthful = loader.load(test_dir + "/negative/truthful", 'truthful') \
#            + loader.load(test_dir + "/positive/truthful", 'truthful')
# deceptive = loader.load(test_dir + "/negative/deceptive", 'deceptive') \
#             + loader.load(test_dir + "/positive/deceptive", 'deceptive')
# positive = loader.load(test_dir + '/positive', 'positive')
# negative = loader.load(test_dir + '/negative', 'negative')
#
# test_data1 = truthful + deceptive
# test_data2 = positive + negative
test_data = loader.load_without_label(test_dir)

model_params = ParameterReader('nbmodel.txt').read(2)
deceptive_model_params = model_params[0]
negative_model_params = model_params[1]
deception_classifier = NaiveClassifier(deceptive_model_params[0], deceptive_model_params[1], test_data)
negativity_classifier = NaiveClassifier(negative_model_params[0], negative_model_params[1], test_data)

deception_result = deception_classifier.classify_all()
negative_result = negativity_classifier.classify_all()

classified_result = {}
for result in deception_result:
    classified_result[result[0].path] = [result[1]]
for result in negative_result:
    classified_result[result[0].path].append(result[1])

writer = ResultWriter(classified_result)
writer.write('nboutput.txt')

# correct = reduce(lambda acc, x: acc + 1 if x[1] == x[0].label else acc, deception_result, 0)
# print 1.0 * correct / len(test_data1)
# correct = reduce(lambda acc, x: acc + 1 if x[1] == x[0].label else acc, negative_result, 0)
# print 1.0 * correct / len(test_data2)
