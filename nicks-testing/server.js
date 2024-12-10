const http = require('http');
const fs = require('fs');
const { spawn } = require('child_process');

// Store the device list
let deviceList = [];

// Create the server
const server = http.createServer((req, res) => {
    if (req.url === '/' && req.method === 'GET') {
        // Serve the index.html file
        fs.readFile('index.html', 'utf8', (err, data) => {
            if (err) {
                res.writeHead(500, { 'Content-Type': 'text/plain' });
                res.end('Error loading HTML file');
                return;
            }
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(data);
        });
    } else if (req.url === '/run' && req.method === 'GET') {
        // Execute the find_device.py script
        const pythonProcess = spawn('/usr/bin/python3', ['find_device.py']);

        let output = '';
        pythonProcess.stdout.on('data', (data) => {
            output += data.toString();
        });

        pythonProcess.stderr.on('data', (err) => {
            console.error(`Error: ${err}`);
        });

        pythonProcess.on('close', (code) => {
            if (code === 0) {
                deviceList = output.split('\n')
                    .filter(line => line.includes('Device name:'))
                    .map(line => line.split('Device name: ')[1].trim());
                res.writeHead(200, { 'Content-Type': 'text/plain' });
                res.end(output);
            } else {
                res.writeHead(500);
                res.end('Failed to execute Python script');
            }
        });
    } else if ((req.url === '/device' || req.url === '/capture') && req.method === 'POST') {
        // Handle device selection and execute the corresponding Python script
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
        });

        req.on('end', () => {
            const { deviceNumber } = JSON.parse(body);
            const deviceName = deviceList[deviceNumber - 1];

            if (!deviceName) {
                res.writeHead(400);
                res.end('Invalid device number');
                return;
            }

            const scriptName = req.url === '/device' ? 'print_device_info.py' : 'capture_starter.py';
            const pythonProcess = spawn('/usr/bin/python3', [scriptName, deviceName]);

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
                    res.end(`Failed to execute ${scriptName}`);
                }
            });
        });
    } else if (req.url === '/packets' && req.method === 'POST') {
        // Execute the get_packets.py script
        const pythonProcess = spawn('/usr/bin/python3', ['get_packets.py']);

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
                res.end('Failed to execute get_packets.py');
            }
        });
    } else {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Not Found');
    }
});

// Start the server on port 3000
server.listen(3000, () => {
    console.log('Server running on http://localhost:3000');
});
