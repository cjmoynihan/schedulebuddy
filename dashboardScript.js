
	//console.log(JSON.stringify(JSON.parse('[\n"cj"\n]')));
	console.log(JSON.stringify(JSON.parse('[\n{\n"end_time": 1519535800,\n"event_name": "Hackathon",\n"start_time": 1519534800,\n"username": "stefan4472"\n}\n]')));
  
	// url of webserver that will handle requests
	var HOST_URL = 'http://partrico.pythonanywhere.com'
	
	// name of user using the website TODO: READ FROM SOMEWHERE ELSE
	//var USERNAME = 'stefan4472';
	
	// canvas where calendar is drawn
	var canvas = document.getElementById("calendarCanvas");
	var ctx = canvas.getContext("2d");
	
	// list of Event objects, which will be drawn to the calendar
	var events = [];
	
	// list of friends
	var friends = [];
	
	// TODO: MAP FRIEND USERNAMES TO LIST
	var friendEvents = [];
	
	loadEvents(USERNAME);
	loadFriends(USERNAME);
	
	var new_event_btn = document.getElementById("submit_event_btn");
	
	// create event from entered info when user clicks submit button
	new_event_btn.onclick = function() {
		// extract fields
		var event_name = document.getElementById("eventNameInput").value;
		var start_time = document.getElementById("startTimeInput").value;
		var end_time = document.getElementById("endTimeInput").value;
		var day = document.getElementById("dayInput").value;
		
		// make sure user entered info for each field
		if (event_name === "") {
			alert("Please Enter Event Name");
		}
		else if (start_time === "") {
			alert("Please Enter Start Time");
		}
		else if (end_time === "") {
			alert("Please Enter End Time");
		}
		else {
			// parse day, start, end times from input fields and createEvent()
			var day = parseInt(day);
			
			var start_hour = parseInt(start_time.substring(0, start_time.indexOf(":")));
			var start_min = parseInt(start_time.substring(start_time.indexOf(":") + 1, start_time.length));
			
			var end_hour = parseInt(end_time.substring(0, end_time.indexOf(":")));
			var end_min = parseInt(end_time.substring(end_time.indexOf(":") + 1, end_time.length));
			
			addEvent(event_name, day, start_hour, start_min, end_hour, end_min);
			
			// clear fields
			document.getElementById('eventNameInput').value = '';
			document.getElementById('startTimeInput').value = '';
			document.getElementById('endTimeInput').value = '';		
		}
	};
	
	var add_friend_btn = document.getElementById("addFriendBtn");
	
	// function makes server request and adds friend name to the list, if exists
	add_friend_btn.onclick = function() {
		
		var friend_name = document.getElementById('friendNameInput').value;
		
		// create HTTP request to add friend to database
		request_obj = new XMLHttpRequest();
		request_obj.open("GET", addFriendRequest(USERNAME, friend_name), true);
		request_obj.setRequestHeader('Access-Control-Allow-Origin', '*');
		request_obj.send(null);
		
		// handle response: parse and add to friends list
		request_obj.onreadystatechange = function() {
			// request is ready
			if (request_obj.readyState == 4)  { 
				alert(request_obj.responseText);
				friends.push(friend_name);
				addFriendToUI(friend_name);
			}
		};
		
		// clear input box
		document.getElementById('friendNameInput').value = '';
	}
	
	// makes HTTP request to server and parses returned events, adding them to events list
	function loadEvents(username) {
		console.log("Running request " + getEventsRequest(USERNAME));
		
		// create HTTP request and use generated GET request
		request_events = new XMLHttpRequest();
		request_events.open("GET", getEventsRequest(USERNAME), true);
		request_events.setRequestHeader('Access-Control-Allow-Origin', '*');
		request_events.send(null);
		
		// handle response: parse and add to events list
		request_events.onreadystatechange = function() {
			// request is ready
			if (request_events.readyState == 4)  { 
				console.log('Received events: ' + request_events.responseText);
				// parse reply and add
				if (request_events.responseText !== "") {
					var parsed_events = JSON.parse(request_events.responseText);
					for (var i = 0; i < parsed_events.length; i++) {
						console.log('Adding received event: ' + JSON.stringify(parsed_events[i]));
						events.push(parsed_events[i]);
					}
					drawCalendar();
				}
			}
		};
	}
	
	// makes HTTP request to server and parses returned friends, adding them to friends list
	function loadFriends(username) {
		console.log("Running request " + getFriendsRequest(USERNAME));
		
		// create HTTP request and use generated GET request
		request_friends = new XMLHttpRequest();
		request_friends.open("GET", getFriendsRequest(USERNAME), true);
		request_friends.setRequestHeader('Access-Control-Allow-Origin', '*');
		request_friends.send(null);
		
		// handle response: parse and add to events list
		request_friends.onreadystatechange = function() {
			// request is ready
			if (request_friends.readyState == 4)  { 
				console.log('Received Friends: ' + request_friends.responseText);
				
				if (request_friends.responseText !== "") {
					var parsed_friends = JSON.parse(request_friends.responseText);
					for (var i = 0; i < parsed_friends.length; i++) {
						console.log("Adding friend " + parsed_friends[i]);
						friends.push(parsed_friends[i]);
						addFriendToUI(parsed_friends[i]);
					}
				}
				//return request_friends.responseText === "" ? [] : JSON.parse(request_friends.responseText);
			}
		};
	}
	
	function addEvent(name, day, startTimeHr, startTimeMin, endTimeHr, endTimeMin) {
		console.log("Creating event using data: " + name + " " + day + " " + startTimeHr + ":" + startTimeMin + " to " + endTimeHr + ":" + endTimeMin);
		
		// construct object
		var event = {
				username: USERNAME,
				event_name: name,
				start_time: getUTCTime(day, startTimeHr, startTimeMin),
				end_time: getUTCTime(day, endTimeHr, endTimeMin),
			};
		// make server request to add event
		request_obj = new XMLHttpRequest();
		console.log("Sending request " + addEventRequest(USERNAME, name, event.start_time, event.end_time));
		request_obj.open("GET", addEventRequest(USERNAME, name, event.start_time, event.end_time), true);
		request_obj.setRequestHeader('Access-Control-Allow-Origin', '*');
		request_obj.send(null);
		
		// handle response: parse and add to events list
		request_obj.onreadystatechange = function() {
			// request is ready
			if (request_obj.readyState == 4)  { 
				console.log('Server response to adding event: ' + request_obj.responseText);
				// add event and redraw calendar
				events.push(event);
				drawCalendar();
			}
		};
	}
	
	function addFriendToUI(friend_name) {
		console.log("Adding friend " + friend_name + " to UI");
		var new_checkbox = document.createElement('div');	
		new_checkbox.innerHTML = "<input type='checkbox' value='" + friend_name + "'>" + friend_name + "</input>";
		new_checkbox.onclick = function() {
			// TODO: ADD FRIEND'S DATA TO CALENDAR
		};
		document.getElementById('friendSection').appendChild(new_checkbox);
	}
	
	// draws given event object to calendar using the given start time of the week
	function drawEvent(event, weekStartTime) {
		console.log("Drawing event " + JSON.stringify(event));
		console.log("Event starts at " + (new Date(event.start_time)).toString() + ". Week starts at " + (new Date(weekStartTime)).toString());
		// don't do anything if event happens before or after given week
		if (event.start_time < weekStartTime || event.start_time > weekStartTime + 604800000) {
			console.log("Event is not in this week's range");
			return;
		}
		
		var start_date = new Date(event.start_time);
		var end_date = new Date(event.end_time);
		
		var box_x = start_date.getDay() * (canvas.width / 7);
		var box_y = canvas.height / 24.0 * start_date.getHours() + canvas.height / 1440.0 * start_date.getMinutes();
		var box_width = canvas.width / 7;
		var box_height = canvas.height / 24.0 * (end_date.getHours() - start_date.getHours()) + canvas.height / 1440.0 * (end_date.getMinutes() - start_date.getMinutes());
		
		console.log("Box coordinates are " + box_x + ", " + box_y + " with w/h " + box_width + ", " + box_height);
		// draw box
		ctx.fillStyle = generateColor();
		ctx.fillRect(box_x, box_y, box_width, box_height);
		
		// draw event name and time *if space*
		var font_size = 30;
		ctx.font = font_size + "px Arial";
		ctx.fillStyle = '#000000';
		
		if (box_height >= 32) {
			ctx.fillText(event.event_name, box_x, box_y + font_size);
		}
		if (box_height >= 64) {
			ctx.fillText(formatTime(start_date.getHours(), start_date.getMinutes()) + ' - ' + formatTime(end_date.getHours(), end_date.getMinutes()), box_x, box_y + 2 * font_size);
		}
	}
	
	function drawCalendar() {
		console.log("Drawing Calendar");
		var day_width = canvas.width / 7;
		var hour_height = canvas.height / 24;
		
		// draw vertical grid lines
		ctx.fillStyle = '#000000';
		for (var i = 0; i <= 24; i++) {
			ctx.moveTo(0, i * hour_height);
			ctx.lineTo(canvas.width, i * hour_height);
			ctx.stroke();
		}
		
		ctx.fillStyle = '#000000';
		// draw lines separating days
		for (var i = 0; i < 8; i++) {
			ctx.moveTo(i * day_width, 0);
			ctx.lineTo(i * day_width, canvas.width);
			ctx.stroke(); 
		}
		
		var start_time = getWeekStartTimeUTC((new Date()).getTime());
		for (var i = 0; i < events.length; i++) {
			drawEvent(events[i], start_time);
		}
	}
	
	// returns start time (ms since Epoch) of the week for the given time
	function getWeekStartTimeUTC(ms) {
		var date = new Date(ms);
		// subtract off ms for day of week, hour of day, minute of day to get time of midnight Monday
		ms -= date.getDay() * 86400000;
		ms -= date.getHours() * 3600000;
		ms -= date.getMinutes() * 60000;
		ms -= date.getSeconds() * 1000;
		ms -= date.getMilliseconds();
		return ms;
	}
	
	// returns UTC time (ms since Epoch) given day, hour, and minute of given week.
	// calculates based on time of previous Monday at midnight
	function getUTCTime(day, hour, minute) {
		var date = new Date();
		// get current time in ms
		var ms = date.getTime();
		
		// subtract of ms for day of week, hour of day, minute of day to get time of midnight Monday
		ms -= date.getDay() * 86400000;
		ms -= date.getHours() * 3600000;
		ms -= date.getMinutes() * 60000;
		ms -= date.getSeconds() * 1000;
		ms -= date.getMilliseconds();
		// add back times for day, hour, and minute
		return ms + day * 86400000 + hour * 3600000 + minute * 60000;
	}
	
	// create string request to get all friends for user
	function getFriendsRequest(username) {
		return "https://cors-anywhere.herokuapp.com/" + HOST_URL + "/get_friends/" + username;
	}
	
	// create string request to add friend for user
	function addFriendRequest(username, friendName) {
		return "https://cors-anywhere.herokuapp.com/" + HOST_URL + "/add_friend?username=" + username + "&friend_username=" + friendName;
	}
	
	// create string request to get all events for user
	function getEventsRequest(username) {
		return "https://cors-anywhere.herokuapp.com/" + HOST_URL + "/get_events/" + username;
	}
	
	// create string request to add an event for user. Takes times in UTC
	function addEventRequest(username, event_name, start_time_utc, end_time_utc) {
		return "https://cors-anywhere.herokuapp.com/" + HOST_URL + "/add_event?username=" + USERNAME + "&event_name=" + event_name + "&start_time=" + start_time_utc + "&end_time=" + end_time_utc;
		//add_event?username=stefan4472&event_name=Hackathon&start_time=1519534800&end_time=1519535800
	}
	
	// returns hex string of nice, random palette color
	function generateColor() {
		var r = (Math.round(Math.random()* 127) + 127).toString(16);
		var g = (Math.round(Math.random()* 127) + 127).toString(16);
		var b = (Math.round(Math.random()* 127) + 127).toString(16);
		return '#' + r + g + b;
	}
	
	// formats hours:minutes date to HH:MM AM/PM
	function formatTime(hours, minutes) {
		return hours + ":" + minutes; // TODO
	}