import os
import calendar


def create_archive():
	archive = ''
	for year in next(os.walk('TeX'))[1]:
		year_months = sorted([int(m[:-len('.tex')]) for m in os.listdir('TeX/' + year)])
		archive += f'<button class="yearmenu">{year}</button>\n'
		archive += '<ul class="monthmenu">\n'
		for month in year_months:
			directory = year + '/' + str(month)
			title = calendar.month_name[month] + ' ' + year
			archive += f'<li><a href="{{ "/TIL/{directory}" | relative_url }}">{title}</a></li>\n'
		archive += '</ul>\n'

	return archive
