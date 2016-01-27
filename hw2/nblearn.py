import random
import re
import sys

from label_parameters import LabelParameters
from param_reader_writer import ParameterWriter
from review_loader import ReviewLoader


class NaiveLearner:
    def __init__(self, data):
        self.all_data = data
        self.populate_training_data(.9)
        self.learn_parameters()

    def populate_training_data(self, ratio):
        self.labels = []
        self.labelled_data = {}
        self.test_data = {}
        for data in self.all_data:
            if data.label in self.labelled_data:
                self.labelled_data[data.label].append(data)
            else:
                self.labels.append(data.label)
                self.labelled_data[data.label] = [data]

        for label, labeled_data in self.labelled_data.iteritems():
            indices_to_include = random.sample(range(len(labeled_data)), int(len(labeled_data) * ratio))
            self.test_data[label] = []
            for i in range(len(labeled_data)):
                if i not in indices_to_include:
                    self.test_data[label].append(self.labelled_data[label][i])
            self.labelled_data[label] = [self.labelled_data[label][i] for i in indices_to_include]

    def learn_parameters(self):
        self.parameters = LabelParameters(self.words_count_from(self.all_labelled_data()), self.labels)
        for label in self.labels:
            self.parameters.process(self.words_count_from(self.labelled_data[label]), label)
        self.parameters.precompute()

    def words_count_from(self, data):
        words_count = {}
        for item in data:
            words = re.compile('\w+').findall(item.text)
            for word in words:
                if word in words_count:
                    words_count[word] += 1
                else:
                    words_count[word] = 1
        return words_count

    def all_labelled_data(self):
        return reduce(lambda acc, x: acc + x, self.labelled_data.values(), [])

    def sampled_label_probability(self, label):
        count = 0
        for labelled_data in self.labelled_data.values():
            count += len(labelled_data)

        return 1.0 * len(self.labelled_data[label]) / count

    def sampled_label_probabilities(self):
        probabilities = {}
        for label in self.labels:
            probabilities[label] = self.sampled_label_probability(label)
        return probabilities


train_dir = sys.argv[1]

loader = ReviewLoader()
deceptive = loader.load(train_dir + '/positive_polarity/deceptive_from_MTurk', 'deceptive') + \
            loader.load(train_dir + '/negative_polarity/deceptive_from_MTurk', 'deceptive')
truthful = loader.load(train_dir + '/negative_polarity/truthful_from_Web', 'truthful') + \
           loader.load(train_dir + '/positive_polarity/truthful_from_TripAdvisor', 'truthful')
deception_learner = NaiveLearner(deceptive + truthful)

positive = loader.load(train_dir + '/positive_polarity', 'positive')
negative = loader.load(train_dir + '/negative_polarity', 'negative')
negativity_learner = NaiveLearner(positive + negative)

writer = ParameterWriter('nbmodel.txt')
writer.write(deception_learner.parameters, deception_learner.sampled_label_probabilities())
writer.write(negativity_learner.parameters, negativity_learner.sampled_label_probabilities())
