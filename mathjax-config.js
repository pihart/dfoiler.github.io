window.MathJax.Hub.Config({
	loader: {
		load: ['[tex]/textmacros']
	},
	tex2jax: {
		// https://tex.stackexchange.com/q/27633
		inlineMath: [ ['$','$'] ],
		processEscapes: true,
		packages: {'[+]': ['textmacros']}
	},
	SVG: {
		linebreaks: { automatic: true }
	}
});

window.MathJax.Hub.Queue(function ()
{
	sidebarHeight();
});

window.addEventListener('resize', MJrerender);
// https://stackoverflow.com/a/56106854
let t = -1;
let delay = 1000;
function MJrerender() {
	if (t >= 0) {
		// If we are still waiting, user is still resizing
		// postpone the action further!
		window.clearTimeout(t);
	}
	t = window.setTimeout(function() {
		MathJax.Hub.Queue(["Rerender",MathJax.Hub]);
		t = -1; // Reset the handle
	}, delay);
};
