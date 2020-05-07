// Button sends the two number inputs to the server and displays the
// result.
document.getElementById("button").addEventListener("click", () => {
  let ws = new WebSocket("ws://localhost:8001/");

  ws.onopen = function(event) {
    msg = {
      x: parseInt(document.getElementById("x").value),
      y: parseInt(document.getElementById("y").value)
    };
    ws.send(JSON.stringify(msg));
  };

  ws.onmessage = function(event) {
    msg = JSON.parse(event.data);
    document.getElementById("result").innerText = msg.sum;
  };
});
