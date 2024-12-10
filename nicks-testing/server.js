const http = require('http');
const { spawn } = require('child_process');

// Create the server
const server = http.createServer((req, res) => {
    if (req.url === '/') {
        // Execute the Python script
        const pythonProcess = spawn('/usr/bin/python3', ['capture_starter.py']);

        let output = '';
        pythonProcess.stdout.on('data', (data) => {
            output += data.toString();
        });

        pythonProcess.stderr.on('data', (err) => {
            console.error(`Error: ${err}`);
        });

        pythonProcess.on('close', (code) => {
            if (code === 0) {
                res.writeHead(200, { 'Content-Type': 'text/plain' });
                res.end(output);
            } else {
                res.writeHead(500);
                res.end('Failed to execute Python script');
            }
        });
    } else {
        res.writeHead(404);
        res.end('Not Found');
    }
});

// Start the server on port 3000
server.listen(3000, () => {
    console.log('Server running on http://localhost:3000');
});
