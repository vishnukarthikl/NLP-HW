import csv

from label_parameters import LabelParameters


class ParameterWriter:
    def __init__(self, parameters, prior_probability):
        self.parameters = parameters
        self.prior_probability = prior_probability

    def write(self, file):
        with open(file, 'w') as file:
            param_writer = csv.writer(file, delimiter=',')
            param_writer.writerow(['__labels'] + self.parameters.labels)
            prior_label_probabilites = []
            for label in self.parameters.labels:
                prior_label_probabilites.append(self.prior_probability[label])
            param_writer.writerow(['__priors'] + prior_label_probabilites)
            for word in self.parameters.vocabulary:
                row = [word]
                for label in self.parameters.labels:
                    row.append(self.parameters.count(word, label))
                param_writer.writerow(row)


class ParameterReader:
    def __init__(self, file):
        self.file = file

    def read(self):
        labels = []
        with open(self.file, 'r') as csvfile:
            label_word_count = {}
            prior_probability = {}
            param_reader = csv.reader(csvfile, delimiter=',')

            row = param_reader.next()
            labels = row[1:]
            for label in labels:
                label_word_count[label] = {}

            row = param_reader.next()
            for i, prior in enumerate(row[1:]):
                prior_probability[labels[i]] = float(prior)

            for row in param_reader:
                word = row[0]
                for i, word_count in enumerate(row[1:]):
                    label_word_count[labels[i]][word] = int(word_count)

        parameters = LabelParameters(label_word_count[labels[0]], labels)
        for label in labels:
            parameters.process(label_word_count[label], label)
        parameters.precompute()

        return parameters, prior_probability
