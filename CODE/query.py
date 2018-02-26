import shelve
import math


class similarity:

    def __init__(self, infile):
         # self.docVector = [[0.125,0,0.301,0,0.602,0.301,0.125,0.125,0,0.301,0],[0.125,0.125,0,0.602,0,0,0.125,0.125,1.204,0,0.125],[0.125,0.125,0,0,0,0.301,0.125,0.125,0,0.301,0.125],[0,0.125,0.301,0,0,0,0,0,0,0,0.125]]
         # self.doc_key = [1,2,3,4,5,6,7,8,9,10,11]
         proc = shelve.open(infile)
         self.docVector = proc['docVector']
         self.doc_key = proc['doc_key']
         proc.close()
        # print(docVector)
        # print(doc_key)

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



    ## TODO: Need to change the signature of computerSimilarity to accept the normalized query
    def similarity(self):
        indexList = []
        docIndices = []
        query = [0,0,0,0,0,0,0,0,0.602,0,0.125]

        similarityVector = []
        rankedOutput = []
        if not self.docVector:
            print(
                 "did not match any documents.")
            return indexList

        if self.docVector:
            for i in range(len(self.docVector)):
              similarityVector.append(self.similarityDistance(query, self.docVector[i]))
            print (similarityVector)
            indexList = sorted(range(len(similarityVector)), key=lambda k: similarityVector[k])

        for i in indexList:
            docIndices.append(self.doc_key[i])

        docIndices.reverse()
        similarityVector.sort()
        similarityVector.reverse()
        rankedOutput.append(docIndices)
        rankedOutput.append(similarityVector)
        # print (rankedOutput) : [[2, 4, 3, 1], [0.8759425974113635, 0.07280193431082146, 0.04990379797919978, 0.0]]
        return rankedOutput


def main():

    queryInstance = similarity('OUTPUT/processingOutput')
    queryInstance.similarity()
    queryInstance.writeOutput('OUTPUT/queryOutput')

if __name__ == "__main__":
        main()
