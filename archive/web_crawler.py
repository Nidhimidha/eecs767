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
# Python EECS 767 Niche Web Crawler
# Author: Blake Bryant
# KU Student ID: 2732226
# Date started: 3/27/2018
# Date finished: xx/xx/xxxx
#
# This program requires a seed url to crawl for additional urls
# The seed URL web page will be stored as well as all other urls
# within the same domain


#
#variables
#

# the URL seed is the beginning search point for crawling
url_seed = 'http://www.oldbaileyonline.org/'


url= 'http://www.oldbaileyonline.org/browse.jsp?id=t17800628-33&div=t17800628-33'
#cached_doc_path ='C:\Users\b589b426\Documents\_student\EECS_767\Project\cached_docs'
cached_doc_path = '/cached_docs'

def func_find_urls_on_page(page):
    try:
        words=[] #array to store each word in the web page
        words=page.split()#split page into words
        try:
            #print (page)
            #url_match = re.compile('(.*?http\w+)',re.DOTALL)
            #result = url_match.match(page)
            #print (result)
            #search words for href tag

            hyperlink_match = re.compile('(href=".*?")',re.DOTALL)#how to tell if a link
            #hyperlink_match = re.compile('(?:href=")(.*?)(?:".*?)',re.DOTALL)#how to tell if a link
            hyperlink_ignore = re.compile('(.*?.css")|(.*?javascript.*?)|(/#.*?)',re.DOTALL)#links to ignore, such as .css
            hyperlink_clean = re.compile('(href=")|(".*?)|(>.*?)|(<.*?)|(\s+.*?)',re.DOTALL)
            for word in words:
                if hyperlink_match.match(word):
                    if not hyperlink_ignore.match(word):
                        word = re.sub(hyperlink_clean,' ',str(word))
                        #word = word.translate(None, 'href="')
                        print word
                        #url_seed + word #should be a proper url to download more stuff 
                
            
            #print words
            
        except:
            print ('Error in regex', sys.exc_info()[0], sys.exc_info()[1])
    except:
        print ('Error finding urls', sys.exc_info()[0], sys.exc_info()[1])

def func_download_page(url):
    # open the URL
    try:
        page = urllib2.urlopen(url).read()
    except:
        print ('Error using urllib to read webpage at url', sys.exc_info()[0], sys.exc_info()[1])
        
    # write the URL content to a file
    try:
        
        #remove prefix of url from url field e.g. http:// or the url_seed
        #this is necessary to shorten the length of the file name
        try:
            #tags = re.compile('(http://)',re.DOTALL)
            tags = re.compile(url_seed,re.DOTALL)          
        except:
            print ('Error in regex', sys.exc_info()[0], sys.exc_info()[1])
        try:
            stripped_url = re.sub(tags,'',str(url)) #remove html tags
        except:
            print ('Error stripping prefix with regex', sys.exc_info()[0], sys.exc_info()[1])

        #remove punctuation from url to allow for writing to file in windows systems
        try:
            #stripped_url = stripped_url.translate(None, url_seed)
            stripped_url = stripped_url.translate(None, string.punctuation)
        except:
            print ('Error removing punctuation from url', sys.exc_info()[0], sys.exc_info()[1])

        try:
            filename = 'cached_docs/'+stripped_url+'.htm'
            #print (filename)##for debugging
            f= open(filename, "w")
            f.write(page)
            f.close
        except:
            print ('Error writing page to local file', sys.exc_info()[0], sys.exc_info()[1])
    except:
        print ('Error writing webpage to local file', sys.exc_info()[0], sys.exc_info()[1])
    return page
# Begin program

# This section of code will provide a brief introductory message and instructions of using the program
print ("Welcome to the EECS767 web crawling")
#func_download_page(url)
func_find_urls_on_page(func_download_page(url))

print ('Program complete!')
