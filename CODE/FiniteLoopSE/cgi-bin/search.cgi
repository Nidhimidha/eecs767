#!/usr/bin/python3
import cgi
import os
import time
import sys
import time
import math
from query import *

## Configs
numresults = 10         # Number of results per page
cachedir = 'CACHE'      # relative directory where summary cache files are located

## Establish the page
print('Content-Type: text/html\r\n\r\n')

## No deprecation between Python 3 and 2.. just to be sure - we only
## run on python 3.5 - tell the end user that if trying to run on the
## wrong version...
ver = sys.version_info
if ver.major != 3 or ver.minor != 5:
        print("""
                <html><head><title>Error 500 :(</title></head><body>
                <br /><br /><br /><br />
                <center><h1>HTTP/1.1 500 Internal Server Error</h1>
                <br /><br /><br /><br />
                This server does not support Python version 3.5.x<br />
                Unfortunately, this is a problem and thus the result is<br />
                this page in lieu of a beautiful table of found results...
                </center></body></html>
        """)
else:
        ## Parse the incoming query
        form = cgi.FieldStorage()
        query = form.getvalue("query", "")      # The current query
        relID = form.getvalue("did", "")        # The relevant doc ID
        doProxy = form.getvalue("proxy", 0)     # Are we using the proximity ranking
        queryVector = form.getvalue("que", "")  # The current query vector
        page = form.getvalue("page", 0)         # The current page

        if doProxy:
                doProxy = 'checked'
        else:
                doProxy = ''

        page = int(page)

        print("""

        <html>
                <meta charset="utf-8" />
                <title>FiniteLoop Squad Search</title>
                <style>
                        body {
                                font: normal 12px/.75 helvetica;
                        }
                        #header {
                                position: fixed;
                                top: 0px;
                                left: 0px;
                                width: 100%;
                                height: 40px;
                                background: steelblue;
                        }
                        #header h1 {
                                margin: 15px;
                                padding: 0;
                                color: white;
                        }
                        #header a {
                                text-decoration: none;
                        }
                        #search {
                                margin: 0 auto;
                                margin-top: 50px;
                                border: 2px dash black;
                                width: 100%;
                                height: 25px;
                                text-align: center;
                        }
                        #search input[type=text] {
                                width: 200px;
                        }
                        input[type=submit] {
                                background: none;
                                border: none;
                                font-size: xx-small;
                                padding: 0;
                                margin: 0;
                                display: inline;
                                color: blue;
                                text-decoration: underline;
                        }
                        #search input[type=submit] {
                                padding:2px 5px; 
                                background:#ccc; 
                                border:0 none;
                                cursor:pointer;
                                -webkit-border-radius: 5px;
                                border-radius: 5px; 
                                color: black;
                                text-decoration: none;
                        }
                        input[name=page] {
                                border: none;
                                font-size: 12px;
                                color: blue;
                                text-decoration: underline;
                        }
                        #results {
                                position: absolute;
                                top: 135px;
                                left: 0;
                                width: 100%;
                                background: #eee;
                        }
                        #results p {
                                padding-left: 10px;
                        }
                        #paging {
                                position: fixed;
                                background: #fff;
                                left: 0px;
                                bottom: 30px;
                                width: 100%;
                                height: 30px;
                        }
                        .blank {
                                background-color: #fff;
                        }
                        .title {
                                font-weight: bold;
                        }
                        .link {
                        }
                        .rank {
                                font-weight: italic;
                                color: gray;
                        }
                        .summary {
                        }
                        #footer {
                                position: fixed;
                                bottom: 0px;
                                left: 0px;
                                width: 100%;
                                height: 30px;
                                color: white;
                                text-align: center;
                                background: steelblue;
                        }
                </style>
                <body>
                        <div id="header">
                                <a href="../index.html"><h1>FiniteLoop Squad 
                                Search</h1></a>
                        </div>

        """ )
        print( """
                        <div id="search">
                                <form method="post" action="search.cgi">
                                        <input type="text" name="query" value="%s"/>
                                        <input type="submit" name="submit" value="Go"/>
                                        <br />
                                        <input type="checkbox" name="proxy" value="1" %s/>
                                        Include Proximity Ranking
                                </form>
        """ % (cgi.escape(query), doProxy))

        ## If page coming in, number is human not index - need to fix
        if page > 0:
                page -= 1
        
        ## Let's see how long it takes...
        t0 = time.time()

        ## FIXME: Just for now so we can run cmd line for debugging
        if query == "":
                query = 'silver'

        ## Only work on the query if we're passed something
        if query != "":
                ## Build the query
                queryInstance = similarity('processingOutput.db','processingArtifacts.db')
                tokenizedQuery = queryInstance.tokenizeQuery(query)
                normalizedQuery = queryInstance.normalizeQuery(tokenizedQuery)
                ## If at least one term from query found in corpus
                if normalizedQuery:
                        ## Search corpus
                        queryInstance.similarity(normalizedQuery)
                        if doProxy:
                                queryInstance.proximity()      
                queryInstance.writeOutput('queryOutput')
                        

        ## How did we do on timing
        t1 = time.time()
        exe = str(float("{0:.3f}".format(t1-t0))) + " sec"
        
        ## Get the results
        if query != "":
                ans = queryInstance.rankedOutput # results and rank
                if len(ans) == 2:
                        que = queryInstance.queryVector  # query vector
                        ques = ':'.join(map(str,que))    # query vector as a string
                        res = ans[0]                     # results
                        ran = ans[1]                     # ranks
                else:
                        res = []
                        ans = []
        else:
                res = []
                ans = []

        ## Figure out the page count
        i = page * numresults
        stop = i + numresults

        if len(res) > 0:
                print( """
                                <p>Found %s results (%s)</p>
                                <p>Showing page %s of %s page(s)</p>
                        </div>
                        <div id="results">
                """ % (len(res), exe, page+1, math.ceil(len(res)/numresults)))
        else:
                print( """
                                <p>There are no pages matching your query<br />
                                It took %s to realize this inevitability</p>
                        </div>
                        <div id="results">
                """ % (exe))

        # k and (res[i]) = result filename
        # relURL = link w/ doc id and query vector parameters
        # res[i][k][2] = result link
        # ran[i] = result rank
        # ??? = result title
        titles = queryInstance.titles

        while i < len(res) and i < stop:
                ## Need the filename
                resFname = k = next(iter(res[i]))

                ## Need the URL from the doc_key
                pURL = res[i][resFname][2]

                ## Need the page title from title_map
                if bool(titles): # returns true if the title_map is not empty
                        ptitle = titles[resFname][0]
                else:
                        ptitle = resFname # Title = filename...

                ## Need the summary - hopefully this won't kill us
                ## use the resFname(.db) to look up query in dictionary for summary text
                psum = ''
                if os.path.isfile(os.path.join(cachedir, resFname+'.db')):
                        ## Open the file
                        S = shelve.open(os.path.join(cachedir, resFname+'.db'))
                        sums = S['htmlText'][resFname]
                        ## Close the shelve file
                        S.close()
                        
                        ## Go through and pull each query term's summary, 
                        ##if it exists and concatenate
                        for x in query:
                                if x in sums:
                                        psum += sums[x] + ' &middot; '
                        if psum == '':
                                ## No exact matches, grab first sum
                                psum = sums[list(sums.keys())[0]] + ' &middot; '

                        ## Remove trailing middot
                        psum = psum[:-10]

                else:
                        psum = '<i>Details Unavailable</i>'

                ## Need the rank
                rank = ran[i]

                ## Can't use the URI as the query vector is too large...
                ## going to post as form
                ## Each entry is a tiny form
                print( """
                        <form method="post" action="search.cgi">
                                <input type="hidden" name="query" value="%s" />
                                <input type="hidden" name="que" value="%s" />
                """ % (query, str(ques)))

                ## Establish relevance feedback link - grab the document ID to pass back 
                pdocID = res[i][k][0]
                relURL = """
                        <input type='hidden' name='did' value='%s'/>
                """ % str(pdocID)

                print( """
                        <p>
                                <p class="title">%s. <a href="%s">%s</a> %s
                                (<input type="submit" name="rel" value="More Like This" />)</p>
                                <p class="rank">Ranking: %s</p>
                                <p class="summary">%s</p>
                        </p>
                        </form>
                """ % (i+1, pURL, ptitle, relURL, rank, psum))
                
                i += 1
                if i < len(res):
                        print( """
                                <p class="blank">
                                        <br /><br /><br />
                                        <br /><br /><br />
                                </p>
                        """)

        if len(res) > 0:
                p = 1
                link = '<p align="center"> Page: '

                ## Make sure we're passing back to the same page
                print( """
                        </div>
                        <div id="paging">
                        <form method="post" action="search.cgi">
                                <input type="hidden" name="query" value="%s" />
                """ % (query))
        
                while p <= math.ceil(len(res)/numresults):
                        if p-1 != page:
                                link += "<input type='submit' name='page' value='" + str(p) + "'/>\n"
                        else:
                                link += " " + str(p) + "\n "
                        p += 1

                print( link+"</p>\n</form>" )
        
        print( """
                        </div>
                        <div id="footer">
                                <p>Spring 2018 &middot;
                                EECS 767, Information Retrieval &middot;
                                Blake Bryant, Nidhi Midha, Ron Andrews</p>
                        </div>
                </body>
        </html>
        """)
