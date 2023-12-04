const say = msg => console.log(msg);


const URL="/test";
const rfuncs = {};


async function sendmsg(data) {
	const response = fetch('/test', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({
			data
		})
	})
	.then(response => response.json())
	.then(data => getmsg(data))
	.catch(error => console.error('Error sending data:', error));
}


function getmsg(data) {
	if (data['t'] in rfuncs) {
		rfuncs[data['t']](data);
	}
	else { say('no js handler for ' + data['t']); }
}


// ############################ LOGIC ############################

const outarea = document.getElementsByClassName('outarea')[0];


function showoutput(data) {
	outarea.innerHTML = '';
	let lines = data['m'].split('\n');
	let box = document.createElement('div');
	box.className = 'outputbox';
	for (let line of lines) {
		if (line.length == 0) { 
			outarea.appendChild(box);
			box = document.createElement('div');
			box.className = 'outputbox';
		}
		let p = document.createElement('p');
		p.innerText = line;
		box.appendChild(p);
	}
}


async function statPressed(e) {
	e.preventDefault();
	const data = { 't':'status' };
	sendmsg(data);
}
rfuncs['status'] = showoutput;


async function peerPressed(e) {
	e.preventDefault();
	const data = { 't':'peers' };
	sendmsg(data);
}
rfuncs['peers'] = function(data) {
	outarea.innerHTML = '';
	let peers = data['peers'];
	const items = ['publickey', 'wgip', 'listen_port', 'lanip', 'wanip'];
	for (let peer of peers) {
		let box = document.createElement('div');
		box.className = 'peerbox';
		box.innerHTML = document.getElementById('demo_peerbox').innerHTML;

		for (let item of items) {
			box.getElementsByClassName(item)[0].innerText = peer[item];
		}
		outarea.appendChild(box);
		// convert peer['time'] to local time
		let time = new Date(peer['time'] * 1000);
		let time_str = time.toLocaleString();
		box.getElementsByClassName('time')[0].innerText = time_str;
	}
}


// ############################ PAGE SETUP ############################



// ############################ EVENT LISTENERS ############################

$("#statusButton").click(statPressed);
$("#peerButton").click(peerPressed);

$("#peerButton").click();