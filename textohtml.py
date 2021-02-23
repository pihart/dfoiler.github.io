import sys			# argv
import os			# path, chdir, listdir, mkdir

# Get absolute path
PATH = os.path.abspath(__file__)
PATH = PATH[:-PATH[::-1].index('/')]
os.chdir(PATH)

# standalone is for making tikz images
standalone = open('standalone.sty').read()
# Generating our header
header = '''<!DOCTYPE html>
<html>
	<head>
		<title>Today I Learned</title>
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto">
		<link rel="stylesheet" href="https://dfoiler.github.io/css/main.css">
		<link rel="stylesheet" href="https://dfoiler.github.io/css/sidebar.css">
		<link rel=icon href="https://dfoiler.github.io/p.ico">
		<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
		<script src="https://dfoiler.github.io/js/mathjax-config.js"></script>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.0/MathJax.js?config=TeX-AMS_SVG-full"></script>
	</head>\n'''

# Dirty hack to get the month
months = ['January','February','March','April','May','April','June'
	'July','August','September','October','November','December']

# Generating the archive
archive = ''
for year in next(os.walk('TeX'))[1]:
	year_months = sorted([int(m[:-len('.tex')]) for m in os.listdir('TeX/'+year)])
	archive += '{0}<button class="yearmenu">'+year+'</button>\n'
	archive += '{0}<ul class="monthmenu">\n'
	for month in year_months:
		directory = year + '/'+str(month)
		title = months[month-1] + ' ' + year
		archive += '{0}\t<li><span><a href="https://dfoiler.github.io/TIL/' \
			+directory+'/">'+title+'</a></span></li>\n'
	archive += '{0}</ul>\n'

indent = lambda n : (0)*'\t'
def start_html(level):
	html = header
	html += '\t<body>\n'
	html += '\t\t<h1 class="title"><a href="https://dfoiler.github.io/TIL/"' \
		' class="title">Today I Learned</a></h1>\n'
	html += '\t\t<div class="container">\n'
	# Add in the archive sidebar
	html += '\t\t\t<div class="sidebar">\n'
	html += '\t\t\t\t<p style="text-align: center; font-weight: bold; '\
		'margin-top: 5px;">Archive</p>\n'
	html += archive.format(indent(0))
	html += '\t\t\t</div>\n'
	html += '\t\t\t<div class="content">\n'
	return html

def prettify(html):
	html = html.replace('\n','').replace('\t','')
	content = []
	for c in html:
		if c == '<':
			content += ['<']
		elif c == '>':
			content[-1] += '>'
			content += ['']
		else:
			# We want to put the tag type right after <
			if not(content[-1] == '<' and c==' '):
				content[-1] += c
	content = [c.strip() for c in content if c]
	level = 0
	no_close = ['</','<img','<!','<link','<meta']
	html = ''
	for c in content:
		if '</' in c:
			level -= 1		
		html += level*'\t' + c + '\n'
		if '<' in c and not any(n in c for n in no_close):
			level += 1
	return html

def end_html(level):
	html = '\t\t\t</div>\n'
	html += '\t\t</div>\n'
	html += '\t\t<script src="https://dfoiler.github.io/js/sidebar.js"></script>\n'
	html += '\t</body>\n'
	html += '</html>\n'
	return html

no_images = '-noimg' in sys.argv
def process_img(tex):
	# Remember we are in the day's directory right now
	# This makes latex and asy behave somewhat
	# My images are always centered, so we split by centers
	parts = tex.split('\\begin{center}')
	tex = parts[0]
	if len(parts) == 1:
		return tex
	for i in range(1,len(parts)):
		# We don't want the center tags
		img = parts[i][:parts[i].index('\\end{center}')]
		# For convenience, we treat asy and tikz separately
		filename = 'img'+str(i)
		if '\\begin{tikz' in img and not no_images:
			print('processing tikz: ' + str(i) + '/' + str(len(parts)-1))
			# Generate file
			img = '\\documentclass[convert={density=500}]{standalone}\n' \
				+standalone+'\\begin{document}'+img+'\n\end{document}'
			f = open(filename+'.tex', 'w')
			f.write(img)
			f.close()
			# Compile; this hangs on error
			os.system('latex -shell-escape '+filename+'.tex > /dev/null 2>&1')
		elif '\\begin{asy}' in img and not no_images:
			print('processing asy : ' + str(i) + '/' + str(len(parts)-1))
			# Generate file
			img = 'settings.outformat = "png";\nsettings.render=5;\n'+img
			img = img.replace('\\begin{asy}','')
			img = img.replace('\\end{asy}','')
			f = open(filename+'.asy', 'w')
			f.write(img)
			f.close()
			# Compile
			os.system('asy '+filename+'.asy')
		# We put a marker here to denote the image
		tex += '\00'+filename+'.png'
		tex += parts[i][parts[i].index('\\end{center}')+len('\\end{center}'):]
	# Clean
	for filename in os.listdir():
		if filename.split('.')[-1] in ['asy','aux','dvi','log','tex','ps','pdf']:
			os.remove(filename)
	return tex

