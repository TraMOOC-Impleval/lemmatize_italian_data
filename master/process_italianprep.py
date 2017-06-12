import sys
import pymorphit_cls
import csv
import re

DEBUG = True


if __name__ == '__main__':
    filename = 'italian2.prep.tab'
    lemmatizer = pymorphit_cls.PyMorphITCLS()

    out = open('italian2.prep.withlemmatized.tab', 'wt')

    with open(filename, 'r') as f:
        reader = csv.reader(f, dialect='excel-tab')

        for i, line in enumerate(reader):
            italian_line = line[3]

            if i == 0:
                outheaderlist = line
                outheaderlist.insert(4, 'lemmatized')
                outheaderline = '\t'.join(outheaderlist).strip() + '\t'
                out.write(outheaderline)
            else:
                italian_line = re.sub(r'[\W]+', ' ', italian_line)
                lemmatized_line = lemmatizer.lemmatize_line(italian_line, mode='Q')

                outlist = line
                outlist.insert(4, lemmatized_line)
                outline = '\t'.join(outlist).strip() + '\n'
                out.write(outline)
                if DEBUG:
                    print(italian_line)
                    print('')
                    print(lemmatized_line)
                    print('---')
        out.close()
        print('Done')