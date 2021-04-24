import os			# path, chdir, listdir, mkdir

# Get absolute path
PATH = os.path.abspath(__file__)
PATH = PATH[:-PATH[::-1].index('/')] + '../'
os.chdir(PATH)

# standalone is for making tikz images
standalone = open('standalone.sty').read()

# Reducing my headaches
# TODO: fix weird spacing after links due to excessive whitespace
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