def process_tex(tex):
	# We process images first, which is difficult
	tex = process_img(tex)
	# Fix TeX hacks for HTML
	tex = tex.replace('``','"')
	tex = tex.replace('---','&mdash;')
	tex = tex.replace('--','&ndash;')
	# Fix < and > signs for HTML
	tex = tex.replace('<','{\\lt}')
	tex = tex.replace('>','{\\gt}')
	# We process \href manually
	parts = tex.split('\\href')
	tex = parts[0]
	if len(parts) == 1:
		return tex
	# Skip the first part
	for part in parts[1:]:
		# Use should be \href{stuff}{stuff}
		link = part[part.index('{')+1:part.index('}')]
		tex += '<a href="'+link+'">'
		part = part[part.index('}')+1:]
		name = part[part.index('{')+1:part.index('}')]
		tex += name + '</a>'
		part = part[part.index('}')+1:]
		tex += part
	return tex

def get_blurb(tex):
	blurb = tex[tex.index('Today I '):]
	# Look for the end of the sentence
	for end in range(len(blurb)):
		if blurb[end:end+2] in ['. ','.\n','.$']:
			blurb = blurb[:end+2]
		elif blurb[end:end+3] in ['.\\]']:
			blurb = blurb[:end+3]
	blurb = blurb[:end].strip()
	return blurb

# TODO: make a last_tag stack for more memory
# TODO: make each list item start a paragraph
def process_line(line, i, last_tags, first_item):
	to_add = ''
	close = last_tags[-1] != '' and not first_item
	new_tags = []
	# Update ending indents now
	environs = ['itemize','enumerate']
	# Consecutive lines implies a new paragraph
	if line == '':
		to_add += indent(i)+'<p>'
		new_tags = ['p']
	# Various list commands
	elif '\\begin{itemize}' in line:
		to_add += indent(i)+'<ul>\n'+indent(i+1)+'<li>'
		new_tags = ['ul','li']
	elif '\\end{itemize}' in line:
		to_add += indent(i-1)+'</ul>\n'
	elif '\\begin{enumerate}' in line:
		to_add += indent(i)+'<ol>\n'+indent(i+1)+'<li>'
		new_tags = ['ol','li']
	elif '\\end{enumerate}' in line:
		to_add += indent(i-1)+'</ol>\n'
		first_item =  False
	elif '\\item' in line:
		line = line.replace('\\item','')
		if not first_item:
			to_add += indent(i)+'<li>'
			new_tags = ['li']
		to_add += line
		first_item = False
	# Image marker
	elif line[0] == '\00':
		filename = line[1:]
		to_add += indent(i)+'<img src="'+filename+'">\n'
	# Catch-all
	else:
		close = False
		if last_tags[-1] == '':
			to_add += indent(i)+'<p>'
			new_tags = ['p']
		to_add += line
	# Update beginning indents later
	if any('\\begin{'+env in line for env in environs):
		i += 1
		first_item = True
		# Close if we're coming from a paragraph
		close = last_tags[-1] == 'p'
		if not close:
			to_add = '\n'+to_add
	# Add in the closing
	if close:
		to_add = '</'+last_tags.pop()+'>\n'+to_add
	if any('\\end{'+env in line for env in environs):
		i -= 1
		last_tags.pop()
	last_tags += new_tags
	return to_add, i, last_tags, first_item

