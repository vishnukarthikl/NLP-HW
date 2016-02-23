def calculate(phrase, label, prior, params):
    words = phrase.split(' ')
    result = prior[label]
    for i, word in enumerate(words):
        if i == 0:
            result *= params[label]['first'][word]
        result *= params[label]['any'][word]
    return result


def calculate_for_all_labels(phrase, prior, params):
    return phrase, calculate(phrase, 'named', prior, params), calculate(phrase, 'not named', prior, params)


def calculate2(phrase, label, prior, params):
    words = phrase.split(' ')
    result = prior[label]
    for i, word in enumerate(words):
        if i == 0:
            result *= params[label]['first'][word]
        else:
            result *= params[label]['not first'][word]
    return result


def calculate_for_all_labels2(phrase, prior, params):
    return phrase, calculate2(phrase, 'named', prior, params), calculate2(phrase, 'not named', prior, params)


def calculate3(phrase, label, prior, params):
    words = phrase.split(' ')
    result = prior[label]
    for i, word in enumerate(words):
        if i == 0:
            result *= params[label]['first'][word]
        else:
            result *= params[label]['any'][word]
    return result


def calculate_for_all_labels3(phrase, prior, params):
    return phrase, calculate3(phrase, 'named', prior, params), calculate3(phrase, 'not named', prior, params)


prior = {'named': 0.3, 'not named': 0.7}
params = {
    'named': {
        'first': {
            'New': 0.32,
            'Bank': 0.12,
            'Mr': 0.08,
            'Red': 0.04,
            'America': 0.24,
            'River': 0.04,
            'York': 0.04,
            'Delhi': 0.04,
            'of': 0.04,
            'Shoes': 0.04
        },
        'any': {'New': 0.22,
                'Bank': 0.08,
                'Mr': 0.05,
                'Red': 0.05,
                'America': 0.22,
                'River': 0.03,
                'York': 0.11,
                'Delhi': 0.14,
                'of': 0.08,
                'Shoes': 0.03
                },
        'not first': {
            'New': 0.05,
            'Bank': .05,
            'Mr': 0.05,
            'Red': .09,
            'America': 0.14,
            'River': .05,
            'York': 0.18,
            'Delhi': .23,
            'of': 0.14,
            'Shoes': .05,
        }
    },
    'not named': {
        'first': {
            'New': 0.36,
            'Bank': 0.20,
            'Mr': 0.02,
            'Red': 0.22,
            'America': 0.02,
            'River': 0.09,
            'York': 0.02,
            'Delhi': 0.02,
            'of': 0.02,
            'Shoes': 0.02
        },
        'any': {
            'New': 0.31,
            'Bank': 0.23,
            'Mr': 0.02,
            'Red': 0.19,
            'America': 0.02,
            'River': 0.08,
            'York': 0.02,
            'Delhi': 0.02,
            'of': 0.02,
            'Shoes': 0.10
        },
        'not first': {
            'New': 0.06,
            'Bank': 0.24,
            'Mr': 0.06,
            'Red': 0.06,
            'America': 0.06,
            'River': 0.06,
            'York': 0.06,
            'Delhi': 0.06,
            'of': 0.06,
            'Shoes': 0.29
        }
    }
}

arr = ['Mr America',
       'Mr Shoes',
       'New Bank',
       'Bank of Delhi',
       'Delhi',
       'Red York',
       'New America',
       'New York',
       'New River',
       'Red River']


def label(named, not_named):
    if named > not_named:
        return 'named'
    else:
        return 'not named'


results1 = map(lambda phrase: calculate_for_all_labels(phrase, prior, params), arr)
for result in results1:
    print '%15s | %f | %f | %s' % (result[0], result[1], result[2], label(result[1], result[2]))

print ""
results2 = map(lambda phrase: calculate_for_all_labels2(phrase, prior, params), arr)
for result in results2:
    print '%15s | %f | %f | %s' % (result[0], result[1], result[2], label(result[1], result[2]))

print ""
results3 = map(lambda phrase: calculate_for_all_labels3(phrase, prior, params), arr)
for result in results3:
    print '%15s | %f | %f | %s' % (result[0], result[1], result[2], label(result[1], result[2]))

for i in range(len(results1)):
    print '%15s | %15s | %15s ' % (
    results1[i][0], label(results1[i][1], results1[i][2]), label(results3[i][1], results3[i][2]))
