window.addEventListener('resize', sidebarHeight);

function sidebarHeight()
{
	var height = $('.content').height();
	$('.sidebar').height(height);
}

sidebarHeight();

var submenus = document.getElementsByClassName('yearmenu');
for(var i = 0; i < submenus.length; ++i)
{
	submenus[i].addEventListener('click', function()
	{
		var submenu = this.nextElementSibling;
		if(submenu.style.display === 'block')
			submenu.style.display = 'none';
		else
			submenu.style.display = 'block';
	});
}