def to_html(tex):
	# This is not general-purpose and will not work with your TeX
	# Preprocess
	tex = process_tex(tex)
	# Extract the blurb
	blurb = get_blurb(tex)
	# Now we work line-by-line
	tex = tex.split('\n')
	while tex[-1] == '': tex = tex[:-1]
	day_html = start_html(4)
	month_html = indent(0)+'<div class="entry">\n'
	# We work line-by-line
	first_item = False
	# Indents
	i = 1
	last_tags = ['']
	for line in tex:
		# A starting line
		if '\\subsubsection' in line:
			h2 = line[len('\\subsubsection{'):-len('}')]
			month, day = h2.split()
			day_html += indent(0)+'<p class="mobilenav"><a href="../" class="link">' \
				'(back up to '+month+')</a></p>\n'
			day_html += indent(0)+'<div class="entry">\n'
			day_html += indent(1)+'<h2>'+h2+'</h2>\n'
			day = day[:-len('th')]
			month_html += indent(1)+'<h3><a href="'+day+'/">'+h2+'</a></h3>\n'
			# Go ahead and start the first paragraph
		else:
			try:
				to_add, i, last_tags, first_item = \
					process_line(line, i, last_tags, first_item)
			except:
				print(day_html)
				print(0/0)
			day_html += to_add
	if last_tags[-1]:
		day_html += '</'+last_tags[-1]+'>\n'
	day_html += indent(0)+'</div>\n' + end_html(4)
	month_html += indent(1)+'<p>'+blurb+'\n'
	month_html += indent(1)+'<a href="'+day+'/" class="link">(continue reading...)</a></p>\n'
	month_html += indent(0)+'</div>\n'
	return day_html, month_html

# Make TIL folder if not present
if 'TIL' not in os.listdir():
	os.mkdir('TIL')

# Start the total file
total_html = start_html(1)
# Add in the intro
total_html += indent(0)+'<h2>Welcome</h2>\n'
intro = process_tex(open('TeX/intro.tex').read())
parts = [part for part in intro.split('\n') if part]
for part in parts:
	total_html += indent(0)+'<p>'+part+'</p>\n'
# Mobile navigation
total_html += indent(0)+'<div class="mobilenav">\n'
total_html += indent(1)+'<h2 style="margin-top: 8pt">Archive</h2>\n'
total_html += indent(1)+'<p>You can navigate to an entry from the archive below.</p>\n'
total_html += archive.format(indent(1))
# Some padding
total_html += indent(1)+'<div style="height: 6pt;"></div>\n'
total_html += indent(0)+'</div>\n'
total_html += indent(0)+'<div style="height: 7pt;"></div>\n'
total_html += end_html(1)
# Make the total file
f = open('TIL/index.html','w')
f.write(prettify(total_html))
f.close()

# Iterate through the years subdirectories
for year in next(os.walk('TeX'))[1]:
	# Start the year file
	year_html = start_html(2)
	year_html += indent(0)+'<p class="mobilenav"><a href="../" class="link">' \
		'(back up to main page) </a></p>\n'
	year_html += indent(0)+'<h2><a href="./">'+year+'</a></h2>\n'
	# Make year if not there
	if year not in next(os.walk('TeX'))[1]:
		os.mkdir('TIL/'+year)
	# Increment the total file
	year_months = sorted(os.listdir('TeX/'+year), key=lambda m:int(m[:-len('.tex')]))
	for month in year_months:
		# Make month if not there
		month = month[:-len('.tex')]
		if month not in os.listdir('TIL/'+year):
			os.mkdir('TIL/'+year+'/'+month)
		# Start the month file
		month_html = start_html(3)
		month_html += indent(0)+'<p class="mobilenav"><a href="../../" class="link">' \
			'(back up to main page)</a></p>\n'
		month_html += indent(0)+'<h2>' + months[int(month)-1] + ' '+year+'</h2>\n'
		# Increment the year file
		year_html += indent(0)+'<h3><a href="'+month+'/">'+ \
			months[int(month)-1] +'</a></h3>\n'
		# Break up the months into days
		alltex = open(PATH+'TeX/'+year+'/'+month+'.tex').read()
		# We start with a section line, so the first is useless
		for tex in alltex.split('\\subsubsection')[1:]:
			tex = '\\subsubsection'+tex
			# Push through helper and make the file
			day = tex[:tex.index('}')].split()[1][:-len('th')]
			directory = 'TIL/'+year+'/'+month+'/'+day+'/'
			if day not in os.listdir('TIL/'+year+'/'+month):
				os.mkdir(directory)
			print('processing '+directory)
			# We work in this directory for now
			os.chdir(directory)
			day_html, month_html_day = to_html(tex)
			os.chdir(PATH)
			# Extract day from the starting subsection line
			f = open(directory+'index.html','w')
			f.write(prettify(day_html))
			f.close()
			# Add onto the month
			month_html += month_html_day
		month_html += end_html(3)
		# Make the month file
		f = open('TIL/'+year+'/'+month+'/'+'index.html','w')
		f.write(prettify(month_html))
		f.close()
	# Some padding
	year_html += indent(0)+'<div style="height: 6pt;"></div>\n'
	year_html += end_html(2)
	# Make the year file
	f = open('TIL/'+year+'/index.html','w')
	f.write(prettify(year_html))
	f.close()
