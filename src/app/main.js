const lottie_container = document.getElementById('lottie');

function loadJSON(animationData) {
	console.log(animationData);
	try {
		lottie_container.innerHTML = '';
	    bodymovin.loadAnimation({
	        container: lottie_container,
	        animationData: animationData,
	        renderer: 'svg',
	        loop: window.loopAll,
	        autoplay: true,
	    });
	}
	catch(e)
	{
		console.error(e);
	}
}

function loadSVG(data_uri) {
	try {
		lottie_container.innerHTML = '';
	    const img = document.createElement("img");
	    img.src = data_uri;
	    lottie_container.append(img);
	}
	catch(e)
	{
		console.error(e);
	}
}
