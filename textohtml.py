import os			# path, chdir, listdir, mkdir

# Get absolute path
PATH = os.path.abspath(__file__)
PATH = PATH[:-PATH[::-1].index('/')]
os.chdir(PATH)

# Extra stuff to make the HTML file
pre = '$'+open('pre.tex').read()+'$'
# This occurs at varying levels, so we make a function for it
def header(level):
	return '''<!DOCTYPE html>
<html>
	<head>
		<title>Today I Learned</title>
		<link rel="stylesheet" href="'''+'../'*level+'''main.css">
		<!-- https://tex.stackexchange.com/questions/27633/mathjax-inline-mode-not-rendering -->
		<script type="text/x-mathjax-config">
			MathJax.Hub.Config({
				tex2jax: {
					inlineMath: [ ['$','$'] ],
					processEscapes: true
				}
			});
		</script>
		<script src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML" type="text/javascript"></script>
	</head>\n'''

def start_html(level):
	html = header(level)
	html += '\t<body>\n'
	html += '\t\t<h1><a href="'+ '../'*(level-1) +'index.html">Today I Learned</a></h1>\n'
	return html

def process_tex(tex):
	tex = tex.replace('``','"')
	tex = tex.replace('<','\\lt')
	tex = tex.replace('>','\\gt')
	return tex

def get_blurb(tex):
	blurb = tex[tex.index('Today I '):]
	for end in range(len(blurb)):
		if blurb[end:end+2] in ['. ','.\n','.$']:
			blurb = blurb[:end+2]
		elif blurb[end:end+3] in ['.\\]']:
			blurb = blurb[:end+3]
	blurb = blurb[:end].strip()
	return blurb

def to_html(tex):
	# Preprocess
	tex = process_tex(tex)
	# Extract the blurb
	blurb = get_blurb(tex)
	# Now we work line-by-line
	tex = tex.split('\n')
	day_html = start_html(3)
	month_html = ''
	# We work line-by-line
	# I use many of my own TeX conventions for this
	# I.e., this is not general purpose and will not work for your TeX
	for line in tex:
		# A starting line
		if '\\subsubsection' in line:
			h2 = line[len('\\subsubsection{'):-len('}')]
			h3 = h2.split()
			month = h3[0]
			day = h3[1]
			day_html += '\t\t<h2><a href="./index.html">'+month+'</a> '+day+'</h2>\n'
			day = day[:-len('th')]
			month_html += '\t\t<h3><a href="'+day+'.html">'+h2+'</a></h3>\n'
			# We attach the ipreamble here
			day_html += '\t\t<p>'+pre
		# Two consecutive new lines implies new paragraph
		elif line == '':
			day_html += '</p>\n\t\t<p>'
		# Various list commands
		elif '\\begin{itemize}' in line:
			day_html += '\t\t</p>\n\t\t<ul>'
		elif '\\end{itemize}' in line:
			day_html += '\t\t</ul>\n\t\t<p>'
		elif '\\begin{enumerate}' in line:
			day_html += '\t\t</p>\n\t\t<ol>'
		elif '\\end{enumerate}' in line:
			day_html += '\t\t</ol>\n\t\t<p>'
		elif '\\item' in line:
			line = line.replace('\\item','')
			day_html += '\n\t\t\t<li>'+line+'</li>'
		# Catch-all
		else:
			day_html += line
	day_html += '</p>\n\t</body>\n</html>'
	month_html += '\t\t<p>'+blurb+'</p>\n'
	return day_html, month_html
	# TODO: do something about images

# Make TIL folder if not present
if 'TIL' not in os.listdir():
	os.mkdir('TIL')

# Dirty hack to get the month
months = ['January','February','March','April','May','April','June'
	'July','August','September','October','November','December']

# Start the total file
total_html = start_html(1)
total_html += '\t\t<p>I\'m putting some stuff I learn here. Nothing to see.</p>\n'
# Iterate through the TeX files
for year in os.listdir('TeX'):
	# Start the year file
	year_html = start_html(2)
	year_html += '\t\t<h2><a href="./index.html">'+year+'</a></h2>\n'
	# Make year if not there
	if year not in os.listdir('TIL'):
		os.mkdir('TIL/'+year)
	# Increment the total file
	total_html += '\t\t<h2><a href="./'+year+'/index.html">'+year+'</a></h2>\n'
	for month in os.listdir(PATH+'TeX/'+year):
		# Make month if not there
		month = month[:-len('.tex')]
		if month not in os.listdir('TIL/'+year):
			os.mkdir('TIL/'+year+'/'+month)
		# Start the month file
		month_html = start_html(3)
		month_html += '\t\t<h2>'+pre+ months[int(month)-1] + \
			' <a href="../index.html">'+year+'</a></h2>\n'
		# Increment the year file
		year_html += '\t\t<h3><a href="./'+month+'/index.html">'+ \
			months[int(month)-1] +'</a></h3>\n'
		# Break up the months into days
		alltex = open(PATH+'TeX/'+year+'/'+month+'.tex').read()
		# We start with a section line, so the first is useless
		for tex in alltex.split('\\subsubsection')[1:]:
			tex = '\\subsubsection'+tex
			# Push through helper and make the file
			day_html, month_html_day = to_html(tex)
			# Extract day from the starting subsection line
			day = tex[:tex.index('}')].split()[1][:-len('th')]
			f = open('TIL/'+year+'/'+month+'/'+day+'.html','w')
			f.write(day_html)
			f.close()
			# Add onto the month
			month_html += month_html_day
		month_html += '\t</body>\n</html>'
		# Make the month file
		f = open('TIL/'+year+'/'+month+'/'+'index.html','w')
		f.write(month_html)
		f.close()
	year_html += '\t</body>\n</html>'
	# Make the year file
	f = open('TIL/'+year+'/index.html','w')
	f.write(year_html)
	f.close()
total_html += '\t</body>\n</html>'
# Make the total file
f = open('TIL/index.html','w')
f.write(total_html)
f.close()
