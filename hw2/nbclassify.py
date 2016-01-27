import os
import random
import re
import sys


class LabelParameter:
    def __init__(self, label):
        self.vocabulary_size = 0
        self.label = label
        self.word_count = {}

    def add_word(self, word):
        if word in self.word_count:
            self.word_count[word] += 1
        else:
            self.word_count[word] = 1
        self.vocabulary_size += 1

    def probability(self, word):
        return 1.0 * self.word_count[word] / self.vocabulary_size

    def all_probabilities(self):
        return map(lambda x: (x, self.probability(x)), self.word_count.iterkeys())


class NaiveLearner:
    def __init__(self, data):
        self.labelled_data = {}
        self.labels = []
        self.parameters = {}
        self.all_data = data
        self.populate_training_data(0.7)
        self.learn_parameters()

    def get_parameters(self, label):
        return self.parameters[label]

    def populate_training_data(self, ratio):
        for data in self.all_data:
            if data.label in self.labelled_data:
                self.labelled_data[data.label].append(data)
            else:
                self.labels.append(data.label)
                self.labelled_data[data.label] = [data]

        for label, labeled_data in self.labelled_data.iteritems():
            self.labelled_data[label] = [self.labelled_data[label][i] for i in
                                         random.sample(range(len(labeled_data)), int(len(labeled_data) * ratio))]

    def learn_parameters(self):
        for label in self.labels:
            self.parameters[label] = self.process(self.labelled_data[label], label)

    def process(self, data, label):
        parameter = LabelParameter(label)
        for item in data:
            words = re.compile('\w+').findall(item.text)
            map(parameter.add_word, words)
        return parameter

    def word_probability_given_label(self, word, label):
        return self.parameters[label].probability(word)

    def probabilities(self, label):
        return self.parameters[label].all_probabilities()


class Review:
    def __init__(self, text, label):
        self.label = label
        self.text = text

    def __str__(self):
        return self.label + ": " + self.text


class ReviewLoader:
    def load(self, directory, label):
        reviews = []
        for root, subFolders, files in os.walk(directory):
            for file in files:
                with open(os.path.join(root, file), 'r') as fin:
                    for lines in fin:
                        reviews.append(Review(lines, label))
        return reviews


train_data_dir = sys.argv[1]

loader = ReviewLoader()
negative_reviews = loader.load(train_data_dir + '/positive_polarity', '1')
positive_reviews = loader.load(train_data_dir + '/negative_polarity', '0')
learner = NaiveLearner(negative_reviews + positive_reviews)
print learner.probabilities('0')
