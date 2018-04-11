import shelve
import math
from math import log10, sqrt
#import ingest
#from ingest import *
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
##      ...,
##      [ DocNamen, DocLocationn, Rankn, Summaryn]
##  ]

class similarity:

    def __init__(self, infile):
        proc = shelve.open(infile)
        self.docVector = proc['docVector']
        self.doc_key = proc['doc_key']
        self.proxVector = proc['proxVector']
        self.termIndex = proc['termIndex']
        #print("self.docVector")
        #print(self.docVector)
        #print("self.doc_key")
        #print(self.doc_key)
        #print("self.proxVector")
        #print(self.proxVector)
        #print("self.termIndex")
        #print(self.termIndex)
        proc.close()
        self.result = []
        self.weightedQuery = []

    #def tokenizeQuery(self, query):
        #return func_tokenize(query)

    def findWholeWord(self, word, query):
        pattern = re.compile(r'\b({0})\b'.format(word), flags=re.IGNORECASE)
        for x in query:
                if pattern.search(x):
                    return True


    def normalizeQuery(self, query):

        self.weightedQuery = [0] * len(self.termIndex)

        for k in self.termIndex:
            if self.findWholeWord(k,query):
		        idf = self.termIndex[k][0]
            else:
                idf = 0

            self.weightedQuery[self.termIndex[k][1]] = idf
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

    def proximity(self, query):

        for k in range(len(self.proxVector)):
            count = 0
            for i in range(len(query)):
                for term in self.termIndex:
                    print term, "::", query[i]
                    if query[i] == term:
                        self.index1 = self.termIndex[term][1]
                        count = count + 1
                    if i != (len(query)-1):
                        if query[i+1] == term:
                            self.index2 = self.termIndex[term][1]

                #print query[i], "::", self.index1
                #print query[i+1], "::", self.index2

                val1 = str(self.proxVector[k][self.index1]).replace("[", "").replace("]", "")
                val2 = str(self.proxVector[k][self.index2]).replace("[", "").replace("]", "")
                if val1 and val2:
                        if not val1.__contains__(",") and not val2.__contains__(","):
                            value = int(val1) - int(val2)
                            print "Gap between is",value
                            self.result.append(abs(value))

                for term in self.termIndex:
                    if query[i] == term:
                        count = count + 1
                print k, "::", count

    def writeOutput(self, outFile):
        out = shelve.open(outFile)
        print(self.rankedOutput)
        out['rankedOutput'] = self.rankedOutput
        print(self.queryVector)
        out['queryVector'] = self.queryVector
        out.close()


    def showResult(self):
        ranks = []
        self.sliced = [self.rankedOutput[i][0:10] for i in range(0, 1)]
        for m in range(len(self.sliced[0])):
            ranks.append(m)

        self.sliced.append(ranks)
        print("self.sliced")
        print(self.sliced)
        return self.sliced


    def relevanceFeedback(self,relevantDoc):
        query = shelve.open('OUTPUT/queryOutput')
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


def main():
    queryInstance = similarity('OUTPUT/processingOutput.db')
    # TODO: get the query from cgi
    #tokenizedQuery = queryInstance.tokenizeQuery("truck arrived of")
    normalizedQuery = queryInstance.normalizeQuery(["truck", "arriv"])
    queryInstance.similarity(normalizedQuery)
    queryInstance.proximity(["truck", "arriv"])
    queryInstance.showResult()
    queryInstance.writeOutput('OUTPUT/queryOutput')

    # TODO: get the relevant doc from cgi
    newResult = queryInstance.relevanceFeedback('D2')

if __name__ == "__main__":
    main()
