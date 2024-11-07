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
RULES_DIR = "/etc/suricata/rules"

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
@app.get("/rule-files")
def list_rule_files():
    try:
        files = [f for f in os.listdir(RULES_DIR) if f.endswith(".rules")]
        return {"files": files}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Rules directory not found.")

# Load rules from a specific .rules file
def load_suricata_rules(file_name: str):
    rules = []
    file_path = os.path.join(RULES_DIR, file_name)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    with open(file_path, "r") as file:
        rules = [line.strip() for line in file if line.strip() and not line.startswith("#")]
    return rules

# Endpoint to get rules from a specific file
@app.get("/rules/{file_name}")
def get_rules(file_name: str):
    return load_suricata_rules(file_name)

# Endpoint to update a specific rule in a selected file
@app.post("/rules/{file_name}/{rule_id}")
def update_rule(file_name: str, rule_id: int, rule: Rule):
    file_path = os.path.join(RULES_DIR, file_name)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    
    with open(file_path, "r") as file:
        rules = file.readlines()

    # Ensure rule ID is within range
    if rule_id < 0 or rule_id >= len(rules):
        raise HTTPException(status_code=400, detail="Invalid rule ID.")

    # Update the rule and write changes back to the file
    rules[rule_id] = rule.rule_text + "\n"
    with open(file_path, "w") as file:
        file.writelines(rules)

    return {"message": "Rule updated successfully"}
