#!/usr/bin/python
# -*- coding: UTF-8 -*-

import nltk
import copy
import pycrfsuite

def load_rmrb_corpus(fpath):
    sents = []
    with open(fpath) as fd:
        sent = []
        for l in fd:
            #lt = l.strip().decode("utf8")
            lt = l.strip()
            if not lt:
                sents.append(sent)
                sent = []
            else:
                w_t = lt.split(" ")
                sent.append([w_t[0], w_t[1], w_t[1]])
    return sents

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
        'word.isdigit=%s' % word.isdigit(),
        'postag=' + postag,
        #'postag[:2]=' + postag[:2],
    ]
    if i > 0:
        pass
        word1 = sent[i-1][0]
        postag1 = sent[i-1][1]
        features.extend([
            '-1:word.lower=' + word1.lower(),
            #'-1:word.istitle=%s' % word1.istitle(),
            #'-1:word.isupper=%s' % word1.isupper(),
            '-1:postag=' + postag1,
            #'-1:postag[:2]=' + postag1[:2],
        ])
    else:
        features.append('BOS')
        
    if i < len(sent)-1:
        pass
        word1 = sent[i+1][0]
        postag1 = sent[i+1][1]
        features.extend([
            '+1:word.lower=' + word1.lower(),
            #'+1:word.istitle=%s' % word1.istitle(),
            #'+1:word.isupper=%s' % word1.isupper(),
            '+1:postag=' + postag1,
            #'+1:postag[:2]=' + postag1[:2],
        ])
    else:
        features.append('EOS')
                
    return features

def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]

def sent2labels(sent):
    return [label for token, postag, label in sent]

def sent2tokens(sent):
    return [token for token, postag, label in sent]    

def sent2postag(sent):
    return [postag for token, postag in sent]    

if 0:
    import nltk
    sent='消息/n 源/g 新浪/nz 财经/n 称/v ，/w 针对/p 今日/t 有/v 媒体/n 平台/n 报道/v 央行/n 已经/d 发文/v 暂停/v 比特/q 币/g 交易/n 的/u 消息/n ，/w 接近/v 监管/vn 层/qv 人士/n 对/p 新浪/nz 财经/n 表示/v ，/w 央行/n 确实/ad 下发/v 文件/n ，/w 但/c 并非/v 叫/v 停/v 比特/q 币/g ，/w 而是/c 加强/v 比特/q 币/g 的/u 监管/vn 。/w ';
    sTuple=[nltk.tag.str2tuple(t) for t in sent.split()]  #根据文本中的空格进行切分，切分后每一项再转为tuple元组，结构为: ('消息', 'N')
    print sTuple
    for s in sTuple:
        print s[0], s[1]
    exit()
    wordsCount=len(sTuple)  #统计词个数
    print('总词数：',wordsCount) 
    plt=nltk.FreqDist(sTuple) #获取统计结果，结果的结构为：<FreqDist: ('，', 'W'): 5, ('币', 'G'): 3,....>  每一项后面的数字是该字与其词性组合的出现次数，除了第一项的FreqDist外，后面的结构正好符合字典类型
    print('各词性标注统计结果：')
    d=dict(plt)  #把统计结果转为字典型，它会删掉不符合字典结构的第一项FreqDist，把后面的结果转存为字典型
    for key in d.keys():  #遍历字典，每一类词性的总次数一目了然
        print(key,d[key])
    exit()
    pass

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

if 1:
    #test_sents = list(nltk.corpus.conll2002.iob_sents('esp.testb'))
    #example_sent = test_sents[0]
    example_sent = []
    #example_sent[0] = (u'La', u'DA', u'LC')
    example_sent.append((u'我', u'', u'v'))
    example_sent.append((u'希', u'', u'v'))
    example_sent.append((u'望', u'', u'v'))
    example_sent.append((u'江', u'', u'v'))
    example_sent.append((u'泽', u'', u'v'))
    example_sent.append((u'民', u'', u'v'))
    print example_sent
    tagger = pycrfsuite.Tagger()
    tagger.open("1998.crfsuite")
    tagger.dump("crfsuite.txt")
    exit()
    tagfea = sent2features(example_sent)
    print "tagfea:", tagfea
    print tagger.tag(tagfea)
    #print "$".join(tagger.tag(sent2features(example_sent)))
    exit()
    pass

#fpath = "199801.txt.utf-8"
#fpath = "/home/kelly/temp/train.all.txt.utf8"
fpath = "train.all.txt.utf8"
#train_sents = list(nltk.corpus.conll2002.iob_sents('esp.train'))
#train_sents = load_corpus(fpath)
train_sents = load_rmrb_corpus(fpath)
test_sents = list(nltk.corpus.conll2002.iob_sents('esp.testb'))

train_sents = train_sents[:3000]

x_train = [sent2features(s) for s in train_sents]
y_train = [sent2labels(s) for s in train_sents]
#y_train = [sent2postag(s) for s in train_sents]
#print len(x_train)
#exit()

print "start append train set."
trainer = pycrfsuite.Trainer(verbose=False)
for xseq, yseq in zip(x_train, y_train):
    trainer.append(xseq, yseq)
print "append train set done."
trainer.set_params({
    'c1': 1.0,
    'c2': 1e-3,
    'max_iterations': 500,
    'feature.possible_transitions': True
    })

trainer.train("1998.crfsuite")
