import operator
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
        if word not in self.word_count:
            return 1.0
        return 1.0 * self.word_count[word] / self.vocabulary_size

    def all_probabilities(self):
        return map(lambda x: (x, self.probability(x)), self.word_count.iterkeys())


class NaiveLearner:
    def __init__(self, data):
        self.all_data = data
        self.populate_training_data(0.7)
        self.learn_parameters()

    def get_parameters(self, label):
        return self.parameters[label]

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
        self.parameters = {}
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

    def label_probability(self, label):
        count = 0
        for labelled_data in self.labelled_data.values():
            count += len(labelled_data)

        return 1.0 * len(self.labelled_data[label]) / count

    def label_probabilities(self):
        probabilities = {}
        for label in self.labels:
            probabilities[label] = self.label_probability(label)
        return probabilities


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
            post_probability[label] = reduce(lambda acc, word: self.parameters[label].probability(word), words,
                                             probability)

        return data, max(post_probability.iteritems(), key=operator.itemgetter(1))[0]


class Review:
    def __init__(self, text, label, path):
        self.label = label
        self.text = text
        self.path = path

    def __str__(self):
        return self.label + ": " + self.text


class ReviewLoader:
    def load(self, directory, label):
        reviews = []
        for root, subFolders, files in os.walk(directory):
            for file in files:
                with open(os.path.join(root, file), 'r') as fin:
                    for lines in fin:
                        reviews.append(Review(lines, label, os.path.join(root, file)))
        return reviews

    def load_without_label(self, directory):
        return self.load(directory, '')


train_data_dir = sys.argv[1]

loader = ReviewLoader()
negative_reviews = loader.load(train_data_dir + '/positive_polarity', '1')
positive_reviews = loader.load(train_data_dir + '/negative_polarity', '0')
learner = NaiveLearner(negative_reviews + positive_reviews)
test_data = reduce(lambda acc, x: acc + x, learner.test_data.values(), [])
classifier = NaiveClassifier(learner.parameters, learner.label_probabilities(), test_data)
result = classifier.classify_all()
correct = reduce(lambda acc, x: acc + 1 if x[1] == x[0].label else acc, result, 0)
print 1.0 * correct / len(test_data)
