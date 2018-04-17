#!/usr/bin/python3
import cgi
import os
import time
import sys
import time
import math
from query import *

#from http import cookies 
#https://docs.python.org/3/library/http.cookies.html

## No deprecation between Python 3 and 2.. just to be sure - we only
## run on python 3.5 - tell the end user that if trying to run on the
## wrong version...
ver = sys.version_info
if ver.major != 3 or ver.minor != 5:
        print('Content-Type: text/html\r\n\r\n')
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
        numresults = 10                         # Number of results per page

        ## Parse the incoming query
        form = cgi.FieldStorage()
        query = form.getvalue("query", "")      # The current query
        relID = form.getvalue("did", "")        # The relevant doc ID
        queryVector = form.getvalue("que", "")  # The current query vector
        page = form.getvalue("page", 0)         # The current page

        page = int(page)

        ## If page coming in, number is human not index - need to fix
        if page > 0:
                page -= 1
        
        ## Let's see how long it takes...
        t0 = time.time()

        ## Only work on the query if we're passed something
        if query != "":
                ## Build the query
                queryInstance = similarity('processingOutput.db','processingArtifacts.db')
                #tokenizedQuery = queryInstance.tokenizeQuery("truck arrived of")
                tokenizedQuery = queryInstance.tokenizeQuery(query)
                normalizedQuery = queryInstance.normalizeQuery(tokenizedQuery)
                ## If at least one term from query found in corpus
                if normalizedQuery:
                        ## Search corpus
                        queryInstance.similarity(normalizedQuery)
                        queryInstance.proximity(tokenizedQuery)      
                queryInstance.writeOutput('queryOutput')
                        

        ## How did we do on timing
        t1 = time.time()
        exe = str(float("{0:.3f}".format(t1-t0))) + " sec"
        
        ## Get the results
        if query != "":
                ans = queryInstance.rankedOutput # results and rank
                que = queryInstance.queryVector  # query vector
                ques = ':'.join(map(str,que))    # query vector as a string
                res = ans[0]                     # results
                ran = ans[1]                     # ranks
        else:
                res = []
                ans = []

        ## Figure out the page count
        i = page * numresults
        stop = i + numresults

        print("Content-type: text/html")
        print()
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
                                height: 50px;
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
                                height: 50px;
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
        """)
        print( """
                        <div id="search">
                                <form method="post" action="search.cgi">
                                        <input type="text" name="query" value="%s"/>
                                        <input type="submit" name="submit" value="Go"/>
                                </form>
                                <p>Found %s results (%s)</p>
                                <p>Showing page %s of %s page(s)</p>
                        </div>
                        <div id="results">
        """ % (cgi.escape(query), len(res), exe, page+1, math.ceil(len(res)/numresults)))

        # k and (res[i]) = result filename
        # relURL = link w/ doc id and query vector parameters
        # res[i][k][2] = result link
        # ran[i] = result rank
        # ??? = result title
        while i < len(res) and i < stop:
                ## Get the filename
                k = next(iter(res[i]))

                ## Can't use the URI as the query vector is too large...
                ## going to post as form
                ## Each entry is a tiny form
                print( """
                        <form method="post" action="search.cgi">
                                <input type="hidden" name="query" value="%s" />
                                <input type="hidden" name="que" value="%s" />
                """ % (query, str(ques)))

                relURL = """
                        <input type='hidden' name='did' value='%s'/>
                """ % str(res[i][k][0])

                print( """
                        <p>
                                <p class="title">%s. %s %s
                                (<input type="submit" name="rel" value="More Like This" />)</p>
                                <p class="link"><a href="#">%s</a></p>
                                <p class="rank">Ranking: %s</p>
                                <p class="summary">%s</p>
                        </p>
                        </form>
                """ % (i+1, k, relURL, res[i][k][2], ran[i], 'unknown'))
                
                i += 1
                if i < len(res):
                        print( """
                                <p class="blank">
                                &nbsp;
                                </p>
                        """)

        p = 1
        link = '<p align="center"> Page: '

        ## Make sure we're passing back to the same page
        print( """
                
                <form method="post" action="search.cgi">
                        <input type="hidden" name="query" value="%s" />
        """ % (query))

        while p <= math.ceil(len(res)/numresults):
                if p-1 != page:
                        #link += "<a href='" + relURL + "&page=" + str(p) + "'>"+str(p)+"</a> "
                        link += "<input type='submit' name='page' value='" + str(p) + "'/>\n"
                else:
                        link += " " + str(p) + "\n "
                p += 1

        ## If no query - no pages...
        if query != "":
                print( link+"</p>\n</form>" )

        print( """
                        <br /><br /><br /><br />
                        <br /><br /><br /><br />
                        <br /><br /><br /><br />
                        </div>
                        <div id="footer">
                                <p>Spring 2018 &middot;
                                EECS 767, Information Retrieval &middot;
                                Blake Bryant, Nidhi Midha, Ron Andrews</p>
                        </div>
                </body>
        </html>
        """)
