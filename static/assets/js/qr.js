
// Get the video element and the button
var scanner = document.querySelector('#scanner');
var startScanButton = document.querySelector('#start-scan');

// Create a new instance of the QR code scanner
var scanner = new Instascan.Scanner({
  video: scanner,
  scanPeriod: 5,
  mirror: false,
});

// When a QR code is detected, send it to the server
scanner.addListener('scan', function (content) {
  console.log(content);
  // Send the QR code to the server using an AJAX request
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/scan-qr", true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4 && xhr.status == 200) {
      // Display the result returned by the server
      console.log(xhr.responseText);
    }
  };
  xhr.send(JSON.stringify({'qr_code': content}));
});

// Start the scanner when the button is clicked
startScanButton.addEventListener('click', function () {
  Instascan.Camera.getCameras().then(function (cameras) {
    if (cameras.length > 0) {
      scanner.start(cameras[0]);
    } else {
      console.error('No cameras found.');
    }
  }).catch(function (e) {
    console.error(e);
  });
});