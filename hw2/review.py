class Review:
    def __init__(self, text, label, path):
        self.label = label
        self.text = text
        self.path = path

    def __str__(self):
        return self.label + ": " + self.text

