import os
import time #used to delay processing
from functools import wraps #used to create timing wrapper 
import json
import threading #required for multi-threading
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


# ----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#variables
#-----------------------------------------------------------------------------

# the URL seed is the root of all pages to be downloaded

#url_seed = 'http://www.oldbaileyonline.org/'
#url_seed='http://www.espn.com'
#url_seed='https://www.nist.gov/'
url_seed='https://www.iso.org'
#url is the first URL that should be downloaded.  This may be different from the
#url seed

#url= 'http://www.oldbaileyonline.org/browse.jsp?id=t17800628-33&div=t17800628-33'
#url='https://www.nist.gov/'
#url= 'http://www.oldbaileyonline.org/'
#url='http://www.espn.com/'
#https://www.rfc-editor.org/rfc-index.html
#https://standards.gov/sibr/query/index.cfm?fuseaction=rsibr.regulatory_sibr_all
url='https://www.iso.org/standards.html'
#https://www.loc.gov/
#https://www.ncaa.com/march-madness
#https://www.nasa.gov/
#https://www.uspto.gov/
#https://patentscope.wipo.int/search/en/sequences.jsf
#http://patentsgazette.uspto.gov/week06/OG/patenteeByName.html
#http://patentsgazette.uspto.gov/week06/OG/patenteeByType.html
#http://patentsgazette.uspto.gov/week06/OG/Cpc-a.html
#https://www.epo.org/index.html
#https://www.ama-assn.org/
#http://www.dcc.ac.uk/resources/metadata-standards/list
#https://www.nist.gov/
#https://www.ncdc.noaa.gov/cdo-web/

#cached_doc_path ='C:\Users\b589b426\Documents\_student\EECS_767\Project\cached_docs'

#this is the relative path to the directory where pages will be downloaded to
cached_doc_path = 'cached_docs/'
#--------End --Variables ---------------------------------------------------
#---------------------------------------------------------------------------


# ----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
# Global Functions
#-----------------------------------------------------------------------------
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



#This function is used to integrate with threading and
# call the webcrawler.func_download_page() function
#
def download_page_thread(url_to_download,crawler):
        print ('downloading:')
        print (url_to_download)
        try:
                downloaded=crawler.func_download_page(url_to_download)
        except:
                print('Error calling func_download_page in loop', sys.exc_info()[0], sys.exc_info()[1])
        try:
                if downloaded:#check if a file was downloaded.  Will be none for bad urls
                        crawler.func_find_urls_on_page(downloaded)
        except:
                print('Error calling func_find_urls_on_page in loop', sys.exc_info()[0], sys.exc_info()[1])
        time.sleep(1)  


#--------End --Global Functions ---------------------------------------------------
#---------------------------------------------------------------------------



# ----------------------------------------------------------------
# Class used to store values and functions used by main
# ----------------------------------------------------------------





