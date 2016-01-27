import csv

from label_parameters import LabelParameters


class ParameterWriter:
    def __init__(self, file):
        self.file = file
        self.models = 0
        with open(self.file, 'w') as file:
            file.truncate()

    def write(self, parameters, prior_probability):
        with open(self.file, 'a') as file:
            param_writer = csv.writer(file, delimiter=',')
            if self.models > 0:
                param_writer.writerow(['******************************'])
            param_writer.writerow(['__labels'] + parameters.labels)
            prior_label_probabilites = []
            for label in parameters.labels:
                prior_label_probabilites.append(prior_probability[label])
            param_writer.writerow(['__priors'] + prior_label_probabilites)
            for word in parameters.vocabulary:
                row = [word]
                for label in parameters.labels:
                    row.append(parameters.count(word, label))
                param_writer.writerow(row)
            self.models += 1


class ParameterReader:
    def __init__(self, file):
        self.file = file

    def read(self, models):
        all_parameters = []
        with open(self.file, 'r') as csvfile:
            param_reader = csv.reader(csvfile, delimiter=',')
            for _ in range(2):
                all_parameters.append(self.read_model(param_reader))
        return all_parameters

    def read_model(self, param_reader):

        label_word_count = {}
        prior_probability = {}

        row = param_reader.next()
        labels = row[1:]
        for label in labels:
            label_word_count[label] = {}

        row = param_reader.next()
        for i, prior in enumerate(row[1:]):
            prior_probability[labels[i]] = float(prior)

        for row in param_reader:
            if len(row) == 1:
                break
            word = row[0]
            for i, word_count in enumerate(row[1:]):
                label_word_count[labels[i]][word] = int(word_count)

        parameters = LabelParameters(label_word_count[labels[0]], labels)
        for label in labels:
            parameters.process(label_word_count[label], label)
        parameters.precompute()

        return parameters, prior_probability
