#!/usr/bin/python3
from sys import argv, stderr
from sgraph import SentenceGraph
from pycorenlp import StanfordCoreNLP
from patterns import patterns

filename = argv[1]
n = int(argv[2])

client = StanfordCoreNLP('http://localhost:9000')

questions = {}
# is first sentence in paragraph, for higher ranking
newsection = True

with open(filename) as f:
    line = f.readline()
    while line:
        if (line.strip() == ''):
            newsection = True
        # sections are separated with empty lines
        if len(line) < 60:
            line = f.readline()
            continue
        corenlp_out = eval(client.annotate(line, properties={
                'annotators': 'depparse, pos, lemma, ner',
            }))
        for i, sent in enumerate(corenlp_out['sentences']):
            sg = SentenceGraph(sent)
            for i, (pat, tmpl) in enumerate(patterns):
                res = sg.match(pat)
                if res is not None:
                    q, _ = tmpl(sg, res)
                    if q:
                        if newsection:
                            questions[q] = 3
                        elif i == 0:
                            questions[q] = 2
                        else:
                            questions[q] = 1
            newsection = False
        line = f.readline()

qlist = sorted(questions.items(), key=lambda item: item[1]/len(item[0].split())**2, reverse=True)
for i in range(min(n, len(qlist))):
    print('[{}]- '.format(i+1), qlist[i][0], qlist[i][1])

if n > len(qlist):  
    stderr.write('\033[01;31m'+'Only {} questions were generated\n'.format(len(qlist)))