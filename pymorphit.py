# coding: utf-8

# by G. De Gasperis and I. Grappasonno, UnivAQ http://www.univaq.it
import time

import re
import codecs
import json
import os

from string import punctuation

UNKOWN = u'?'


def catChoice():
    global catS
    catL = list(catS)
    ci = 1
    for i, c in enumerate(catL):
        print(i+1, c)
        ci += 1
        ci += 1
    a = int(input('Quale? :'))
    if (a > 0) and (a <= len(catL)):
        return catL[a]
    else:
        return 'J:j'


def addCatTree(catK, catV):
    global catTree
    if not catK in catTree.keys():
        catTree[catK] = set([])
    catTree[catK] = catTree[catK].union(catTree[catK], set(catV))
    pass


def makeTupleList(lx):
    out = []
    for e in lx:
        if type(e) == type((0, 0)):
            out.append(e)
        elif type(e) == type([]):
            out += makeTupleList(e)
        else:
            print('?????')
    return out


def tokenize(line):
    scanner = re.Scanner([
        (r"[0-9]+", lambda scanner, token: ("DET-NUM", token)),
        (r"[A-Z]*[a-z]+[àèéìòù]*", lambda scanner, token: ("LESSEMA", token)),
        (r"[!.?]+", lambda scanner, token: ("PUNT_FIN", token)),
        (r"[,;:]+", lambda scanner, token: ("PUNT", token)),
        (r"\s+", None),  # None == skip token.
    ])
    out0 = scanner.scan(line)
    return makeTupleList(out0)


def RomanTranslate(s):
    string = s.upper()
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "M": 1000}
    try:
        return sum(map(lambda x: values[x], string))
    except:
        return ''


def isNumber(token):
    out = False
    if len(token) > 0:
        try:
            f = float(token)
            out = True
        except ValueError:
            if isNumber(str(RomanTranslate(token))):
                out = True
            pass
    return out

'''
I am not sure what this part does.
However, it works perfectly fine without. So I commented it out.

def log(s):
    if type(s) in [type(u''), type('')]:
        return s.encode('utf-8')
    else:
        out = ''
        for z in s:
            out += '\t' + log(str(z).encode('utf-8'))
        return out
'''

def learnLemma(lemmaPrec, lessema, succ):
    global dMorphit, dRules
    ltupla = str((lemmaPrec[1], lessema, succ[1]))
    if ltupla in dRules.keys():
        c = dRules[ltupla]
        print ('regola:', ltupla, c)
        return c
    else:
        print('NUOVA REGOLA!')
        print ('Contesto: [..', lemmaPrec[0], lessema, succ[0],'..]')
        print ('\t\t', '<'+lemmaPrec[1]+'>', lessema, '<'+succ[1]+'>')
        print(0, 'Save and Exit')
        lemmi = dMorphit[lessema]
        for m in range(1, len(lemmi) + 1):
            print (m, lemmi[m-1])
            pass
        print(-1, 'Categoria generica')
        a = int(input('Quale? :'))
        if a > 0:
            out = (lemmi[a - 1][0], lemmi[a - 1][1])
            dRules[ltupla] = out
            return out
        else:
            if a == -1:
                return (lessema, UNKOWN)
            return ''


def makeLemma(lemmaPrec, lessema, succ):
    out = learnLemma(lemmaPrec, lessema, succ)
    if out == '':
        open(DRULES_FILE, 'w').write(json.dumps(dRules))
        exit(0)
    return out


def hasLemma(lessema):

    global dMorphit
    return lessema in dMorphit.keys()


def getLemma(lemmaPrec, lessema, succ):

    out = u''
    lemmi = dMorphit[lessema]
    out = lemmi[0]
    if len(lemmi) > 1:
        # ambiguità
        if lemmaPrec != UNKOWN:
            succLemma = lemmatize(UNKOWN, succ, UNKOWN)
            out = makeLemma(lemmaPrec, lessema, succLemma)  # usa regole ed euristiche per determinare il lemma
        else:
            out = (lemmi[0][0], UNKOWN)
    return out


def lemmatize(lemmaPrec, lessema, succ):
    out = u''
    if type(lessema) == tuple:
        lessema = lessema[1]

    # print (log(lessema), '...',)
    if len(lessema) > 0:
        if hasLemma(lessema):
            out = getLemma(lemmaPrec, lessema, succ)
        elif hasLemma(lessema.lower()):
            out = getLemma(lemmaPrec, lessema.lower(), succ)
        elif hasLemma(lessema.capitalize()):
            out = getLemma(lemmaPrec, lessema.capitalize(), succ)
        elif isNumber(lessema):
            out = (u'X', u'DET-NUM')
        else:
            out = (lessema, UNKOWN)
    if lemmaPrec != UNKOWN:
        pass
        # print ('\t-->\t', log(out))
    return out


# ------------ MAIN -----------------
if __name__ == '__main__':
    tl = tokenize(u'Il turista che andò al mare, e mai più ci Tornerà.')
    print(tl)
    pass
    myPuntuaction = punctuation
    myPuntuaction = myPuntuaction.replace('-', '')
    r = re.compile(r'[\s{}]+'.format(re.escape(myPuntuaction)))

    dMorphit = {}
    dRules = {}
    catTree = {}

    DRULES_FILE = 'drules.json'
    if os.path.isfile(DRULES_FILE):
        dRules = json.loads(open(DRULES_FILE, 'r').read())

    # DMORPHIT_FILE = 'dmorphit.json'
    # if os.path.isfile(DMORPHIT_FILE):
    #     dMorphit = json.loads(open(DMORPHIT_FILE,'r').read())
    # else:
    fm = codecs.open('morph-it_048_utf8.txt', 'r', encoding='utf-8')

    for line in fm:
        lst = re.split(' |\t', line.strip())
        cat = lst[2]

        if cat.find('-') > 0:
            catL2 = cat.split('-')
            addCatTree(catL2[0], catL2[1:])
        elif cat.find(':') > 0:
            [catL1l, catL1r] = cat.split(':')
            if catL1l.find('-') > 0:
                [catL2l, catL2r] = catL1l.split('-')
                addCatTree(catL2l, catL2r)
            else:
                addCatTree(catL1l, '')
        else:
            addCatTree(cat, '')
        try:
            if lst[0] in dMorphit.keys():
                dMorphit[lst[0]] += [(lst[1], lst[2])]
            else:
                dMorphit[lst[0]] = [(lst[1], lst[2])]
        except:
            pass
    # open(DMORPHIT_FILE,'w').write(json.dumps(dMorphit))

    print('initiation done...', flush=True)
    time.sleep(5)

    with codecs.open('collodi_pinocchio_utf8.txt', 'r', 'utf-8') as fc:
        lemmaPrec = u'[]'
        lemmabile = lemmaPrec
        succ = u''

        for line in fc:

            tl = tokenize(line.strip())

            widx = 0

            for widx2, t in enumerate(tl):

                if t[0] == 'LESSEMA':
                    succ = '[]'
                    if widx < len(tl) - 1:
                        succ = tl[widx2 + 1]

                    if len(lemmabile) > 0:
                        lemmaPrec = lemmabile


                    print('-------------------')
                    print(tl)

                    print('lemma:', lemmabile)

                    print('lemmaprec:', lemmaPrec)
                    print('t1:', t[1])
                    print('succ:', succ)


                    lemmabile = lemmatize(lemmaPrec, t[1], succ)
                    widx += 1



                    print('-------------------')
