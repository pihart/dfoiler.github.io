import os			# path, chdir, listdir, mkdir

# Get absolute path
PATH = os.path.abspath(__file__)
PATH = PATH[:-PATH[::-1].index('/')]
os.chdir(PATH)

# standalone is for making tikz images
standalone = open('standalone.sty').read()
# This occurs at varying levels, so we make a function for it
def header(level):
	return '''<!DOCTYPE html>
<html>
	<head>
		<title>Today I Learned</title>
		<link rel="stylesheet" href="'''+'../'*level+'''main.css">
		<link rel="stylesheet" href="'''+'../'*level+'''sidebar.css">
		<link rel=icon href="'''+'../'*level+'''p.ico">
		<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
		<script src="'''+'../'*level+'''mathjax-config.js"></script>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.0/MathJax.js?config=TeX-AMS_SVG-full"></script>
	</head>\n'''

# Dirty hack to get the month
months = ['January','February','March','April','May','April','June'
	'July','August','September','October','November','December']

def gen_sidebar():
	r = '\t\t\t<div class="sidebar">\n'
	r += '\t\t\t\t<p style="text-align: center; font-weight: bold; '\
		'margin-top: 5px;">Archive</p>\n'
	for year in next(os.walk('TeX'))[1]:
		year_months = sorted([int(m[:-len('.tex')]) for m in os.listdir('TeX/'+year)])
		r += '\t\t\t\t<p class="yearmenu">'+year+'</p>\n'
		r += '\t\t\t\t<ul class="monthmenu">\n'
		for month in year_months:
			directory = year + '/'+str(month)
			title = months[month-1] + ' ' + year
			r += '\t\t\t\t\t<li><span><a href={0}' \
				+directory+'/>'+title+'</a></span></li>\n'
		r += '\t\t\t\t</ul>\n'
	r += '\t\t\t</div>\n'
	return r

sidebar_template = gen_sidebar()
def sidebar(level):
	return sidebar_template.format('../'*(level-1))

indent = lambda n : (4+n)*'\t'
def start_html(level):
	html = header(level)
	html += '\t<body>\n'
	html += '\t\t<h1 class="title"><a href="./'+ '../'*(level-1) + \
		'" class="title">Today I Learned</a></h1>\n'
	html += '\t\t<div class="container">\n'
	html += sidebar(level)
	html += '\t\t\t<div class="content">\n'
	return html

def end_html(level):
	html = '\t\t\t</div>\n'
	html += '\t\t</div>\n'
	html += '\t\t<script src="'+'../'*level+'sidebar.js"></script>\n'
	html += '\t</body>\n'
	html += '</html>\n'
	return html

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
		filename = ''
		if '\\begin{tikz' in img:
			print('processing tikz: ' + str(i) + '/' + str(len(parts)-1))
			filename = 'img'+str(i)
			# Generate file
			img = '\\documentclass[convert={density=500}]{standalone}\n' \
				+standalone+'\\begin{document}'+img+'\n\end{document}'
			f = open(filename+'.tex', 'w')
			f.write(img)
			f.close()
			# Compile; this hangs on error
			os.system('latex -shell-escape '+filename+'.tex > /dev/null 2>&1')
		elif '\\begin{asy}' in img:
			print('processing asy : ' + str(i) + '/' + str(len(parts)-1))
			filename = 'img'+str(i)
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
		if filename.split('.')[-1] in ['asy','tex','aux','dvi','log','ps','pdf']:
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
	for line in tex:
		# A starting line
		if '\\subsubsection' in line:
			h2 = line[len('\\subsubsection{'):-len('}')]
			month, day = h2.split()
			day_html += indent(0)+'<p class="back"><a href="../" class="link">' \
				'(back up to '+month+')</a></p>\n'
			day_html += indent(0)+'<div class="entry">\n'
			day_html += indent(1)+'<h2>'+h2+'</h2>\n'
			day = day[:-len('th')]
			month_html += indent(1)+'<h3><a href="'+day+'/">'+h2+'</a></h3>\n'
			# Go ahead and start the first paragraph
			day_html += indent(1)+'<p>'
		# Two consecutive new lines implies new paragraph
		elif line == '':
			day_html += '</p>\n'+indent(1)+'<p>'
		# Various list commands
		# We start the first item
		elif '\\begin{itemize}' in line:
			day_html += indent(1)+'</p>\n'+indent(1)+'<ul>\n'+indent(2)+'<li>'
			first_item = True
		elif '\\end{itemize}' in line:
			day_html += '</li>\n'+indent(1)+'</ul>\n'+indent(1)+'<p>'
		elif '\\begin{enumerate}' in line:
			day_html += indent(1)+'</p>\n'+indent(1)+'<ol>\n'+indent(2)+'<li>'
			first_item = True
		elif '\\end{enumerate}' in line:
			day_html += '</li>\n'+indent(1)+'</ol>\n'+indent(1)+'<p>'
		elif '\\item' in line:
			line = line.replace('\\item','')
			if not first_item:
				day_html += '</li>\n'+indent(2)+'<li>'
			first_item = False
			day_html += line
		# Image marker
		elif line[0] == '\00':
			filename = line[1:]
			day_html += '</p>\n'+indent(1)+'<img src="'+filename+'">\n'+indent(1)+'<p>'
		# Catch-all
		else:
			day_html += line
	day_html += '</p>\n'+indent(0)+'</div>\n' + end_html(4)
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
intro = process_tex(open('TeX/intro.tex').read())
parts = [part for part in intro.split('\n') if part]
for part in parts[:-1]:
	total_html += indent(0)+'<p>'+part+'</p>\n'
total_html += indent(0)+'<p style="margin-bottom: 18pt;">'+parts[-1]+'</p>\n'
# Iterate through the years subdirectories
for year in next(os.walk('TeX'))[1]:
	# Start the year file
	year_html = start_html(2)
	year_html += indent(0)+'<p class="back"><a href="../" class="link">' \
		'(back up to main page) </a></p>\n'
	year_html += indent(0)+'<h2><a href="./">'+year+'</a></h2>\n'
	# Make year if not there
	if year not in next(os.walk('TeX'))[1]:
		os.mkdir('TIL/'+year)
	# Increment the total file
	total_html += indent(0)+'<h2><a href="'+year+'/">'+year+'</a></h2>\n'
	year_months = sorted(os.listdir('TeX/'+year), key=lambda m:int(m[:-len('.tex')]))
	for month in year_months:
		# Make month if not there
		month = month[:-len('.tex')]
		if month not in os.listdir('TIL/'+year):
			os.mkdir('TIL/'+year+'/'+month)
		# Start the month file
		month_html = start_html(3)
		month_html += indent(0)+'<p class="back"><a href="../" class="link">' \
			'(back up to '+year+')</a></p>\n'
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
			f.write(day_html)
			f.close()
			# Add onto the month
			month_html += month_html_day
		month_html += end_html(3)
		# Make the month file
		f = open('TIL/'+year+'/'+month+'/'+'index.html','w')
		f.write(month_html)
		f.close()
	year_html += end_html(2)
	# Make the year file
	f = open('TIL/'+year+'/index.html','w')
	f.write(year_html)
	f.close()
total_html += end_html(1)
# Make the total file
f = open('TIL/index.html','w')
f.write(total_html)
f.close()
