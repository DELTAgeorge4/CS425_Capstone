from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse
import os

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Middleware for session management
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

templates = Jinja2Templates(directory="templates")

# Directory where Suricata rules are stored
RULES_DIR = "C:\\Program Files\\Suricata\\rules" # For Windows
#RULES_DIR = "/etc/suricata/rules"  # For Linux

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
async def login(request: Request, data: LoginData):
    # Replace with real user validation
    if data.username == "testuser" and data.password == "testpass":
        request.session["authenticated"] = True
        return {"message": "Login successful"}  # JSON response instead of redirect
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")

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

@app.get("/fart")
async def fart():
    return {"message": "fart"}

# Class for rule representation
class Rule(BaseModel):
    rule_text: str

# Endpoint to list all available rule files
@app.get("/rules", dependencies=[Depends(verify_user)])
def list_rule_files():
    try:
        files = [f for f in os.listdir(RULES_DIR) if f.endswith(".rules")]
        print(files)
        return {"files": files}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Rules directory not found.")

SURICATA_ACTIONS = {"alert", "drop", "pass", "reject", "log", "activate", "dynamic", "monitor"}

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
                print(possible_rule)
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


