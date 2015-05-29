#!/usr/bin/python
# -*- coding: UTF-8 -*-

import nltk
import copy
import pycrfsuite

def load_corpus(fpath):
    sents = []
    with open(fpath) as fd:
        for l in fd:
            sent = []
            for w in l.split(" "):
                if not w:
                    continue
                else:
                    token_tag = w.split("/")
                    if len(token_tag) == 2:
                        token_tag = [tmp if isinstance(tmp, unicode) else tmp.decode("utf8") for tmp in token_tag]
                        token_tag.append(token_tag[-1])
                        sent.append(token_tag)
            sents.append(sent)
    return sents

def cut_word(word, tag):
    if isinstance(word, str):
        word = word.decode("utf8")
    wl = list(word)
    llen = len(wl)
    if llen == 0:
        return []
    elif llen == 1:
        wl[0] = [wl[0], "S", tag]
        return wl
    else:
        ret_list = []
        for idx, w in enumerate(wl):
            if idx == 0:
                ret_list.append([w, "B", tag])
            elif idx == llen - 1:
                ret_list.append([w, "E", tag])
            else:
                ret_list.append([w, "M", tag])
        return ret_list

def trans_to_bmes(src, dest):
    sents = load_corpus(src)
    with open(dest, "w") as fd:
        wl = []
        for sent in sents:
            for word in sent:
                wl.extend(cut_word(word[0], word[1]))
    print len(wl)
    print wl[0]

def save_to_file(sents, fpath):
    with open(fpath, "w") as fd:
        for sent in sents:
            lines = [(w[0] + " " + w[1] + "\n").encode("utf8") for w in sent]
            fd.writelines(lines)

def word2features(sent, i):
    word = sent[i][0]
    postag = sent[i][1]
    features = [
        'bias',
        'word.lower=' + word.lower(),
        #'word[-3:]=' + word[-3:],
        #'word[-2:]=' + word[-2:],
        #'word.isupper=%s' % word.isupper(),
        #'word.istitle=%s' % word.istitle(),
        #'word.isdigit=%s' % word.isdigit(),
        #'postag=' + postag,
        #'postag[:2]=' + postag[:2],
    ]
    if i > 0:
        pass
        #word1 = sent[i-1][0]
        #postag1 = sent[i-1][1]
        #features.extend([
        #    '-1:word.lower=' + word1.lower(),
        #    '-1:word.istitle=%s' % word1.istitle(),
        #    '-1:word.isupper=%s' % word1.isupper(),
        #    '-1:postag=' + postag1,
        #    '-1:postag[:2]=' + postag1[:2],
        #])
    else:
        features.append('BOS')
        
    if i < len(sent)-1:
        pass
        #word1 = sent[i+1][0]
        #postag1 = sent[i+1][1]
        #features.extend([
        #    '+1:word.lower=' + word1.lower(),
        #    '+1:word.istitle=%s' % word1.istitle(),
        #    '+1:word.isupper=%s' % word1.isupper(),
        #    '+1:postag=' + postag1,
        #    '+1:postag[:2]=' + postag1[:2],
        #])
    else:
        features.append('EOS')
                
    return features

def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]

def sent2labels(sent):
    return [label for token, postag, label in sent]

def sent2tokens(sent):
    return [token for token, postag, label in sent]    

if 0:
    fpath = "/home/kelly/backup/199801.txt.utf-8"
    dest_fpath = "/home/kelly/tempfile"
    trans_to_bmes(fpath, dest_fpath)
    exit()

if 0:
    #format corpus
    fpath = "/home/kelly/backup/199801.txt.utf-8"
    dest_fpath = "/home/kelly/code/codebackup/codebackup/"
    sents = load_corpus(fpath)
    print sents[0]
    save_to_file(sents, "/home/kelly/tempfile")
    exit()

if 0:
    test_sents = list(nltk.corpus.conll2002.iob_sents('esp.testb'))
    #example_sent = test_sents[0]
    example_sent = []
    #example_sent[0] = (u'La', u'DA', u'LC')
    example_sent.append((u'我', u'', u'v'))
    example_sent.append((u'希望', u'', u'v'))
    example_sent.append((u'经过', u'', u'v'))
    example_sent.append((u'江泽民', u'', u'v'))
    print example_sent
    tagger = pycrfsuite.Tagger()
    tagger.open("/home/kelly/temp/1998.crfsuite")
    tagfea = sent2features(example_sent)
    print "tagfea:", tagfea
    print tagger.tag(tagfea)
    #print "$".join(tagger.tag(sent2features(example_sent)))
    exit()
    pass

fpath = "/home/kelly/backup/199801.txt.utf-8"
#train_sents = list(nltk.corpus.conll2002.iob_sents('esp.train'))
train_sents = load_corpus(fpath)
test_sents = list(nltk.corpus.conll2002.iob_sents('esp.testb'))

train_sents = train_sents[:3000]

x_train = [sent2features(s) for s in train_sents]
y_train = [sent2labels(s) for s in train_sents]

trainer = pycrfsuite.Trainer(verbose=False)
for xseq, yseq in zip(x_train, y_train):
    trainer.append(xseq, yseq)
trainer.set_params({
    'c1': 1.0,
    'c2': 1e-3,
    'max_iterations': 50,
    'feature.possible_transitions': True
    })

trainer.train("/home/kelly/temp/1998.crfsuite")
