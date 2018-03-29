import os
import json
import shelve
import sys
import io
import fileinput
import string
import urllib #required to open html documents
import urllib2 #required in python 2.7
import re #required to remove html tags vie regex
import codecs #required to open html files
import nltk #requires python 3.5 or python 2.7 to install
from nltk.stem.porter import *
from nltk.corpus import stopwords #must download stopwords at least once.  This is done by
                                  #open the python shell and type:
                                  #import nltk
                                  #nltk.download("stopwords")
from collections import defaultdict #necessary for the proximity data structure                                

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
# Variables
#


#path =('C:\\Users\\b589b426\\Documents\\_student\\EECS_767\\Project\\docsnew\\')
path = ('/Users/terrapin/Documents/GitHub/eecs767/CODE/INPUT/docsnew/') 




 
#
#    Function definitions
#    This function queries the user to input a directory path to search

def func_get_directory_name():
    try:
        directoryName = raw_input ('Please enter a directory containing documents ot index: ')
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
        try:
            tags = re.compile('(b\')((\<script.*?\>).*?(\<\/script\>))|((\<style.*?\>).*?(\<\/style\>))|(\<.*?\>)|(\<.*?\/\>)|(\<\/.*?\>)|(&\w+;)|(html)|(\\\\n)|(\\\\x\w\w)',re.DOTALL) #works at removing style tags
            
        except:
            print ('Error in regex', sys.exc_info()[0], sys.exc_info()[1])
        ### the following section uses Python 3 conventions
        #try:
            ##tr = str.maketrans(" ", " ", string.punctuation)#used to strip punctuation ## need to change for python 2   THis is python 3
        #except:
            #print ('Error removing punctuation', sys.exc_info()[0])     
        ### End Python 3 section
        #strip unicode from string
        try:
            raw_input = (raw_input.decode('unicode_escape').encode('ascii','ignore')) ##
        except:
            print ('Error removing unicode characters from line var', sys.exc_info()[0], sys.exc_info()[1])
        try:
            #line = tags.sub(' ',str(raw_input)) #remove html tags ##python 3 code
            line = re.sub(tags,' ',str(raw_input)) #remove html tags
        except:
            print ('Error removing html tags', sys.exc_info()[0], sys.exc_info()[1])
        try:
            #line= (line.lower().translate(tr).split())#convert line to lower case, remove punctionation and tokenize this uses python 3 requires uncommenting 
            line= (line.lower().translate(None, string.punctuation).split())#convert line to lower case, remove punctionation and tokenize #This is Python2 version
        except:
            print ('Error Changing case, removing punctuation and spliting', sys.exc_info()[0], sys.exc_info()[1])               
        try:
            line=[word for word in line if word not in stop_words] #remove stop words from raw line
        except:
            print ('Error with stop words', sys.exc_info()[0], sys.exc_info()[1])           
        try:
            stemmer = PorterStemmer() #create a stemmer with the nltk porter stemmer
            #print (type(term))
            #if type(term) is unicode:
                #try:
                    #print ('term is unicode')
                #except:
                    #print ('Error handling unicode for stemmer', sys.exc_info()[0])
##            for term in line:
##                #print (type(term))
##                #trying to write code to deal with unicode characters
##                if type(term) is unicode:
##                    try:
##                        print ('term is unicode')
##                        
##                        line= [stemmer.stem(term.decode('utf-8'))]                        
##                    except:
##                        print ('Error handling unicode for stemmer', sys.exc_info()[0], sys.exc_info()[1])
##                else:
##                    line=[stemmer.stem(term)]
                
            line=[stemmer.stem(term) for term in line] #use nltk stemmer to convert to word roots
        except:
            print ('Error with stemming', sys.exc_info()[0], sys.exc_info()[1])
            pass
        return line
    except:
        print ('Error in tokenizer function', sys.exc_info()[0], sys.exc_info()[1])
        pass

# This function writes data to text files via json


def func_json_out(terms,doc_key,proximity):
    try:
        print ('Exporting JSON data to text files')
        try:
            with open('index.txt','w') as index_out_put_file:
                index_out_put_file.write(json.dumps(terms))        
            
        except:
            print ('Error printing data to index file', sys.exc_info()[0], sys.exc_info()[1])
        try:
            with open('doc_key.txt','w') as doc_key_out_put_file:
                doc_key_out_put_file.write(json.dumps(doc_key))
        except:
            print ('Error printing data to doc_key file', sys.exc_info()[0], sys.exc_info()[1])
        try:
            with open('proximity.txt','w') as proximity_out_put_file:
                proximity_out_put_file.write(json.dumps(proximity))
        except:
            print ('Error printing data to doc_key file', sys.exc_info()[0], sys.exc_info()[1])  
        #export data via shelve
    except:
        print ('Error with func_json_out', sys.exc_info()[0], sys.exc_info()[1])
        
        
