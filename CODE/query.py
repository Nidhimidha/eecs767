import shelve
import math
from math import log10, sqrt
import ingest
from ingest import *
import re
import time
from functools import wraps
from operator import itemgetter
import collections

#
# Python EECS 767 Query Processing
# Author: Nidhi Midha
# KU Student ID: 2924365
# Date started: 2/11/2018
# Date finished: xx/xx/xxxx
#


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
##      ...,
##      [ DocNamen, DocLocationn, Rankn, Summaryn]
##  ]

def timing(f):
    @wraps(f)
    def ft(*args, **kwargs):
        t0 = time.time()
        exe = f(*args, **kwargs)
        t1 = time.time()
        print("\t%s Execution Time (sec): %s" %
              (f.__name__, str(t1 - t0)))
        return exe

    return ft


class similarity:

    def __init__(self, infile1, infile2):
        proc1 = shelve.open(infile1)
        self.doc_key = proc1['doc_key']
        self.proxVector = proc1['proxDict']
        self.termIndex = proc1['termIDF']
        self.termDict = proc1['termDict']
        self.titles = proc1['title_map']
        proc1.close()
        proc2 = shelve.open(infile2)
        self.docVector = proc2['docVector']
        proc2.close()
        self.weightedQuery = []
        self.rankedOutput = []
        self.queryVector = []
        self.queryList = []
        self.termList = []
        self.proxRankedOutput = []

    def tokenizeQuery(self, query):
        return func_tokenize(query)

    def findWholeWord(self, word, query):
        for x in query:
            result = re.findall('\\b' + word + '\\b', x, flags=re.IGNORECASE)
            if len(result) > 0:
                return True

    # @timing
    def normalizeQuery(self, query):

        self.weightedQuery = [0] * len(self.termIndex)
        flag = False
        for k in self.termIndex:
            if self.findWholeWord(k, query):
                idf = self.termIndex[k][0]
                flag = True
                for l in range(len(self.termDict[k])):
                    self.termList.append(k)
                    self.queryList.append(self.termDict[k][l][0])
            else:
                idf = 0

            self.weightedQuery[self.termIndex[k][1]] = idf
        self.queryList = list(set(self.queryList))
        self.termList = list(set(self.termList))

        if flag:
            sumOfSquares = 0
            for i in range(len(self.weightedQuery)):
                sumOfSquares += self.weightedQuery[i] * self.weightedQuery[i]
            length = sqrt(sumOfSquares)
            self.queryVector = [float("{0:.4f}".format(self.weightedQuery[i] / length))
                                for i in range(len(self.weightedQuery))]

        return self.queryVector

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

    # @timing
    def similarity(self, normalizedQuery):
        indexList = []
        docIndices = []
        similarityVector = []

        if not self.docVector:
            print(
                "did not match any documents.")
            return indexList

        if self.docVector:
            for i in range(len(self.queryList)):
                similarityVector.append(
                    float("{0:.4f}".format(self.similarityDistance(normalizedQuery, self.docVector[i]))))
            indexList = sorted(range(len(similarityVector)), key=lambda k: similarityVector[k])

        for i in indexList:
            docIndices.append(self.doc_key[i])

        docIndices.reverse()
        similarityVector.sort()
        similarityVector.reverse()
        self.rankedOutput.append(docIndices)
        self.rankedOutput.append(similarityVector)
        # self.rankedOutput = [self.rankedOutput[i][0:20] for i in range(len(self.rankedOutput))]

    # @timing
    def proximity(self):
        documentIndices = []
        self.proxArray = {}
        for i in range(len(self.queryList)):
            self.proxArray[self.queryList[i]] = {"count": 1, "proximity": 1000}

        for n, k in enumerate(self.termList[:-1]):
            for i in self.proxVector[self.termList[n]]:
                for j in self.proxVector[self.termList[n + 1]]:

                    if i == j:
                        for l in range(len(self.proxVector[self.termList[n]][i])):
                            for m in range(len(self.proxVector[self.termList[n + 1]][j])):
                                count = 0
                                value = int(self.proxVector[self.termList[n]][i][l]) - int(
                                    self.proxVector[self.termList[n + 1]][j][m])
                                count = self.proxArray[self.queryList[j]]["count"]
                                count = count + 1
                                self.proxArray[self.queryList[j]]["count"] = count
                                self.proxArray[self.queryList[j]]["proximity"] = abs(value)
                                break

        newlist = collections.OrderedDict(sorted(self.proxArray.items(),
                                                 key=lambda kv: (kv[1]['count'], -kv[1]['proximity']), reverse=True))

        cosineVecIndices = []
        for i in range(len(self.rankedOutput[0])):
            cosineVecIndices.append([item[0] for item in list(self.rankedOutput[0][i].values())])

        newSimilarityVector = []
        for i in newlist.keys():
            for j in cosineVecIndices:
                val1 = str(j).replace("[", "").replace("]", "")
                if i == int(val1):
                    newSimilarityVector.append([cosineVecIndices.index(j), float("{0:.6f}".format(((float(
                        self.rankedOutput[1][cosineVecIndices.index(j)])) * (float(
                        list(newlist.values())[i]["count"]))) / (float(list(newlist.values())[i]["proximity"]))))])
                    break
        list1 = sorted(newSimilarityVector, key=itemgetter(1), reverse=True)

        for i in range(len(list1)):
            documentIndices.append(self.rankedOutput[0][list1[i][0]])

        self.proxRankedOutput.append(documentIndices)
        self.proxRankedOutput.append([i[1] for i in list1])

    def writeOutput(self, outFile):
        out = shelve.open(outFile)
        out['rankedOutput'] = self.rankedOutput
        out['proxRankedOutput'] = self.proxRankedOutput
        out['queryVector'] = self.queryVector
        out.close()

    def showResult(self):
        ranks = []
        self.sliced = [self.rankedOutput[i][0:10] for i in range(0, 1)]
        for m in range(len(self.sliced[0])):
            ranks.append(m)

        self.sliced.append(ranks)
        return self.sliced

    def relevanceFeedback(self, infile, relevantDoc):
        query = shelve.open(infile)
        self.queryVector = query['queryVector']
        query.close()
        a = 0.5
        b = 0.5
        docVectorIndices = []
        docVectorIndices.append(int(relevantDoc[1:]) - 1)
        relevantDocVectors = [self.docVector[i] for i in docVectorIndices]
        totalReleVec = [sum(i) for i in zip(*relevantDocVectors)]
        newReleVec = [j * b for j in totalReleVec]
        updatedQuery = [i * a for i in self.queryVector]
        newQ = [sum(x) for x in zip(updatedQuery, newReleVec)]
        self.similarity(newQ)
        self.writeOutput('OUTPUT/queryOutput')
        return self.showResult()


@timing
def main():
    queryInstance = similarity('OUTPUT/processingOutput.db', 'OUTPUT/processingArtifacts.db')
    queryInstance = similarity()
    # TODO: get the query from cgi
    tokenizedQuery = queryInstance.tokenizeQuery(["truck", "arriv"])
    normalizedQuery = queryInstance.normalizeQuery(tokenizedQuery)
    queryInstance.similarity(normalizedQuery)
    queryInstance.proximity()

    # normalizedQuery = queryInstance.normalizeQuery(["truck", "arriv"])
    # queryInstance.similarity(normalizedQuery)
    # queryInstance.proximity(["truck", "arriv"])
    queryInstance.showResult()
    queryInstance.writeOutput('OUTPUT/queryOutput')

    # TODO: get the relevant doc from cgi
    newResult = queryInstance.relevanceFeedback('OUTPUT/queryOutput','D2')


if __name__ == "__main__":
    main()
