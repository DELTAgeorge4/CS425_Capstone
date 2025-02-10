from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse
from typing import List
import os
import subprocess

import sys
sys.path.append("..")
from .login.loginScript import login
from .login.signUp import create_user
from .DB_To_GUI import Get_Honeypot_Info
from .DB_To_GUI import Get_SNMP_Info
from .DB_To_GUI import Get_Suricata_Info

#res = Get_Honeypot_Info()
#print(res)
# create_user("admin", "admin", "admin")
# create_user("nick", "password123", "admin")
app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")

# Middleware for session management
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

templates = Jinja2Templates(directory="../frontend/templates")

# Directory where Suricata rules are stored
#RULES_DIR = "C:\\Program Files\\Suricata\\rules" # For Windows
RULES_DIR = "/etc/suricata/rules"  # For Linux

class LoginData(BaseModel):
    username: str
    password: str

# Mock login validation function for restricted routes
def verify_user(request: Request):
    if not request.session.get("authenticated"):
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/login")
async def loginf(request: Request, data: LoginData):
    # Replace with real user validation
    successfully_authenticated = login(data.username, data.password)
    print(successfully_authenticated)
    if successfully_authenticated:
        request.session["authenticated"] = True
        return {"message": "Login successful"}  # JSON response instead of redirect
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")
@app.get("/accounts")
async def accounts(request: Request):
    return templates.TemplateResponse("accounts.html", {"request": request})

@app.get("/honeypot-page",name="honeypot-page")
async def honeypotPage(request: Request):
    return templates.TemplateResponse("honeypot-page.html", {"request": request})

@app.get("/home", dependencies=[Depends(verify_user)])
async def home(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/topology", dependencies=[Depends(verify_user)])
async def topology(request: Request):
    return templates.TemplateResponse("topology.html", {"request": request})

@app.get("/devices", dependencies=[Depends(verify_user)])
async def devices(request: Request):
    return templates.TemplateResponse("devices.html", {"request": request})

@app.get("/ips", dependencies=[Depends(verify_user)])
async def ips(request: Request):
    return templates.TemplateResponse("ips.html", {"request": request})

@app.get("/settings", dependencies=[Depends(verify_user)])
async def settings(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request})

@app.get("/nav", dependencies=[Depends(verify_user)])
async def nav(request: Request):
    return templates.TemplateResponse("nav.html", {"request": request})

@app.get("/sniffer", dependencies=[Depends(verify_user)])
async def sniffer(request: Request):
    return templates.TemplateResponse("sniffer.html", {"request": request})

@app.get("/fart")
async def fart():
    return {"message": "fart"}

# Class for a list of checkbox data with file name and checked status
class CheckBoxData(BaseModel):
    checkBoxList: List[bool]

@app.post("/checkboxes")
async def checkboxes(data: CheckBoxData):
    print(data.checkBoxList)
    files = [f for f in os.listdir(RULES_DIR) if f.endswith(".rules")]
    # print(files)
    for i, file in enumerate(files):
        edit_rules(file, data.checkBoxList[i])
    # edit_rules(files[0], data.checkBoxList[0])
    
    # restart_suricata()
    return {"checkBoxList": data.checkBoxList}

@app.post("/restart-suricata")
async def call_restart_suricata():
    restart_suricata()
        
def restart_suricata():
    #restartSuricata.sh path in same directory as this file
    print("suricata restarting")
    subprocess.run(["./restartSuricata.sh"])

@app.post("/clear-snmp")
async def call_clear_snmp():
    clear_snmp()

def clear_snmp():
    print("Clearing SNMP Table")
    subprocess.run(["./Clear_SNMP.sh"])

@app.post("/clear-honeypot")
async def call_clear_honeypot():
    clear_honeypot()

def clear_honeypot():
    print("Clearing Honeypot Table")
    subprocess.run(["./Clear_Honeypot.sh"])

@app.post("/clear-suricata")
async def call_clear_suricata():
    clear_suricata()

def clear_suricata():
    print("Clearing Suricata Table")
    subprocess.run(["./Clear_Suricata.sh"]) 

