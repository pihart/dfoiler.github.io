window.addEventListener('resize', sidebarHeight);

function sidebarHeight()
{
	var height = $('.content').height();
	$('.sidebar').height(height);
}

sidebarHeight();
