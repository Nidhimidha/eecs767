import os
import sys
import io
import fileinput
import string
import urllib #required to open html documents
import re #required to remove html tags vie regex
import codecs #required to open html files
import nltk #requires python 3.5 or python 2.7 to install
from nltk.stem.porter import *
from nltk.corpus import stopwords #must download stopwords at least once.  This is done by
                                  #open the python shell and type:
                                  #import nltk
                                  #nltk.download("stopwords")

#
# Python LEECS 767 Document Parsing
# Author: Blake Bryant
# KU Student ID: 2732226
# Date started: 2/19/2018
# Date finished: xx/xx/xxxx
#
# This program requests a directory path from the user.  All documents
# in the path provided are then tokenized (converted to lower case,
# stripped of punctuation, and split into an array of words

# The frequency of each term in a document is stored as an array
# that is then added to a dictionary of terms

 
#
#    Function definitions
#    This function queries the user to input a directory path to search

def func_get_directory_name():
    try:
        directoryName = input ('Please enter a directory containing documents ot index: ')
        print ('Indexing documents in directory "' +directoryName+'"')
        return directoryName
    except:
        print ('Error accessing directory')

# This function searches for html tags within documents and removes them prior
# to tokenization

def func_tokenize(raw_input):
    try:
        stop_words = set(stopwords.words('english'))
    except:
        print ('Error creating stop words.  Please verify the stopwords were imported prior to running this program')
        print ('Run the following commands in a python shell to download the stop words')
        print ('import nltk')
        print ('nltk.download("stopwords")')
    try:
        
        tags = re.compile('((\<script.*?\>).*?(\<\/script\>))|((\<style.*?\>).*?(\<\/style\>))|(\<.*?\>)|(\<.*?\/\>)|(\<\/.*?\>)|(&\w+;)|(html)|(\\\\n)|(\\\\x\w\w)',re.DOTALL) #works at removing style tags
        tr = str.maketrans(" ", " ", string.punctuation)#used to strip punctuation
        stemmer = PorterStemmer() #create a stemmer with the nltk porter stemmer
        
        line = tags.sub(' ',str(raw_input)) #remove html tags
        line= (line.lower().translate(tr).split())#convert line to lower case, remove punctionation and tokenize
        line=[word for word in line if word not in stop_words] #remove stop words from raw line
        line=[stemmer.stem(term) for term in line] #use nltk stemmer to convert to word roots
 #       line= (line.split())#tokenize
        return line
    except:
        print ('Error removing html tags')


        
# Begin program
# This section of code will provide a brief introductory message and instructions of using the program
print ("Welcome to the EECS767 document parsing program!")

#Open all files in the directory provided by the func_get_directory_name() funciton
# store each document as row within a table called "data"
# store document id, name and path to document in a dictionary called "doc_key"
try:
   
    #path=func_get_directory_name()
    #path=str('/Users/blakebryant/Documents/_KU_Student/EECS_767_Info_Retrieval/project/docsnew/')
    path=str('/Users/blakebryant/Documents/_KU_Student/EECS_767_Info_Retrieval/project/few_html/')
    #path=str('/Users/blakebryant/Documents/_KU_Student/EECS_767_Info_Retrieval/project/test_docs/')

    #print (path) #Debugging
    documents_in_directory = os.listdir(path)
    #print (documents_in_directory) ##Debugging
    data = []
    doc_key={}#create dictionary to store document information
    for document_id, filename in enumerate(documents_in_directory):
        if not filename.startswith('.'): #and os.path.isfile(os.path.join(root, filename)):
            doc_key[filename]=[document_id,os.path.abspath(filename)]
            page = urllib.request.urlopen('file://'+path+filename).read() #using urllib as it is required for html docs
            print ('Caching document'+ str(document_id))
            line = func_tokenize(page) #remove HTML tags from the document
            data.append(line)# add tokenized document to data array           
            #print (page)
    #print ('Document Key: ') ##Debugging
    #print (doc_key)##test print doc_key
except:
    print ('Error opening file')
    
#Iterate through each document (row in data) and append term frequemcy
#to the document position in the terms dictionary  
try:
    num_docs=len(data)
    terms={}
    print ('Creating index')
    for document_id, document in enumerate (data):
        print ('Parsing terms for document_id'+ str(document_id))
        #print ('analyzing document '+str(document_id)) ##Debugging info
        #print ('document ' + str(document))    ##Debugging info
        for term in document:                  
            if term in terms:
                terms[term][document_id]+=1
            else:
                terms[term]=[0]*num_docs
                terms[term][document_id]+=1
    #print ('Terms index: ')
    #print (terms) #debugging info
except:       
  print ('Error updating tf values in terms dictionary')
  
#print term index and doc_key to output file
try:
    print ('Writing data to files')
    try:
        index_out_put_file = open('index.txt','w')
        index_out_put_file.write(str(terms))
        index_out_put_file.close()
    except:
        print ('Error printing data to index file')
    try:
        doc_key_out_put_file = open('doc_key.txt','w')
        #doc_key_out_put_file.write(str(doc_key)) # generating an error with the (r) symbol in the file name
        #'Wrangell®CSt_Elias_National_Park_and_Preserve.htm'
        print('',doc_key, file=doc_key_out_put_file)
        doc_key_out_put_file.close()
    except:
        print ('Error printing data to doc_key file', sys.exc_info()[0])
except:
    print ('Error writing data to file', sys.exc_info()[0])

print ('Program complete!')