#funciton that opens up the rules files and edits the rules to comment them out if checkbox is not checked
def edit_rules(file_name: str, isChecked: bool):

    file_path = os.path.join(RULES_DIR, file_name)
    updated_lines = []

    # Read the file and process each line
    with open(file_path, "r") as file:
        lines = file.readlines()
        for line in lines:
            stripped = line.strip()

            # Keep empty lines as is
            if not stripped:
                updated_lines.append(line)
                continue

            # Check if the line is a comment
            if stripped.startswith("#"):
                possible_rule = stripped.lstrip("#").strip()

                # Validate if it's a commented Suricata rule
                valid_char = ">" in possible_rule or "<" in possible_rule
                action = possible_rule.split(" ", 1)[0]  # Extract the first word
                if action in SURICATA_ACTIONS and valid_char:
                    # It's a commented rule; uncomment or keep commented based on isChecked
                    if isChecked:
                        updated_lines.append(stripped.lstrip("#") + "\n")  # Uncomment
                    else:
                        updated_lines.append(line)  # Keep it commented
                else:
                    # Regular comment, keep as is
                    updated_lines.append(line)
            else:
                # Active rules: comment out if unchecked, keep as is if checked
                action = stripped.split(" ", 1)[0]  # Extract the first word
                if action in SURICATA_ACTIONS:
                    if not isChecked:
                        updated_lines.append(f"# {line}")  # Comment out
                    else:
                        updated_lines.append(line)  # Keep it uncommented
                else:
                    # Unrecognized lines, keep as is
                    updated_lines.append(line)

    # Write the updated lines back to the file
    with open(file_path, "w") as file:
        file.writelines(updated_lines)

    print(f"Updated rules in {file_name} based on checkbox state: {isChecked}")


# Class for rule representation
class Rule(BaseModel):
    rule_text: str

# Endpoint to list all available rule files
@app.get("/rules", dependencies=[Depends(verify_user)])
def list_rule_files():
    try:
        files = [f for f in os.listdir(RULES_DIR) if f.endswith(".rules")]
        # print(files)
        return {"files": files}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Rules directory not found.")

SURICATA_ACTIONS = {"alert", "drop", "pass", "reject", "log", "activate", "dynamic", "monitor"}

@app.get("/honeypot-logs", dependencies=[Depends(verify_user)])
def display_honeypot_logs():
     results = Get_Honeypot_Info()
     return {"Honeypot": results}

@app.get("/snmp-logs", dependencies=[Depends(verify_user)])
def display_SNMP_logs():
     results = Get_SNMP_Info()
     return {"SNMP": results}

@app.get("/suricata-logs", dependencies=[Depends(verify_user)])
def display_Suricata_logs():
     results = Get_Suricata_Info()
     print(len(results))
     print(type(results))
     return {"Suricata": results}


def load_suricata_rules(file_name: str):
    rules = []
    file_path = os.path.join(RULES_DIR, file_name)
    
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    
    with open(file_path, "r") as file:
        for line in file:
            stripped = line.strip()
            if not stripped:
                continue  # Skip empty lines
            
            if stripped.startswith("#"):
                possible_rule = stripped.lstrip("#").strip()
                # print(possible_rule)
                validChar = ">" in possible_rule or "<" in possible_rule
                action = possible_rule.split(" ", 1)[0]  # Extract the first word
                if action in SURICATA_ACTIONS and validChar:
                    rules.append({"type": "inactive_rule", "content": possible_rule})
                else:
                    rules.append({"type": "comment", "content": stripped})
            else:
                # Check if the line starts with a valid action
                action = stripped.split(" ", 1)[0]  # Extract the first word
                if action in SURICATA_ACTIONS:
                    rules.append({"type": "active_rule", "action": action, "content": stripped})
                else:
                    # If the line doesn't match any action, it may not be a valid rule
                    rules.append({"type": "unknown", "content": stripped})
    
    return rules

# Endpoint to get rules from a specific file
@app.get("/rules/{file_name}", dependencies=[Depends(verify_user)])
def get_rules(file_name: str):
    return load_suricata_rules(file_name)
