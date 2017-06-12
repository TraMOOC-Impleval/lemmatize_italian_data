# coding: utf-8

# by G. De Gasperis and I. Grappasonno, UnivAQ http://www.univaq.it
# adapted by: H. de Vos

#package for debug
import time

#Packages for technical support
import re
import codecs
import json
import os
import sys

#Packages for linguistic support
from string import punctuation



class PyMorphITCLS(object):
    def __init__(self):
        self.UNKOWN = u'?'
        self.DOUBT = u'!'
        self.DRULES_FILE = 'drules.json'
        self.DEBUG = False

        print('initialize models...', flush=True)
        self.initialize_models()
        print('initializing done...', flush=True)

    # Initialisation funcs --------------------------------------

    def catChoice(self):
        global catS
        catL = list(catS)
        ci = 1
        for i, c in enumerate(catL):
            print(i + 1, c)
            ci += 1
            ci += 1
        a = int(input('Quale? :'))
        if (a > 0) and (a <= len(catL)):
            return catL[a]
        else:
            return 'J:j'

    def addCatTree(self, catK, catV):
        # global catTree
        if not catK in self.catTree.keys():
            self.catTree[catK] = set([])
        self.catTree[catK] = self.catTree[catK].union(self.catTree[catK], set(catV))
        pass

    def makeTupleList(self, lx):
        out = []
        for e in lx:
            if type(e) == type((0, 0)):
                # print(e)
                out.append(e)
            elif type(e) == type([]):
                out += self.makeTupleList(e)
            else:
                if self.DEBUG:
                    print('?????')
        return out

    def initialize_models(self):
        myPuntuaction = punctuation
        myPuntuaction = myPuntuaction.replace('-', '')
        r = re.compile(r'[\s{}]+'.format(re.escape(myPuntuaction)))

        self.dMorphit = {}
        self.dRules = {}
        self.catTree = {}

        DRULES_FILE = 'drules.json'
        if os.path.isfile(DRULES_FILE):
            dRules = json.loads(open(DRULES_FILE, 'r').read())

        fm = codecs.open('morph-it_048_utf8.txt', 'r', encoding='utf-8')

        for line in fm:
            lst = re.split(' |\t', line.strip())
            cat = lst[2]

            if cat.find('-') > 0:
                catL2 = cat.split('-')
                self.addCatTree(catL2[0], catL2[1:])
            elif cat.find(':') > 0:
                [catL1l, catL1r] = cat.split(':')
                if catL1l.find('-') > 0:
                    [catL2l, catL2r] = catL1l.split('-')
                    self.addCatTree(catL2l, catL2r)
                else:
                    self.addCatTree(catL1l, '')
            else:
                self.addCatTree(cat, '')
            try:
                if lst[0] in self.dMorphit.keys():
                    self.dMorphit[lst[0]] += [(lst[1], lst[2])]
                else:
                    self.dMorphit[lst[0]] = [(lst[1], lst[2])]
            except:
                pass

    # Tokenization funcs --------------------------------------------------------

    def tokenize(self, line):
        scanner = re.Scanner([
            (r"[0-9]+", lambda scanner, token: ("DET-NUM", token)),
            (r"[A-Z]*[a-z]+[àèéìòù]*", lambda scanner, token: ("LESSEMA", token)),
            (r"[!.?]+", lambda scanner, token: ("PUNT_FIN", token)),
            (r"[,;:]+", lambda scanner, token: ("PUNT", token)),
            (r"\s+", None),  # None == skip token.
        ])
        out0 = scanner.scan(line)

        return self.makeTupleList(out0)

    # Lemmatization funcs --------------------------------------------------------

    def RomanTranslate(self, s):
        '''

        :param s: <str> Roman Number
        :return: <int> Decimal equivalent of the roman number
        '''
        string = s.upper()
        values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "M": 1000}
        try:
            return sum(map(lambda x: values[x], string))
        except:
            return ''

    def isNumber(self, token):
        out = False
        if len(token) > 0:
            try:
                f = float(token)
                out = True
            except ValueError:
                if self.isNumber(str(self.RomanTranslate(token))):
                    out = True
                pass
        return out

    def learnLemma(self, lemmaPrec, lessema, succ):
        # global dMorphit, dRules
        ltupla = str((lemmaPrec[1], lessema, succ[1]))
        if ltupla in self.dRules.keys():
            c = self.dRules[ltupla]
            print('regola:', ltupla, c)
            return c

        else:
            print('NUOVA REGOLA!')
            print('Contesto: [..', lemmaPrec[0], lessema, succ[0], '..]')
            print('\t\t', '<' + lemmaPrec[1] + '>', lessema, '<' + succ[1] + '>')
            print(0, 'Save and Exit')
            lemmi = self.dMorphit[lessema]
            for m in range(1, len(lemmi) + 1):
                print(m, lemmi[m - 1])
                pass
            print(-1, 'Categoria generica')
            a = int(input('Quale? :'))

            if a > 0:
                out = (lemmi[a - 1][0], lemmi[a - 1][1])
                self.dRules[ltupla] = out
                return out
            else:
                if a == -1:
                    return (lessema, self.UNKOWN)
                return ''

    def makeLemma(self, lemmaPrec, lessema, succ, dMorphit, dRules):
        out = self.learnLemma(lemmaPrec, lessema, succ)
        if out == '':
            open(self.DRULES_FILE, 'w').write(json.dumps(dRules))
            exit(0)
        return out

    def hasLemma(self, lessema):

        # global dMorphit
        return lessema in self.dMorphit.keys()

    def getLemma(self, lemmaPrec, lessema, succ, mode='G'):

        out = u''  # <-- redundant.
        lemmi = self.dMorphit[lessema]
        out = lemmi[0]
        if len(lemmi) > 1:

            if lemmaPrec != self.UNKOWN and mode == 'G':
                succLemma = self.lemmatize(self.UNKOWN, succ, self.UNKOWN)
                out = self.makeLemma(lemmaPrec, lessema, succLemma)  # usa regole ed euristiche per determinare il lemma
            elif lemmaPrec != self.UNKOWN and mode == 'Q':
                out = (lemmi[0][0], self.DOUBT)
            else:
                out = (lemmi[0][0], self.UNKOWN)

        return out

    def lemmatize(self, lemmaPrec, lessema, succ, mode='G'):
        '''
        Lemmatize the target word.
        :param lemmaPrec: <tuple> (lemma, POS-tag) lemmatized word preceding to target word
        :param lessema: <tuple> (type ('LESSEMA (lexeme) or PUNT (Punctuation)), target word)
        :param succ: <>unlemmatized word succeeding the target word.
        :return: <tuple> (lemma, POS-tag)
        '''

        out = u''
        if type(lessema) == tuple:
            lessema = lessema[1]

        if self.DEBUG:
            print(lessema, '...', )

        if len(lessema) > 0:
            if self.hasLemma(lessema):
                out = self.getLemma(lemmaPrec, lessema, succ, mode)
            elif self.hasLemma(lessema.lower()):
                out = self.getLemma(lemmaPrec, lessema.lower(), succ, mode)
            elif self.hasLemma(lessema.capitalize()):
                out = self.getLemma(lemmaPrec, lessema.capitalize(), succ, mode)
            elif self.isNumber(lessema):
                out = (u'X', u'DET-NUM')
            else:
                out = (lessema, self.UNKOWN)

        if lemmaPrec != self.UNKOWN and self.DEBUG:
            print('\t-->\t', out)

        return out

    def lemmatize_line(self, line, mode = 'G'):
        lemmaPrec = u'[]'
        lemmabile = lemmaPrec
        succ = u''

        lemmalist = []
        tl = self.tokenize(line.strip())
        for widx, t in enumerate(tl):
            if t[0] == 'LESSEMA':
                succ = '[]'
                if widx < len(tl) - 1:
                    succ = tl[widx + 1]

                if len(lemmabile) > 0:
                    lemmaPrec = lemmabile

                lemmabile = self.lemmatize(lemmaPrec, t[1], succ, mode)

                if self.DEBUG:
                    print('lemma: ', lemmabile[0])

                lemmalist.append(lemmabile[0])

        linestr = '{}\n'.format(' '.join(lemmalist))

        return linestr


    def lemmatize_file(self, filename='collodi_pinocchio_utf8.txt', mode='G'):

        outfile = ''.join(filename.split('.')[:-1]) + '.lemmatized.txt'

        out = open(outfile, 'wt')

        with codecs.open(filename, 'r', 'utf-8') as fc:
            lemmaPrec = u'[]'
            lemmabile = lemmaPrec
            succ = u''

            for line in fc:

                lemmatized_line = self.lemmatize_line(line, mode)

                out.write(lemmatized_line)

        out.close()
        print('Lemmatized file saved as {}'.format(outfile))

if __name__ == '__main__':
    lemmatizer = PyMorphITCLS()
    lemmatizer.lemmatize_file(mode='Q')