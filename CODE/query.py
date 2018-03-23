import shelve
import math
from math import log10, sqrt
import ingest
from ingest import *
# from itertools import islice
import re


## INPUT
##-------------------------------------------------------------------------##
## index = [
##       { Term1: [tf1, tf2, ..., tfn] },
##       { Term2: [tf1, tf2, ..., tfn] },
##       ...,
##       { Termm: [tf1, tf2, ..., tfn] }
## ]
## doc_key = [
##      { DocName1: [DocID1, DocLocation1] },
##      { DocName2: [DocID2, DocLocation2] },
##      ...,
##      { DocNamen: [DocIDn, DocLocationn] }
## ]
## docVector = [
##      [WT1,D1, WT1,D2, ..., WT1,Dn],
##      [WT2,D1, WT2,D2, ..., WT2,Dn],
##      ...,
##      [WTm,D1, WTm,D2, ..., WTm,Dn]
## ]
## proxVector = [
##      [ [P1T1,D1, P2T1,D1, ..., PiT1D1],
##        [P1T1,D2, P2T1,D2, ..., PiT1D2],
##        ...,
##        [P1T1,Dn, P2T1,Dn, ..., PiT1Dn] ],
##      [ [P1T2,D1, P2T2,D1, ..., PiT2D1],
##        [P1T2,D2, P2T2,D2, ..., PiT2D2],
##        ...,
##        [P1T2,Dn, P2T2,Dn, ..., PiT2Dn] ],
##      ...,
##      [ [P1Tm,D1, P2Tm,D1, ..., PiTmD1],
##        [P1Tm,D2, P2Tm,D2, ..., PiTmD2],
##        ...,
##        [P1Tm,Dn, P2Tm,Dn, ..., PiTmDn] ]
## ]
## termIndex = {
##      Term1: i1,
##      Term2: i2,
##      ...,
##      Termm: im
## }

## OUTPUT
##-------------------------------------------------------------------------##
## results = [
##      [ DocName1, DocLocation1, Rank1, Summary1],
##      [ DocName2, DocLocation2, Rank2, Summary2],
##      …,
##      [ DocNamen, DocLocationn, Rankn, Summaryn]
##  ]

class similarity:

    def __init__(self, infile, infile1):
        proc = shelve.open(infile)
        self.docVector = proc['docVector']
        self.doc_key = proc['doc_key']
        self.proxVector = proc['proxVector']
        self.termIndex = proc['termIndex']
        proc.close()
        ingest = shelve.open(infile1)
        self.index = ingest['index']
        ingest.close
        self.result = []
        self.weightedQuery = []

    def tokenizeQuery(self, query):
        return func_tokenize(query)

    def findWholeWord(self, w):
        return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

    def normalizeQuery(self, query):
        for i in range(len(self.index)):
            for key, value in self.index[i].items():
                for val in range(len(value)):
                    if value[val] > 1:
                        value[val] = 1
                    self.index[i][key] = value
        self.index.sort(key=lambda k: list(k)[0])

        self.weightedQuery = [0] * len(self.index)

        for i in range(len(self.index)):
            word = list(self.index[i])[0]
            if self.findWholeWord(word)(query):
                df = len(list(filter(None, self.index[i][word])))
                idf = log10(len(self.index[i][word]) / float(df))
                idf = float("{0:.4f}".format(idf))
            else:
                idf = 0

            self.weightedQuery[i] = idf
        sumOfSquares = 0
        for i in range(len(self.weightedQuery)):
            sumOfSquares += self.weightedQuery[i] * self.weightedQuery[i]
        length = sqrt(sumOfSquares)
        queryVector = [float("{0:.4f}".format(self.weightedQuery[i] / length))
                       for i in range(len(self.weightedQuery))]
        return queryVector

    def vectorlength(self, vec):
        length = float(0)
        for num in vec:
            length += num * num
        return math.sqrt(length)

    def similarityDistance(self, w1, w2):
        sim = float(0)
        for wi1, wi2 in zip(w1, w2):
            sim += wi1 * wi2
        sim = sim / (self.vectorlength(w1) * self.vectorlength(w2))
        return sim

    def similarity(self, normalizedQuery):
        indexList = []
        docIndices = []

        similarityVector = []
        self.rankedOutput = []
        if not self.docVector:
            print(
                "did not match any documents.")
            return indexList

        if self.docVector:
            for i in range(len(self.docVector)):
                similarityVector.append(self.similarityDistance(normalizedQuery, self.docVector[i]))
            indexList = sorted(range(len(similarityVector)), key=lambda k: similarityVector[k])

        for i in indexList:
            docIndices.append(self.doc_key[i])

        docIndices.reverse()
        similarityVector.sort()
        similarityVector.reverse()
        self.rankedOutput.append(docIndices)
        self.rankedOutput.append(similarityVector)
        self.sliced = [self.rankedOutput[i][0:3] for i in range(0, 1)]
        # for item in self.sliced:
        # print("sliced output is")
        # print(item)
        return self.rankedOutput

    def proximity(self, tokenizedQuery):
        query = tokenizedQuery.split()

        for k in range(len(self.proxVector)):
            count = 0
            for i in range(len(query)):
                for j in range(i + 1, len(query)):
                    for term in self.termIndex:
                        if query[i].__eq__(term):
                            self.index1 = self.termIndex[term]
                            count = count + 1

                        if query[j].__eq__(term):
                            self.index2 = self.termIndex[term]
                    val1 = str(self.proxVector[k][self.index1]).replace("[", "").replace("]", "")
                    val2 = str(self.proxVector[k][self.index2]).replace("[", "").replace("]", "")
                    if val1 and val2:
                        if not val1.__contains__(",") and not val2.__contains__(","):
                            value = int(val1) - int(val2)
                            self.result.append(abs(value))
                    break
                for term in self.termIndex:
                    if query[i].__eq__(term):
                        count = count + 1
        return self.rankedOutput

    def writeOutput(self, outFile):
        out = shelve.open(outFile)
        out['rankedOutput'] = self.rankedOutput
        out.close()


def main():
    queryInstance = similarity('OUTPUT/processingOutput', 'OUTPUT/ingestOutput')
    #TODO: get the query from cgi
    tokenizedQuery = queryInstance.tokenizeQuery("truck arrived of")
    normalizedQuery = queryInstance.normalizeQuery(tokenizedQuery)
    queryInstance.similarity(normalizedQuery)
    queryInstance.proximity(tokenizedQuery)
    queryInstance.writeOutput('OUTPUT/queryOutput')


if __name__ == "__main__":
    main()
