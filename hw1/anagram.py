import sys


def permute(items):
    if len(items) == 1:
        yield [items[0]]

    for index, value in enumerate(items):
        nested_permutations = permute(items[:index] + items[index + 1:])
        for nested_permutation in nested_permutations:
            yield [value] + nested_permutation[:index] + nested_permutation[index:]


string = sys.argv[1]
with open('anagram_out.txt', 'w') as f:
    f.truncate()
    for p in sorted(map(lambda x: ''.join(x), permute(list(string)))):
        f.write(p)
        f.write('\n')
