import os
import time
from functools import wraps
import json
import shelve
import sys
import io
import fileinput
import string
import urllib #required to open html documents
#import urllib2 #required in python 2.7
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


#-------------------------------------------------------------------------
# Variables
#

#--------------------------------------------------------------------------


file_format='file://' #linux format
#path = ('/Users/terrapin/Documents/GitHub/eecs767/CODE/INPUT/docsnew/') ##linux Prod

#path = ('/Users/blakebryant/Documents/_KU_Student/EECS_767_Info_Retrieval/project/docsnew/') ##Blake's MAC
#path = ('/Users/blakebryant/Documents/_KU_Student/EECS_767_Info_Retrieval/project/cached_docs/') ##Blake's MAC

path = ('/home/splunk/Documents/EECS_767/Project/cached_docs/')
#path = ('/home/splunk/Documents/EECS_767/Project/test_docs/')
#path = ('/home/splunk/Documents/EECS_767/Project/docsnew/')

#path = ('/home/splunk/Documents/EECS_767/Project/_medium_doc_sample/')
#path = ('/home/splunk/Documents/EECS_767/Project/_large_doc_sample/')

#file_format='file:\\' #windows format
#path =('C:\\Users\\b589b426\\Documents\\_student\\EECS_767\\Project\\docsnew\\')## windows
#path =('C:\\Users\\b589b426\\Documents\\_student\\EECS_767\\Project\\cached_docs\\')## windows

#path =('C:\\Users\\b589b426\\Documents\\_student\\EECS_767\\Project\\test\\')

if(len(sys.argv)>1):
	path=sys.argv[1]

#-------------------------------------------------------------------------------
#
#    Function definitions
#-------------------------------------------------------------------------------
# This function adds timing data to program execution
def timing(f):
        @wraps(f)
        def ft(*args, **kwargs):
                t0 = time.time()
                exe = f(*args, **kwargs)
                t1 = time.time()
                print ("\t%s Execution Time (sec): %s" %
                        (f.__name__, str(t1-t0)))
                return exe
        return ft

#    This function queries the user to input a directory path to search
#@timing #comment out to remove timing
def func_get_directory_name():
    try:
        directoryName = raw_input ('Please enter a directory containing documents ot index: ')
        print ('Indexing documents in directory "' +directoryName+'"')
        return directoryName
    except:
        print ('Error accessing directory')



# This function searches for html tags within documents and removes them prior
# to tokenization

