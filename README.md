# To Run UI application
Make sure you are in the installation directory, run `run.sh` script, it will install dependencies and run the application on the `https://localhost:8000` 

# Georges Contibutions
Everything in /CS425_Capstone/Georges_Scripts + All implementation of these scripts including:
Everything in /frontend and in /backend that had to deal with, IPS alerts, Honeypot, and SNMP along with code in the backend main.py that had to deal with these functions, "alertsTab" open tab events in ./frontend/static/js/ips-settings which are 

```
@app.get("/honeypot-logs", dependencies=[Depends(verify_user)])

@app.get("/snmp-logs", dependencies=[Depends(verify_user)])

@app.get("/suricata-logs", dependencies=[Depends(verify_user)])

@app.post("/clear-snmp")

def clear_snmp():

@app.post("/clear-honeypot")

def clear_honeypot():

@app.post("/clear-suricata")

def clear_suricata():

@app.get("/honeypot-page",name="honeypot-page")
```

# James Contributions 
Everything in `./backend/db/`, `./backend/login/`, `./backend/passwordHashing/`, `./installation/`, most functions in `./backend/main.py` except for George's stuff most of Javascript files in `./frontend/static/js/` except for `honeypot/` and `devices`
