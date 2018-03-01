#!/usr/bin/python
import cgi
import os
import time
#from http import cookies 
#https://docs.python.org/3/library/http.cookies.html

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

form = cgi.FieldStorage()
query = form.getvalue("query", "(no query)")

print( """
		<div id="search">
			<form method="post" action="search.cgi">
				<input type="text" name="query" value="%s"/>
			</form>
			<p>Found ... results (x.xx seconds)</p>
		</div>
		<div id="results">
""" % cgi.escape(query))

results = [
	[ "doc1", "link", "rank", "summary" ],
	[ "doc2", "link", "rank", "summary" ],
	[ "doc3", "link", "rank", "summary" ],
	[ "doc4", "link", "rank", "summary" ],
	[ "doc5", "link", "rank", "summary" ],
	]

i = 0
while i < len(results):
	print( """
		<p>
			<p class="title">%s</p>
			<p class="link"><a href="#">%s</a></p>
			<p class="rank">Ranking: %s</p>
			<p class="summary">%s</p>
		</p>
	""" % (results[i][0], results[i][1], results[i][2], results[i][3]))
	i += 1
	if i < len(results):
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