#@timing #comment out to remove timing
def func_tokenize(raw_input):
    try:
        #stop_words = set(stopwords.words('english'))
        new_words_list=stopwords.words('english')
        new_words_list.append('home')# adding home to stop words list because it is in every document
        stop_words = set(new_words_list)
    except:
        print ('Error creating stop words.  Please verify the stopwords were imported prior to running this program')
        print ('Run the following commands in a python shell to download the stop words')
        print ('import nltk')
        print ('nltk.download("stopwords")')
    try:        
        try:
            #tags = re.compile('(b\')((\<script.*?\>).*?(\<\/script\>))|((\<style.*?\>).*?(\<\/style\>))|(\<.*?\>)|(\<.*?\/\>)|(\<\/.*?\>)|(&\w+;)|(html)|(\\\\n)|(\\\\x\w\w)',re.DOTALL) #works at removing style tags
            #tags = re.compile('(b\')((<script.*?>).*?(</script>))|((<style.*?>).*?(</style>))|(<.*?>)|(<.*?/>)|(</.*?>)|(&\w+;)|(html)|(\\\\n)|(\\\\x\w\w)',re.DOTALL) #works at removing style tags
            #tags = re.compile('(<script>.*?</script>)|(<noscript>.*?</noscript>)|(<!--.*?-->)|(<.*?>)|(<.*?>\w)',re.DOTALL)
            #tags = re.compile('(<!.*?>)|(<script>.*?</script>)|(<noscript>.*?</noscript>)|(<.*?>)|((\\u[0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ]+)*)',re.DOTALL)
            #tags = re.compile('(<!.*?>)|(<script>.*?</script>)|(<noscript>.*?</noscript>)',re.DOTALL)
            #tags = re.compile('(<!.*?>)|(<script>.*?</script>)|(<noscript>.*?</noscript>)|([\\u2000-\\u2100])|(\\u00f8)|(\\u00b0)|([\\u0500-\\u0600])|([\\u5000-\\u6000])',re.DOTALL)
            tags = re.compile('(^<.*?>)|(^<!.*?>)|(^<script>.*?</script>)|(^<noscript>.*?</noscript>)|([\\u0080-\\uFFEF])',re.DOTALL)
            #tags = re.compile(r'(<!.*?>)|(<script>.*?</script>)|(<noscript>.*?</noscript>)|(\\u\d*[\s|\w*])',re.DOTALL)
            #tags = re.compile(r'(<!.*?>)|(<script>.*?</script>)|(<noscript>.*?</noscript>)|([^\\u0200-\\uFFFF])',re.DOTALL)##attempt to remove unicode
            reg_numbers = re.compile(r'(\s\d+\s)')
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
	    #print ('Error removing unicode characters from line var', sys.exc_info()[0], sys.exc_info()[1])
            pass
	    
        try:
            #line = tags.sub(' ',str(raw_input)) #remove html tags ##python 3 code
            line = re.sub(tags,' ',str(raw_input)) #remove html tags
        except:
            print ('Error removing html tags', sys.exc_info()[0], sys.exc_info()[1])
        try:
            
            #line= (line.lower().translate(tr).split())#convert line to lower case, remove punctionation and tokenize this uses python 3 requires uncommenting 
            #line= (line.lower().translate(None, string.punctuation).split())#convert line to lower case, remove punctionation and tokenize #This is Python2 version
            #right_num_spaces=" "*256
            punctuation =re.compile('['+string.punctuation+']')
            line= re.sub(punctuation,' ',line)#remove punctuation with regex but replace with a space to preserve words
            #line = re.sub(reg_numbers,'',line)#remove numbers from string
            line=line.lower().split()#convert to lowercase and split into words
           
            
        except:
            print ('Error Changing case, removing punctuation and spliting', sys.exc_info()[0], sys.exc_info()[1])  
                     
        try:
            line=[word for word in line if word not in stop_words] #remove stop words from raw line
        except:
            print ('Error with stop words', sys.exc_info()[0], sys.exc_info()[1])           
        try:
            stemmer = PorterStemmer() #create a stemmer with the nltk porter stemmer               
            line=[stemmer.stem(term) for term in line] #use nltk stemmer to convert to word roots
        except:
            print ('Error with stemming', sys.exc_info()[0], sys.exc_info()[1])
            pass
        return line
    except:
        print ('Error in tokenizer function', sys.exc_info()[0], sys.exc_info()[1])
        pass

    

# ----------------------------------------------------------------
# Class used to store values and functions used by main
# ----------------------------------------------------------------

