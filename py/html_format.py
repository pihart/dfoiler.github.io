import os			# path, chdir, listdir, mkdir

# Get absolute path
PATH = os.path.abspath(__file__)
PATH = PATH[:-PATH[::-1].index('/')] + '../'
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
	archive += '<button class="yearmenu">'+year+'</button>\n'
	archive += '<ul class="monthmenu">\n'
	for month in year_months:
		directory = year + '/'+str(month)
		title = months[month-1] + ' ' + year
		archive += '<li><span><a href="https://dfoiler.github.io/TIL/' \
			+directory+'/">'+title+'</a></span></li>\n'
	archive += '</ul>\n'

# Generating the top HTML
start_html = header
start_html += '<body>\n'
start_html += '<h1 class="title"><a href="https://dfoiler.github.io/TIL/"' \
	' class="title">Today I Learned</a></h1>\n'
start_html += '<div class="container">\n'
# Add in the archive sidebar
start_html += '<div class="sidebar">\n'
start_html += '<p style="text-align: center; font-weight: bold; '\
	'margin-top: 5px;">Archive</p>\n'
start_html += archive
start_html += '</div>\n'
start_html += '<div class="content">\n'

# Generating the bottom HTML
end_html = '</div>\n'
end_html += '</div>\n'
end_html += '<script src="https://dfoiler.github.io/js/sidebar.js"></script>\n'
end_html += '</body>\n'
end_html += '</html>\n'

# Reducing my headaches
def prettify(html):
	# Standardize input
	html = html.replace('\n','').replace('\t','')
	# Gather tags and content
	content = []
	for c in html:
		# New tag
		if c == '<':
			content += ['<']
		# Close tag
		elif c == '>':
			content[-1] += '>'
			content += ['']
		# We want the tag type after "<": no "<  p>"
		elif not(content[-1] == '<' and c==' '):
			content[-1] += c
	content = [c.strip() for c in content if c]
	# Indents
	level = 0
	# Not exhaustive, but good enough for now
	no_close = ['</','<img','<!','<link','<meta']
	html = ''
	for c in content:
		# Hit a close: now indent less
		if '</' in c:
			level -= 1		
		html += level*'\t' + c + '\n'
		# Hit an open: next get indented more
		if '<' in c and not any(tag in c for tag in no_close):
			level += 1
	return html
