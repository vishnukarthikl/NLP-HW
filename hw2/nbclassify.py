import math
import operator
import os
import random
import re
import sys


class LabelParameters:
    def __init__(self, vocabulary, labels):
        self.vocabulary = vocabulary
        self.labels = labels
        self.word_count_for_label = {}

    def process(self, word_counts, label):
        self.word_count_for_label[label] = word_counts

    def count(self, word, label):
        if label in self.word_count_for_label:
            if word in self.word_count_for_label[label]:
                return self.word_count_for_label[label][word]
        return 0

    def probability(self, word, label):
        return 1.0 * (self.count(word, label) + 1) / (self.total_word_count[label] + len(self.vocabulary))

    def count_for_label(self, label):
        return reduce(lambda acc, x: acc + x, self.word_count_for_label[label].values(), 0)

    def precompute(self):
        self.total_word_count = {}
        for label in self.labels:
            self.total_word_count[label] = self.count_for_label(label)


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
            post_probability[label] = reduce(
                    lambda acc, word: acc + math.log(self.parameters.probability(word, label), 10), words,
                    math.log(probability))

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
negative_reviews = loader.load(train_data_dir + '/positive_polarity/deceptive_from_MTurk', '0') + \
                   loader.load(train_data_dir + '/negative_polarity/deceptive_from_MTurk', '0')
positive_reviews = loader.load(train_data_dir + '/positive_polarity/truthful_from_Web', '1') + \
                   loader.load(train_data_dir + '/negative_polarity/truthful_from_Web', '1')
learner = NaiveLearner(negative_reviews + positive_reviews)

test_data = reduce(lambda acc, x: acc + x, learner.test_data.values(), [])
classifier = NaiveClassifier(learner.parameters, learner.label_probabilities(), test_data)
result = classifier.classify_all()
correct = reduce(lambda acc, x: acc + 1 if x[1] == x[0].label else acc, result, 0)
print 1.0 * correct / len(test_data)
