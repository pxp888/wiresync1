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


async function statPressed(e) {
	e.preventDefault();
	const data = { 't':'stat',
		'm':document.getElementById('msgLine').value };
	sendmsg(data);
}
rfuncs['stat'] = function(data) {
	say('stat response: ' + data['m']);
}

$("#submit").click(statPressed);
$("#msgLine").addEventListener("submit", function(event) { preventDefault(event); });


