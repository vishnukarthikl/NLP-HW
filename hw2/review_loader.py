import os
from review import Review

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
