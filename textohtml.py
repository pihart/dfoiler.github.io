import os			# path, chdir, listdir, mkdir

# Get absolute path
PATH = os.path.abspath(__file__)
PATH = PATH[:-PATH[::-1].index('/')]
os.chdir(PATH)

# Extra stuff to make the HTML file
header = open('header.html').read()
pre = open('pre.tex').read()

def to_html(tex):
	# We get this out of the way
	tex = tex.replace('``','"')
	tex = tex.replace('<',' \\lt ')
	tex = tex.replace('>',' \\gt ')
	# Now we work line-by-line
	tex = tex.split('\n')
	html = header
	html += '<body>\n'
	html += '<h1>Today I Learned</h1>\n'
	# We work line-by-line
	# I use many of my own TeX conventions for this
	# I.e., this is not general purpose and will not work for your TeX
	for line in tex:
		# A starting line
		if '\\subsubsection' in line:
			h2 = line[len('\\subsubsection{'):-len('}')]
			html += '<h2>'+h2+'</h2>\n'
			# We attach the preamble here
			html += '<p>$'+pre+'$'
			print(h2)
			day = h2.split()[1][:-len('th')]
		# Two consecutive new lines implies new paragraph
		elif line == '':
			html += '</p>\n<p>'
		# Various list commands
		elif '\\begin{itemize}' in line:
			html += '</p>\n<ul>'
		elif '\\end{itemize}' in line:
			html += '</ul>\n<p>'
		elif '\\begin{enumerate}' in line:
			html += '</p>\n<ol>'
		elif '\\end{enumerate}' in line:
			html += '</ol>\n<p>'
		elif '\\item' in line:
			line = line.replace('\\item','')
			html += '<li>'+line+'</li>'
		# Catch-all
		else:
			html += line
	html += '\n</p>\n</body>'
	return html
	# TODO: do something about images

# Make TIL folder if not present
if 'TIL' not in os.listdir():
	os.mkdir('TIL')

# Iterate through the TeX files
for year in os.listdir('TeX'):
	# Make year if not there
	if year not in os.listdir('TIL'):
		os.mkdir('TIL/'+year)
	for month in os.listdir(PATH+'TeX/'+year):
		# Make month if not there
		month = month[:-len('.tex')]
		if month not in os.listdir('TIL/'+year):
			os.mkdir('TIL/'+year+'/'+month)
		# Break up the months into days
		alltex = open(PATH+'TeX/'+year+'/'+month+'.tex').read()
		# We start with a section line, so the first is useless
		for tex in alltex.split('\\subsubsection')[1:]:
			tex = '\\subsubsection'+tex
			# Push through helper and make the file
			html = to_html(tex)
			# Extract day from the starting subsection line
			day = tex[:tex.index('}')].split()[1][:-len('th')]
			f = open(PATH+'TIL/'+year+'/'+month+'/'+day+'.html','w')
			f.write(html)
			f.close()