# Begin program
# This section of code will provide a brief introductory message and instructions of using the program
print ("Welcome to the EECS767 document parsing program!")

#Open all files in the directory provided by the func_get_directory_name() funciton
# store each document as row within a table called "data"
# store document id, name and path to document in a dictionary called "doc_key"
try:
   
    #path=func_get_directory_name()
    #path=str('/Users/blakebryant/Documents/_KU_Student/EECS_767_Info_Retrieval/project/test_docs/')
    #path=('C:\\Users\\b589b426\\Documents\\_student\\EECS_767\\Project\\test_docs\\')
    #path='/cached_documents/'
    #path=('C:\\Users\\b589b426\\Documents\\_student\\EECS_767\\Project\\cached_docs\\')
    #path=('C:\\Users\\b589b426\\Documents\\_student\\EECS_767\\Project\\docsnew\\')
    #print (path) #Debugging
    documents_in_directory = os.listdir(path)
    #print (documents_in_directory) ##Debugging
    data = []
    doc_key={}#create dictionary to store document information
    for document_id, filename in enumerate(documents_in_directory):
        #print(filename)#debugging
        if not filename.startswith('.'): #and os.path.isfile(os.path.join(root, filename)):
            #print(filename)#debugging
            doc_key[filename]=[document_id,os.path.abspath(filename)]
            #page = urllib.request.urlopen('file://'+path+filename).read() #Linux path #Python3 version
            try:
                page = urllib2.urlopen('file://'+path+filename).read()##linux path
                #page = urllib2.urlopen('file:\\'+path+filename).read()##windows path
                #page = urllib.request.urlopen('file:\\'+path+filename).read() #Windows path
            except:
                print ('Error using urllib to open file', sys.exc_info()[0], sys.exc_info()[1])
            print ('Caching document'+ str(document_id))
            line = func_tokenize(page) #remove HTML tags from the document
            try:
                data.append(line)# add tokenized document to data array
            except:
                print ('Error adding line to data', sys.exc_info()[0], sys.exc_info()[1])
except:
    print ('Error opening file')
    
#Iterate through each document (row in data) and append term frequemcy
#to the document position in the terms dictionary  
try:
    num_docs=len(data)
    terms={}
    #from collections import defaultdict
    #dates_dict = defaultdict(list)
    #for key, date in cur:
        #dates_dict[key].append(date)    
    proximity=defaultdict(list)
    print ('Creating index')
    for document_id, document in enumerate (data):
        print ('Parsing terms for document_id'+ str(document_id))
        for term_position, term in enumerate (document):                   
            if term in terms:
                try:
                    terms[term][document_id]+=1
                except:
                    print ('Error updating term in terms dictionary', sys.exc_info()[0], sys.exc_info()[1])
                try:
                    #print ('debugging proximity dictionary')
                    #print (proximity[term])
                    
                    #assign the current term proximity to a list for appending additional tuples
                    temp_list=proximity[term]
                    try:
                        temp_list.append((document_id,term_position))
                        #print ('debugging temp list')
                        #print (temp_list)
                    except:
                        print ('Error appending data to temp_list', sys.exc_info()[0], sys.exc_info()[1])
                    #change term value to temp list   
                    proximity[term]=temp_list
                    #print ('debugging proximity[term] after appending')
                    #print (proximity[term])
                except:
                    print ('Error updating proximity in proximity dictionary', sys.exc_info()[0], sys.exc_info()[1])
                    
            else:
                # Add a new key to the terms dictionary
                try:
                    terms[term]=[0]*num_docs
                    terms[term][document_id]+=1
                except:
                    print ('Error adding new term to term dictionary', sys.exc_info()[0], sys.exc_info()[1])
                    
                # Add a new key to the proximity dictionary
                try:
                    proximity[term]=[(document_id,term_position)] #store proximity in a separate dictionary, this is a list of a tupple with a list inside it
                except:
                    print ('Error adding new proximity to proximity dictionary', sys.exc_info()[0], sys.exc_info()[1])
except:       
    print ('Error updating tf values in terms dictionary', sys.exc_info()[0], sys.exc_info()[1])
  
#print term index and doc_key to output file
#This section has been rewritten to export data via json
#as this addressed several issues in attempting to convert 
#values
try:
    
    ## the following function is optional and outputs data to .txt files via JSON
    ## this may assist in troubleshooting
    #func_json_out(terms,doc_key,proximity)
    
    print ('Exporting data to shelf .db file')
    try:   
        d = shelve.open('OUTPUT/ingestOutput.db')
        d['index'] = [terms]
        d['doc_key'] = [doc_key]
        d['proximity'] = proximity
        d.close()   
    except:
        print ('Error exporting data via shelve', sys.exc_info()[0], sys.exc_info()[1]) 
        
except:
    print ('Error writing data to file', sys.exc_info()[0], sys.exc_info()[1])

print ('Program complete!')
