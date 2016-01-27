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
