// var source = new EventSource('{{ url_for('sse.notifications', channel='user-1') }}');

// source.addEventListener('greeting', function (event) {
//     var data = JSON.parse(event.data);
//     alert('The server says ' + data.message);
// }, false);

// source.addEventListener('error', function (event) {
//     alert('Failed to connect to event stream. Is Redis running?');
// }, false);


var logged_user_id = null;

function joinUser() {
    let username = document.getElementById('username-input').value;
    fetch('/user', {
        'method': 'POST',
        'headers': {'Content-Type': 'application/json'},
        'body': JSON.stringify({name: username}),
    }).then(response => response.json())
        .then(user => logged_user_id = user._id);
}
