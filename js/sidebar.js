// setting the sidebar's height
window.addEventListener('resize', sidebarHeight);

function sidebarHeight()
{
	// +11 accounts for the padding of the sidebar
	var contentHeight = $('.content')[0].offsetHeight - 11;
	$('.sidebar').height(contentHeight);
}

sidebarHeight();

window.MathJax.Hub.Queue(function ()
{
	sidebarHeight();
});

// the clickable menus
var submenus = document.getElementsByClassName('yearmenu');
for(var i = 0; i < submenus.length; ++i)
{
	// just add a listener for each element
	submenus[i].addEventListener('click', function()
	{
		// hack by looking at the next element directly
		var submenu = this.nextElementSibling;
		if(submenu.style.display === 'block')
			submenu.style.display = 'none';
		else
			submenu.style.display = 'block';
	});
}
