# given: n-best list, language model, language labels
# transition probabilities: from lm
# emission probabilities from n-best list
import sys, math, re, nltk, argparse

transitions = {}
emissions = {}
best_edge = {}
best_score = {}
r1 = .1
r2 = .2
r3 = .7
lang_ids = []
char_lm = {}
max_trans = 0.
min_trans = 0.
dictionary = {}


def normalize_emission():
    for key in emissions.keys():
        total = 0.
        for skey in emissions[key].keys():
            total += emissions[key][skey]
        for skey in emissions[key].keys():
            if total == 0:
                continue
            emissions[key][skey] = emissions[key][skey] / total


def normalize_pred_scores():
    for key in emissions.keys():
        for skey in emissions[key].keys():
            emissions[key][skey] = math.pow(emissions[key][skey], 3)


def load_transitions(list, size):
    end = size + 1
    for line in list:
        tokens = line.split()
        prob = float(tokens[0])
        ngram = '_'.join(tokens[1: end])
        transitions[ngram] = math.exp(prob)


def load_model(lm_file, dtlm_file, seq_file, nmt_file):
    dtlmFile = open(dtlm_file, 'r', encoding='utf8')
    for line in dtlmFile:
        if len(line.strip()) == 0:
            continue
        tokens = line.split('\t')
        src = tokens[0].replace('|', '')
        trg = tokens[4]
        score = float(tokens[3])

        if src not in emissions:
            emissions[src] = {}
        if trg in emissions[src]:
            continue
        count = len(emissions[src].keys())
        weight = 1.0
        emissions[src][trg] = weight * score
    normalize_emission()
    sqtr_preds = open(seq_file, 'r', encoding='utf8')
    for line in sqtr_preds:
        if len(line.strip()) == 0:
            continue
        tokens = line.split('\t')
        if len(tokens) < 4:
            continue
        src = tokens[0].replace(' ', '')
        trg = tokens[3].replace(' ', '').replace('\n', '')
        score = float(tokens[2])
        # print(src, trg, score)
        if src not in emissions:
            emissions[src] = {}
        if trg in emissions[src]:
            emissions[src][trg] = max(score, emissions[src][trg])
        count = len(emissions[src].keys())
        weight = 1.0
        emissions[src][trg] = weight * score
    normalize_emission()
    nmt_preds = open(nmt_file, 'r', encoding='utf8').readlines()
    nmt_emissions = {}
    for line in nmt_preds:
        if len(line.strip()) == 0:
            continue
        tokens = line.split('\t')
        src = tokens[0].strip()
        trg = tokens[1].strip()
        score = float(tokens[2])
        score = math.exp(score)

        if src not in nmt_emissions:
            nmt_emissions[src] = {}
        if trg in nmt_emissions[src]:
            nmt_emissions[src][trg] = max(score, nmt_emissions[src][trg])
            continue
        # count = len(emissions[src].keys())
        weight = 1.0
        nmt_emissions[src][trg] = weight * score

    for key in nmt_emissions.keys():
        total = 0.
        for skey in nmt_emissions[key].keys():
            total += nmt_emissions[key][skey]
        for skey in nmt_emissions[key].keys():
            nmt_emissions[key][skey] = nmt_emissions[key][skey] / total
            if key not in emissions:
                emissions[key] = {}
            if skey in emissions[key]:
                emissions[key][skey] = max(nmt_emissions[key][skey], emissions[key][skey])
            else:
                emissions[key][skey] = nmt_emissions[key][skey]
    normalize_emission()
    normalize_pred_scores()
    lines = open(lm_file, 'r', encoding='utf8').readlines()
    start = 0
    end = 0
    total_trigrams = 0
    total_bigrams = 0
    total_unigrams = 0
    for line in lines:
        if re.search('ngram 1=', line):
            total_unigrams = int(line.split('=')[1])
        if re.search('ngram 2=', line):
            total_bigrams = int(line.split('=')[1])
        if re.search('ngram 3=', line):
            total_trigrams = int(line.split('=')[1])
            break
    trigram_start = 0
    bigram_start = 0
    unigram_start = 0
    for i in range(len(lines)):
        if lines[i].strip() == "\\1-grams:":
            unigram_start = i + 1
        if lines[i].strip() == "\\2-grams:":
            bigram_start = i + 1
        if lines[i].strip() == "\\3-grams:":
            trigram_start = i + 1
    load_transitions(lines[unigram_start: total_unigrams], 1)
    load_transitions(lines[bigram_start: total_bigrams], 2)
    load_transitions(lines[trigram_start:total_trigrams], 3)


def getTranisitionScore(w1, w2, w3):
    tri_prob = transitions['_'.join([w1, w2, w3])] if '_'.join([w1, w2, w3]) in transitions else 0.
    bi_prob = transitions['_'.join([w2, w3])] if '_'.join([w2, w3]) in transitions else 0.
    uni_prob = transitions[w3] if w3 in transitions else 0.
    score = r3 * tri_prob + r2 * bi_prob + r1 * uni_prob
    return 0. if score == 0. else math.pow(score, .15)

