const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { exec } = require('child_process');

// Create the server
const server = http.createServer((req, res) => {
    if (req.url === '/') {
        // Serve the HTML file
        const filePath = path.join(__dirname, 'index.html');
        fs.readFile(filePath, (err, content) => {
            if (err) {
                res.writeHead(500);
                res.end('Error loading file');
            } else {
                res.writeHead(200, { 'Content-Type': 'text/html' });
                res.end(content, 'utf-8');
            }
        });
    } else if (req.url === '/packet-sniffer'){
        exec('./display_devices', (error, stdout, stderr) => {
            if (error) {
                res.writeHead(500);
                res.end(`Error executing C program: ${error.message}`);
            } else {
                res.writeHead(200, { 'Content-Type': 'text/plain' });
                res.end(`C program output:\n${stdout}`);
            }
        });
    }
});

// Start the server on port 3000
server.listen(3000, () => {
    console.log('Server running on http://localhost:3000');
    const child = spawn('./output');
    child.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
      });
      
      child.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
      });
      
      child.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
      });
});