class WebCrawler(object):
        def __init__(self, url_downloaded_queue, need_to_download_queue, download_manifest):
                self.url_downloaded_queue=url_downloaded_queue
                self.need_to_download_queue=need_to_download_queue
                self.download_manifest=download_manifest  
             
        #@timing #comment out to remove timing
        def func_download_page(self,passed_url):
        # open the URL
                try:
                        
                        page = urllib2.urlopen(passed_url).read()
                except:
                        print ('Error using urllib to read webpage at url', sys.exc_info()[0], sys.exc_info()[1])
                        return None
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
                                stripped_url = re.sub(tags,'',str(passed_url)) #remove html tags
                        except:
                                print ('Error stripping prefix with regex', sys.exc_info()[0], sys.exc_info()[1])
                
                        #remove punctuation from url to allow for writing to file in windows systems
                        try:
                                #stripped_url = stripped_url.translate(None, url_seed)
                                stripped_url = stripped_url.translate(None, string.punctuation)
                        except:
                                print ('Error removing punctuation from url', sys.exc_info()[0], sys.exc_info()[1])
                
                        try:
                                filename = str(cached_doc_path+stripped_url+'.htm')
                                #print('filename used to write file')
                                #print (filename)##for debugging
                                f= open(filename, "w")
                                f.write(page)
                                f.close
                        except:
                                print ('Error writing page to local file', sys.exc_info()[0], sys.exc_info()[1])
                        try:
                                self.url_downloaded_queue.append(passed_url)
                        except:
                                print ('Error updating url downloaded queue', sys.exc_info()[0], sys.exc_info()[1])
                        try:
                                if self.need_to_download_queue:#check if queue is empty
                                        self.need_to_download_queue.remove(passed_url)
                        except:
                                print ('Error removing url from need_to_download_queue', sys.exc_info()[0], sys.exc_info()[1])
                        ##Create a file to map URL to filename
                        try:
                                self.download_manifest[str(stripped_url+'.htm')]=str(passed_url)
                                #self.download_manifest[filename]=str(passed_url)
                                self.func_export_download_manifest_with_shelve()
                        except:
                                print ('Error adding url to download_manifest', sys.exc_info()[0], sys.exc_info()[1]) 
                                
                        #try:
                                #download_manifest = str(cached_doc_path+'download_manifest.txt')
                                #f= open(download_manifest, "a")
                                #f.write(str('filename:'+stripped_url+' url:'+passed_url+'\n'))
                                #f.close
                        #except:
                                #print ('Error writing to file to store url and filename', sys.exc_info()[0], sys.exc_info()[1])    
        
                                
                except:
                        print ('Error writing webpage to local file', sys.exc_info()[0], sys.exc_info()[1])
                return page
        
        #@timing #comment out to remove timing        
        def func_export_download_manifest_with_shelve(self):              
                print ('Exporting manifest to shelf .db file')
                try:   
                    d = shelve.open(cached_doc_path+'/download_manifest')
                    d['manifest'] = self.download_manifest
                    d.close()   
                except:
                    print ('Error exporting data via shelve', sys.exc_info()[0], sys.exc_info()[1])                                 
        
        
        def func_get_robots_txt(self):
                try:
                        robo_url=str(url_seed+'robots.txt')
                        robots = urllib2.urlopen(robo_url).read()
                        robots=robots.split()#splitwords into array
                        print ('printing robots')
                        print (robots)
                        return robots
                except:
                        print ('Error parsing robots.txt', sys.exc_info()[0], sys.exc_info()[1])
                        return None
        
        def func_find_urls_on_page(self,page):
                try:
                        words=[] #array to store each word in the web page
                        #url_queue=[]
                        words=page.split()#split page into words
                        try:
                                #print (page)
                                #url_match = re.compile('(.*?http\w+)',re.DOTALL)
                                #result = url_match.match(page)
                                #print (result)
                                #search words for href tag
                    
                                hyperlink_match = re.compile('(href=".*?")',re.DOTALL)#how to tell if a link
                                #hyperlink_match = re.compile('(?:href=")(.*?)(?:".*?)',re.DOTALL)#how to tell if a link
                                hyperlink_ignore = re.compile('(.*?.css.*?)|(.*?javascript.*?)|(.*?#.*?)|(.*?mailto.*?)|(.*?.jpg)|(.*?.png)|(.*?.amp)|(.*?.bmp)|(.*?.mp3)|(.*?.mp4)|(.*?.avi)|(.*?.gif)|(.*?.pdf)',re.DOTALL)#links to ignore, such as .css
                                #hyperlink_clean = re.compile('(href=")|(".*?$)|(>.*?)|(<.*?)|(.*?\s+.*?)',re.DOTALL)
                                hyperlink_clean = re.compile('(href=")|(".*?$)',re.DOTALL)#sanitize href and root links
                                for word in words:
                                    #try:
                                        #if word not in robots_txt:# check robots.txt
                                                try:
                                                        if hyperlink_match.match(word): #check that the word contains "hfref=
                                                                try:
                                                                        if not hyperlink_ignore.match(word): #check list of hrefs to ignore such as .css or javascript
                                                                                word = re.sub(hyperlink_clean,'',str(word))
                                                                                try:     
                                                                                        if 'http://' in word: #check to see if the link is an absolute link
                                                                                                if url_seed in word:#used to limit search to same website
                                                                                                        if word not in self.url_downloaded_queue: #check to see that the URL has not already been downloaded
                                                                                                                if word not in self.need_to_download_queue: #check that url is not already in the need to download queue
                                                                                                                        self.need_to_download_queue.append(str(word))  
                                                                                                                else:
                                                                                                                        return None
                                                                                                    
                                                                                        elif '../' in word: #check if relative link
                                                                                                word=str(url_seed+word)#append current url_seed to directory traversal
                                                                                                if url_seed in word:#used to limit search to same website
                                                                                                        if word not in self.url_downloaded_queue: #check to see that the URL has not already been downloaded
                                                                                                                if word not in self.need_to_download_queue: #check that url is not already in the need to download queue
                                                                                                                        self.need_to_download_queue.append(str(word))                    
                                                                                        elif 'https://' in word: #check to see if the link is an absolute link with https
                                                                                                if url_seed in word:#used to limit search to same website
                                                                                                        if word not in self.url_downloaded_queue: #check to see that the URL has not already been downloaded
                                                                                                                if word not in self.need_to_download_queue: #check that url is not already in the need to download queue
                                                                                                                        self.need_to_download_queue.append(str(word))                                                              
                                                                                        #elif word is '/':
                                                                                            #print ('word is just /')
                                                                                        else: #print word  
                                                                                                word = str(url_seed+word)
                                                                                                if url_seed in word:#used to limit search to same website
                                                                                                        if word not in self.url_downloaded_queue: #check to see that the URL has not already been downloaded
                                                                                                                if word not in self.need_to_download_queue: #check that url is not already in the need to download queue 
                                                                                                                        self.need_to_download_queue.append(word)
                                                                                except:
                                                                                        print ('Error differentiating between remaining url types', sys.exc_info()[0], sys.exc_info()[1])
                                                                except:
                                                                        print ('Error with ignore regex', sys.exc_info()[0], sys.exc_info()[1])
                                                except:
                                                        print ('Error matching hyperlink regex', sys.exc_info()[0], sys.exc_info()[1])
                                    #print url_queue
                                    
                                
                             
                                   #except:
                                    #    print ('Error in checking robots.txt', sys.exc_info()[0], sys.exc_info()[1])
                        except:
                                print ('Error in regex', sys.exc_info()[0], sys.exc_info()[1])
                            #return url_queue
                except:
                        print ('Error finding urls', sys.exc_info()[0], sys.exc_info()[1])

          


# Begin program

# This section of code will provide a brief introductory message and instructions of using the program
#print ("Welcome to the EECS767 web crawling")
#func_download_page(url)

#url_downloaded_queue=[]
#need_to_download_queue=[]

#-------------------------------------------------------------
# The Main Program
#
#----------------------------------------------------------

@timing #comment out to remove timing
def main():
        print ("Welcome to the EECS767 web crawling program!")
        crawler=WebCrawler([],[],{})
        #crawler.func_get_robots_txt()
        
        crawler.func_find_urls_on_page(crawler.func_download_page(url))
        print ('queue of urls to download:')
        print (crawler.need_to_download_queue)
        print ('Urls that have been downloaded:')
        print (crawler.url_downloaded_queue)
        #Process urls in url_to_download queue
        
        
        while crawler.need_to_download_queue:
                for url_to_download in crawler.need_to_download_queue:
                        #create a new thread for each URL
                        thread=threading.Thread(target=download_page_thread(url_to_download,crawler))       
        crawler.func_export_download_manifest_with_shelve()
        print ('Program complete!')
if __name__ == "__main__":    
        main()