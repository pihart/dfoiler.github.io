// setting the sidebar's height
window.addEventListener('resize', sidebarHeight);

function sidebarHeight()
{
	// +15 accounts for the margin-bottom of an entry
	var contentHeight = $('.content').height() + 15;
	// height all the way to the bottom
	var windowHeight = window.innerHeight - $('.title')[0].offsetHeight - 12;
	$('.sidebar').height(Math.max(contentHeight, windowHeight));
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
