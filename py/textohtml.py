import sys			# argv
import os			# path, chdir, listdir, mkdir

# Relocate for local imports
PATH = os.path.abspath(__file__)
PATH = PATH[:-PATH[::-1].index('/')]
os.chdir(PATH)

from html_format import *

# Relocate for the rest of the program
PATH = os.path.abspath(__file__)
PATH = PATH[:-PATH[::-1].index('/')] + '../'
os.chdir(PATH)

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
	tex = tex.replace('<',' \\lt ')
	tex = tex.replace('>',' \\gt ')
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

def process_line(line, last_tags, first_item):
	to_add = ''
	close_until = last_tags[-1] if not first_item else ''
	new_tags = []
	# Update ending indents now
	environ_tags = {'itemize':'ul','enumerate':'ol',
		'theorem':'div','lemma':'div','proposition':'div',
		'idea':'div','definition':'div','example':'div'}
	# Consecutive lines implies a new paragraph
	if not line or line.isspace():
		pass
	# Various list commands
	elif any('\\begin{'+env in line for env in environ_tags):
		env = [e for e in environ_tags if '\\begin{'+e in line][0]
		# Close if coming from a paragraph
		close_until = 'p' if last_tags[-1] == 'p' else ''
		if env == 'itemize' or env == 'enumerate':
			first_item = True
			new_tags = [environ_tags[env],'li','p']
		else:
			new_tags = ['div class="'+env+'"','p']
			to_add += '<b>'+env[0].upper()+env[1:]+'.</b> '
	elif any('\\end{'+env in line for env in environ_tags):
		env = [e for e in environ_tags if '\\end{'+e in line][0]
		close_until = environ_tags[env]
	elif '\\item' in line:
		line = line.replace('\\item','')
		# Close tag if not first item
		if not first_item:
			new_tags = ['li','p']
			close_until = 'li'
		to_add += line
		first_item = False
	# Image marker
	elif line[0] == '\00':
		filename = line[1:]
		to_add += '<img src="'+filename+'">\n'
	# Catch-all
	else:
		close_until = ''
		# We can only write into p
		if last_tags[-1] != 'p':
			new_tags = ['p']
		to_add += line
	# Add in the closing
	closing = ''
	if close_until:
		index = len(last_tags)-1-last_tags[::-1].index(close_until)
		closing = '\n'.join('</'+t+'>' for t in last_tags[index:][::-1])
		last_tags = last_tags[:index]
	to_add = closing + '\n'.join('<'+t+'>' for t in new_tags) + to_add
	# only add in the titles
	last_tags += [t.split()[0] for t in new_tags]
	return to_add, last_tags, first_item

def to_html(tex):
	# This is not general-purpose and will not work with your TeX
	# Preprocess
	tex = process_tex(tex)
	# Extract the blurb
	blurb = get_blurb(tex)
	# Now we work line-by-line
	tex = tex.split('\n')
	while tex[-1] == '': tex = tex[:-1]
	day_html = start_html
	month_html = '<div class="entry">\n'
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
			day_html += '<p class="mobilenav"><a href="../" class="link">' \
				'(back up to '+month+')</a></p>\n'
			day_html += '<div class="entry">\n'
			day_html += '<h2>'+h2+'</h2>\n'
			day = day[:-len('th')]
			month_html += '<h3><a href="'+day+'/">'+h2+'</a></h3>\n'
			# Go ahead and start the first paragraph
		else:
			try:
				to_add, last_tags, first_item = \
					process_line(line, last_tags, first_item)
			except:
				print(day_html)
				print(0/0)
			day_html += to_add
	if last_tags[-1]:
		day_html += '</'+last_tags[-1]+'>\n'
	day_html += '</div>\n' + end_html
	month_html += '<p>'+blurb+'\n'
	month_html += '<a href="'+day+'/" class="link">(continue reading...)</a></p>\n'
	month_html += '</div>\n'
	return day_html, month_html

# Make TIL folder if not present
if 'TIL' not in os.listdir():
	os.mkdir('TIL')

# Start the total file
total_html = start_html
# Add in the intro
total_html += '<h2>Welcome</h2>\n'
intro = process_tex(open('TeX/intro.tex').read())
parts = [part for part in intro.split('\n') if part]
for part in parts:
	total_html += '<p>'+part+'</p>\n'
# Mobile navigation
total_html += '<div class="mobilenav">\n'
total_html += '<h2 style="margin-top: 8pt">Archive</h2>\n'
total_html += '<p>You can navigate to an entry from the archive below.</p>\n'
total_html += archive
# Some padding
total_html += '<div style="height: 6pt;"></div>\n'
total_html += '</div>\n'
total_html += '<div style="height: 7pt;"></div>\n'
total_html += end_html
# Make the total file
f = open('TIL/index.html','w')
f.write(prettify(total_html))
f.close()

# Iterate through the years subdirectories
for year in next(os.walk('TeX'))[1]:
	# Start the year file
	year_html = start_html
	year_html += '<p class="mobilenav"><a href="../" class="link">' \
		'(back up to main page) </a></p>\n'
	year_html += '<h2><a href="./">'+year+'</a></h2>\n'
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
		month_html = start_html
		month_html += '<p class="mobilenav"><a href="../../" class="link">' \
			'(back up to main page)</a></p>\n'
		month_html += '<h2>' + months[int(month)-1] + ' '+year+'</h2>\n'
		# Increment the year file
		year_html += '<h3><a href="'+month+'/">'+ \
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
		month_html += end_html
		# Make the month file
		f = open('TIL/'+year+'/'+month+'/'+'index.html','w')
		f.write(prettify(month_html))
		f.close()
	# Some padding
	year_html += '<div style="height: 6pt;"></div>\n'
	year_html += end_html
	# Make the year file
	f = open('TIL/'+year+'/index.html','w')
	f.write(prettify(year_html))
	f.close()