class IndexValues(object):
    def __init__(self, data, doc_key,title_map, terms, proximity,download_manifest,num_docs):
        self.data = data #array to store raw input from file
        self.doc_key = doc_key #dictionary to store document information
        self.title_map=title_map#used to map titles to filenames
        self.terms=terms #dictionary to store terms and their frequency
        self.proximity=proximity # dictionary to store term location within documents
        self.download_manifest=download_manifest#this should be a dictionary stored in an external .db file
        self.num_docs=num_docs

    # This function parses documents to generate term frequency and term proximity
    # This function calls the parsing document function
    #@timing #comment out to remove timing
    def func_create_index(self):   
        #Iterate through each document (row in data) and append term frequemcy
        #to the document position in the terms dictionary  
        try:
            self.num_docs=len(self.data)#used to initialize terms arrays
            print ('Creating index')
            for document_id, document in enumerate (self.data):
                self.func_parse_document(self.num_docs,document_id,document)
        except:       
            print ('Error updating tf values in terms dictionary', sys.exc_info()[0], sys.exc_info()[1])
        #return index_data()
    #This function parses the document for <title> tags and stores the stringe within the tags in a
    #dictionary called "title_map"
    #@timing #comment out to remove timing
    def func_parse_title(self,page,filename):
        #print ('Parsing title for document'+ str(filename))
        try:
            match = re.search(r'(<title>)(.*?)(<)',page) #regex to match title and tags as separate capture groups
            title = match.group(2)	#regex to return the string between tags
            #print ('printing title')
            #print (title)
            self.title_map[filename]=[title] #store title in the title_map dictionary
        except:
            print('Error parsing title of document', sys.exc_info()[0], sys.exc_info()[1])
        #terms=getattr(index_data,terms)
            
    #@timing #comment out to remove timing
    def func_parse_document(self,num_docs,document_id,document):
        print ('Parsing terms for document_id'+ str(document_id))
        #terms=getattr(index_data,terms)
        #proximity=getattr(index_data,proximity)
        for term_position, term in enumerate (document):                   
            if term in self.terms:
                try:
                    #terms[term][document_id]+=1
                    self.terms[term][document_id]+=1
                except:
                    print ('Error updating term in terms dictionary', sys.exc_info()[0], sys.exc_info()[1])
                try:                   
                    #assign the current term proximity to a list for appending additional tuples
                    temp_list=self.proximity[term]
                    try:
                        temp_list.append((document_id,term_position))
                        #print ('debugging temp list')
                        #print (temp_list)
                        #change term value to temp list   
                        #proximity[term]=temp_list
                        #setattr(index_data,proximity[term],temp_list)
                        self.proximity[term]=temp_list
                    except:
                        print ('Error appending data to temp_list', sys.exc_info()[0], sys.exc_info()[1])
                   
                except:
                    print ('Error updating proximity in proximity dictionary', sys.exc_info()[0], sys.exc_info()[1])
                    
            else:
                # Add a new key to the terms dictionary
                try:
                    self.terms[term]=[0]*num_docs
                    #setattr(index_data,terms[term],terms)
                    self.terms[term][document_id]+=1
                    #setattr(index_data,terms[term],terms)
                except:
                    print ('Error adding new term to term dictionary', sys.exc_info()[0], sys.exc_info()[1])
                    
                # Add a new key to the proximity dictionary
                try:
                    self.proximity[term]=[(document_id,term_position)] #store proximity in a separate dictionary, this is a list of a tupple with a list inside it
                   
                except:
                    print ('Error adding new proximity to proximity dictionary', sys.exc_info()[0], sys.exc_info()[1])

    # This function writes data to text files via json
    #@timing #comment out to remove timing
    def func_json_out(self):
        try:
            print ('Exporting JSON data to text files')
            try:
                with open('index.txt','w') as index_out_put_file:
                    index_out_put_file.write(json.dumps(self.terms))        
                
            except:
                print ('Error printing data to index file', sys.exc_info()[0], sys.exc_info()[1])
            try:
                with open('doc_key.txt','w') as doc_key_out_put_file:
                    doc_key_out_put_file.write(json.dumps(self.doc_key))
            except:
                print ('Error printing data to doc_key file', sys.exc_info()[0], sys.exc_info()[1])
            try:
                with open('proximity.txt','w') as proximity_out_put_file:
                    proximity_out_put_file.write(json.dumps(self.proximity))
            except:
                print ('Error printing data to doc_key file', sys.exc_info()[0], sys.exc_info()[1])
            try:
                with open('title_map.txt','w') as title_map_out_put_file:
                    title_map_out_put_file.write(json.dumps(self.title_map))
            except:
                print ('Error printing data to title_map file', sys.exc_info()[0], sys.exc_info()[1]) 
            try:
                with open('num_docs.txt','w') as num_docs_out_put_file:
                    num_docs_out_put_file.write(json.dumps(self.num_docs))
            except:
                print ('Error printing data to title_map file', sys.exc_info()[0], sys.exc_info()[1])

            #export data via shelve
        except:
            print ('Error with func_json_out', sys.exc_info()[0], sys.exc_info()[1])
            
    #@timing #comment out to remove timing        
    def func_export_data_via_shelve(self):    
        try:           
            print ('Exporting data to shelf .db file')
            try:   
                d = shelve.open('OUTPUT/ingestOutput')
                d['index'] = self.terms
                d['doc_key'] = self.doc_key
                d['proximity'] = self.proximity ## may be wrong without []
                d['title_map']=self.title_map 
                d['num_docs']=self.num_docs
                d.close()   
            except:
                print ('Error exporting data via shelve', sys.exc_info()[0], sys.exc_info()[1]) 
                
        except:
            print ('Error writing data to file', sys.exc_info()[0], sys.exc_info()[1])
    #@timing #comment out to remove timing
    def func_read_download_manifest(self,path):
        try: 
            #with open(path+"download_manifest.txt", "r") as download_manifest_file:
                #manifest=download_manifest_file.readline() 
                #file_url=
                #download_shelf_file = shelve.open(path+'download_manifest.db')#python 2
                download_shelf_file = shelve.open(path+'download_manifest')#python 3
                self.download_manifest = download_shelf_file['manifest']                
        except:
            print ('Error opening download manifest', sys.exc_info()[0], sys.exc_info()[1])      

    #Open all files in the directory provided by the func_get_directory_name() funciton
    # store each document as row within a table called "data"
    # store document id, name and path to document in a dictionary called "doc_key"
    #@timing #comment out to remove timing  
    def func_open_files(self,path):
        try:
            print ('Opening documents in '+str(path))
            documents_in_directory = os.listdir(path)
            #print (documents_in_directory) ##Debugging
            #data = []
            document_id=0
            #doc_key={}#create dictionary to store document information
            for document, filename in enumerate(documents_in_directory):
                #def func_open_document(doc_key
                print(filename)#debugging
                #if not (filename.startswith('.') or filename.endswith('.db')):# added exclusion for .db file to prevent parsing the manifest file 		
                if (filename.endswith('.htm') or filename.endswith('.txt')):#only open.htm files.  This will ignore data files
                        #------------------
                        #---------------- need to fix tests for manifest file which doesnt exist yet
                        try:
                                if self.download_manifest:
                                        self.doc_key[filename]=[document_id,os.path.abspath(filename),str(self.download_manifest[filename])]
                                else:
                                        self.doc_key[filename]=[document_id,os.path.abspath(filename),"no_url"]
                        except:
                            print ('Error appednding document info to doc_key', sys.exc_info()[0], sys.exc_info()[1])
                        try:
                            print ('Caching document '+ str(document_id))
   			    #page = urllib2.urlopen(file_format+path+filename).read()##python 2 version
                            page = urllib.request.urlopen(file_format+path+filename).read().decode('utf-8')#python 3 version
                            document_id+=1
                        except:
                            print ('Error using urllib to open file', sys.exc_info()[0], sys.exc_info()[1])
                        print ('Parsing title and tags from '+str(filename))  
                        self.func_parse_title(page,filename)
                        line = func_tokenize(page) #remove HTML tags from the document
                        try:
                            self.data.append(line)
        
                        except:
                            print ('Error adding line to data', sys.exc_info()[0], sys.exc_info()[1])
        except:
            print ('Error opening file', sys.exc_info()[0], sys.exc_info()[1])
 
#-------------------------------------------------------------
# The Main Program
#
#----------------------------------------------------------

@timing #comment out to remove timing
def main():
    print ("Welcome to the EECS767 document parsing program!")
    index_data=IndexValues([],{},{},{},defaultdict(list),{},0)
    index_data.func_read_download_manifest(path)
    index_data.func_open_files(path)   
    index_data.func_create_index() 
    #index_data.func_json_out()#May be useful for debugging
    index_data.func_export_data_via_shelve()
    print ('Program complete!')
if __name__ == "__main__":    
	main()
