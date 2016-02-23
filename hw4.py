def viterbi(obs, states, start_p, trans_p, emit_p):
    V = [{}]
    for i in states:
        V[0][i] = start_p[i] * emit_p[i][obs[0]]
        # Run Viterbi when t > 0
    for t in range(1, len(obs)):
        V.append({})
        for y in states:
            (prob, state) = max((V[t - 1][y0] * trans_p[y0][y] * emit_p[y][obs[t]], y0) for y0 in states)
            V[t][y] = prob
    for i in dptable(V):
        print i
    opt = []
    for j in V:
        for x, y in j.items():
            if j[x] == max(j.values()):
                opt.append(x)
                # the highest probability
    h = max(V[-1].values())
    print 'The steps of states are ' + ' '.join(
            opt) + ' with highest probability of %s' % h  # it prints a table of steps from dictionary


def dptable(V):
    yield " ".join(("%10d" % i) for i in range(len(V)))
    for y in V[0]:
        yield "%.7s: " % y + " ".join("%.7s" % ("%f" % v[y]) for v in V)


states = ('awake', 'asleep')
observations = ('quiet', 'quiet', 'noise')
start_probability = {'awake': 0.8, 'asleep': 0.2}
transition_probability = {
    'awake': {'awake': 0.8, 'asleep': 0.2},
    'asleep': {'awake': 0.2, 'asleep': 0.8}
}
emission_probability = {
    'awake': {'noise': 0.6, 'quiet': 0.4},
    'asleep': {'noise': 0.2, 'quiet': 0.8}
}

viterbi(observations,
        states,
        start_probability,
        transition_probability,
        emission_probability)
