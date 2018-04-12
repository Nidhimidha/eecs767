#!/usr/bin/python3
import cgi
import os
import time
import sys
import time
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
        ## Parse the incoming query
        form = cgi.FieldStorage()
        query = form.getvalue("query", "")
        relID = form.getvalue("did", "")
        queryVector = form.getvalue("que", "")

        ## Let's see how long it takes...
        t0 = time.time()

        ## Build the query
        queryInstance = similarity('processingOutput.db')
        #tokenizedQuery = queryInstance.tokenizeQuery("truck arrived of")
        tokenizedQuery = queryInstance.tokenizeQuery(query)
        normalizedQuery = queryInstance.normalizeQuery(tokenizedQuery)

        ## Search corpus
        queryInstance.similarity(normalizedQuery)
        queryInstance.proximity(tokenizedQuery)

        ## How did we do on timing
        t1 = time.time()
        exe = str(float("{0:.3f}".format(t1-t0))) + " sec"
        
        ## Get the results
        ans = queryInstance.rankedOutput # results and rank
        que = queryInstance.queryVector  # query vector
        ques = ':'.join(map(str,que))    # query vector as a string
        res = ans[0]                     # results
        ran = ans[1]                     # ranks

        print("Content-type: text/html")
        print()
        print("""
        <html>
                <meta charset="utf-8" />
                <title>FiniteLoop Squad Search</title>
                <style>
                        body {
                                font: normal 10px/.75 helvetica;
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
                        #search input {
                                width: 200px;
                        }
                        #results {
                                position: absolute;
                                top: 125px;
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
                                <form method="post" action="cgi-bin/search.cgi">
                                        <input type="text" name="query" />
                                </form>
""")
        
        print( """
                        <div id="search">
                                <form method="post" action="search.cgi">
                                        <input type="text" name="query" value="%s"/>
                                </form>
                                <p>Found %s results (%s)</p>
                        </div>
                        <div id="results">
        """ % (cgi.escape(query), len(res), exe))

        i = 0

        # k and (res[i]) = result filename
        # relURL = link w/ doc id and query vector parameters
        # res[i][k][2] = result link
        # ran[i] = result rank
        # ??? = result title
        while i < len(res):
                ## Get the filename
                k = next(iter(res[i]))

                ## Build the relevance link
                relURL = 'search.cgi?'
                relURL += 'did='+str(res[i][k][0])+'&'
                relURL += 'que='+str(ques)+'&'
                relURL += 'query='+query
                print( """
                        <p>
                                <p class="title">%s
                                        <a href="%s">
                                                <i><small>More Like This</small></i>
                                        </a>
                                </p>
                                <p class="link"><a href="#">%s</a></p>
                                <p class="rank">Ranking: %s</p>
                                <p class="summary">%s</p>
                        </p>
                """ % (k, relURL, res[i][k][2], ran[i], 'unknown'))
                
                i += 1
                if i < len(res):
                        print( """
                                <p class="blank">
                                &nbsp;
                                </p>
                        """)

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