def constructString(idx, name):
    return str(idx) + ' ' + name


def calculate_score(sent):
    words = ['<s>', '<s>'] + sent.split() + ['</s>', '</s>']
    best_edge[constructString(0, '<s>')] = None
    best_score['1 <unk>'] = 0
    n = 3
    temp = {}

    temp['<unk>'] = 0
    emissions['<s>'] = temp
    emissions['</s>'] = temp
    score = 0.
    for i in range(1, len(words) - 2):
        key1 = words[i - 1] if words[i - 1] in emissions else '<s>'
        for w1 in emissions[key1].keys():
            key2 = words[i] if words[i] in emissions else '<s>'
            for w2 in emissions[key2].keys():
                key3 = words[i + 1] if words[i + 1] in emissions else '<s>'
                if key3 in dictionary:
                    emissions[key3][dictionary[key3]] = 0
                for w3 in emissions[key3].keys():
                    if constructString(i, w2) in best_score:
                        score = best_score[constructString(i, w2)] + getTranisitionScore(w1, w2, w3) + \
                                emissions[key3][w3]
                        if (constructString(i + 1, w3) in best_score and best_score[
                            constructString(i + 1, w3)] < score) or (constructString(i + 1, w3) not in best_score):
                            best_score[constructString(i + 1, w3)] = score
                            best_edge[constructString(i + 1, w3)] = constructString(i, w2)
    i = len(words) - 2
    key1 = words[i - 1] if words[i - 1] in emissions else '<s>'
    for w1 in emissions[key1].keys():
        key2 = words[i] if words[i] in emissions else '<s>'
        for w2 in emissions[key2].keys():
            key3 = words[i + 1] if words[i + 1] in emissions else '<s>'
            for w3 in emissions[key3].keys():
                if constructString(i, w2) in best_score:
                    score = best_score[constructString(i, w2)] + getTranisitionScore(w1, w2, w3) + \
                            emissions[key3][w3]
                    # print(score)
                    if (constructString(i + 1, w3) in best_score and best_score[
                        constructString(i + 1, w3)] < score) or (constructString(i + 1, w3) not in best_score):
                        best_score[constructString(i + 1, w3)] = score
                        best_edge[constructString(i + 1, w3)] = constructString(i, w2)


def backtrack(sent):
    words = []
    next_edge = best_edge[constructString(len(sent.split()) + 2, '<unk>')]
    while next_edge != '1 <unk>':
        token = next_edge.split()[1] if len(next_edge.split()) == 2 else '<unk>'
        words.append(token)
        next_edge = best_edge[next_edge]
    words.reverse()
    return ' '.join(words)


def clean_sentence(sent):
    chars = '.?!,/:;-+=)(}{][|*&^%$#@'
    for char in chars:
        sent = sent.replace(char, ' ' + char + ' ')
    uncleaned = nltk.sent_tokenize(sent.lower())
    cleaned = []
    for line in uncleaned:
        for char in chars:
            line = line.replace(char, ' ')
        if len(line.strip()) > 0:
            cleaned.append(line)
    return cleaned


def load_lids(fname):
    lines = open(fname, 'r').readlines()
    out = []
    for line in lines:
        if len(line.strip()) == 0:
            if len(out) > 0:
                lang_ids.append(out)
            out = []
        tokens = line.split()
        if len(tokens) < 3:
            continue
        src = tokens[0]
        lang = tokens[2]
        out.append((src, lang))
    lang_ids.append(out)


def neural_lid(x):
    return [token[1] for token in lang_ids[x]]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-d', '--dtlm', help='dtlm predictions', required=True)
    requiredNamed.add_argument('-s', '--seq', help='sequitur predictions', required=True)
    requiredNamed.add_argument('-n', '--nmt', help='nmt predictions', required=True)
    requiredNamed.add_argument('-w', '--lm', help='word-level language model', required=True)
    requiredNamed.add_argument('-l', '--lid', help='language labels', required=True)
    requiredNamed.add_argument('-t', '--test', help='test file name', required=True)
    parser.add_argument('-o', '--output', help='output file name')
    args = parser.parse_args()
    print(args)
    load_model(args.lm, args.dtlm, args.seq, args.nmt)
    load_lids(args.lid)
    test = open(args.test, 'r')
    outFile = None
    if args.output is not None:
        outFile = open(args.output, 'w')
    sents = []
    for line in test:
        sents += clean_sentence(line)
    for x, sent in enumerate(sents):
        best_edge = {}
        best_score = {}
        calculate_score(sent)
        output = backtrack(sent)
        oTokens = output.split()
        senTokens = sent.split()
        
        lids = neural_lid(x)
        if len(lids) != len(senTokens):
            print('Error!:', output, '<-->', sent)
            exit()
        for i in range(len(oTokens)):
            if lids[i] == 'E' or oTokens == '<unk>':
                oTokens[i] = senTokens[i]

        if outFile is None:
            print(' '.join(oTokens))
        else:
            outFile.write(' '.join(oTokens) + '\n')
