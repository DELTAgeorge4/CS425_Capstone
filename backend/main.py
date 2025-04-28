from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse
from typing import List
import os
import subprocess
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from datetime import datetime
from typing import Optional



import sys
import json


sys.path.append("..")
from .login.loginScript import login, getUserRole, changePassword, resetPassword, getUsers, getUserID, log_to_db, fetch_all_login_logs, get_recent_failed_attempts
from .login.signUp import create_user, check_role_exists, get_user_notification_preferences, set_user_notification_preferences
from .DB_To_GUI import Get_Honeypot_Info
from .DB_To_GUI import Get_SNMP_Info
from .DB_To_GUI import Get_Suricata_Info
from .DB_To_GUI import Sniffer
from .DB_To_GUI import protocol_counter
from .theme.DB_theme import get_theme, set_theme, set_font_size, get_font_size
from .db_vt.main import get_vt_results


#res = Get_Honeypot_Info()
#print(res)

# create_user("george", "gkokkinis2015@gmail.com ", "password123", "admin")
# create_user("nick", "katsarosnicholas01@gmail.com", "password123", "admin")
# create_user("james", "jamesdak231@gmail.com", "password123", "admin")
# changePassword("admin", "admin", "password123")



app = FastAPI(docs_url=None)

# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "../frontend/static")
templates_dir = os.path.join(os.path.dirname(__file__), "../frontend/templates")


app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Middleware for session management
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")


templates = Jinja2Templates(directory=templates_dir)

# Directory where Suricata rules are stored
#RULES_DIR = "C:\\Program Files\\Suricata\\rules" # For Windows
RULES_DIR = "/etc/suricata/rules"  # For Linux

# ruleCheckboxChanged = False
# globalRules = get_rules()

class LoginData(BaseModel):
    username: str
    password: str

# Mock login validation function for restricted routes
def verify_user(request: Request):
    if not request.session.get("authenticated"):
        raise HTTPException(status_code=401, detail="Unauthorized")

def verify_admin(request: Request):
    if request.session.get("role") != "admin":
        raise HTTPException(status_code=403, detail="forbidden")

def verify_moderator_or_admin(request: Request):
    if request.session.get("role") not in ["admin", "moderator"]:
        raise HTTPException(status_code=403, detail="forbidden")
    
    
    
@app.get("/user_id", dependencies=[Depends(verify_user)])
async def get_user_id(request: Request):
    username = request.session.get("username")
    user_id = getUserID(username)
    return {"user_id": user_id}


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/login")
async def loginf(request: Request, data: LoginData):
    # Replace with real user validation
    successfully_authenticated = login(data.username, data.password)
    print(get_recent_failed_attempts(data.username))

    # print(successfully_authenticated)
    if successfully_authenticated:
        request.session["authenticated"] = True
        request.session["username"] = data.username
        request.session["role"] = getUserRole(data.username)
        return {"message": "Login successful"}  # JSON response instead of redirect
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/login-logs", dependencies=[Depends(verify_user)])
async def login_logs(request: Request):
    logs = fetch_all_login_logs()
    print(logs)
    return JSONResponse(content={"logs": logs})


@app.get("/logout", dependencies=[Depends(verify_user)])
async def logout(request: Request):
    print(request.session["role"])
    log_to_db(request.session["username"], "LOGGED_OUT")
    request.session.clear()
    return RedirectResponse(url="/")


# ======================== Pages ========================

@app.get("/f/accounts", dependencies=[Depends(verify_user)])
async def accounts(request: Request):
    return templates.TemplateResponse("accounts.html", {"request": request})

@app.get("/f/honeypot-page", dependencies=[Depends(verify_user)], name="honeypot-page")
async def honeypotPage(request: Request):
    return templates.TemplateResponse("honeypot-page.html", {"request": request})

@app.get("/f/dashboard", dependencies=[Depends(verify_user)])
async def home(request: Request):
    # return templates.TemplateResponse("base.html", {"request": request})
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/f/layout", dependencies=[Depends(verify_user)])
async def layout(request: Request):
    # return templates.TemplateResponse("base.html", {"request": request})
    return templates.TemplateResponse("layout.html", {"request": request})


@app.get("/f/topology", dependencies=[Depends(verify_user)])
async def topology(request: Request):
    return templates.TemplateResponse("topology.html", {"request": request})

@app.get("/f/theme-settings", dependencies=[Depends(verify_user)])
async def theme_settings(request: Request):
    return templates.TemplateResponse("settings_theme.html", {"request": request})

@app.get("/f/notification-settings", dependencies=[Depends(verify_user)])
async def notification_settings(request: Request):
    return templates.TemplateResponse("settings_notification.html", {"request": request})

@app.get("/user-notification-settings", dependencies=[Depends(verify_user)])
async def user_notification_settings(request: Request):
    username = request.session.get("username")
    userID = getUserID(username)
    userNotificationPreferences = get_user_notification_preferences(userID)
    return {"userNotificationPreferences": userNotificationPreferences}


@app.get("/f/config-settings", dependencies=[Depends(verify_user)])
async def theme_settings(request: Request):
    return templates.TemplateResponse("settings_configuration.html", {"request": request})

@app.get("/f/SIEM", dependencies=[Depends(verify_user)])
async def SIEM(request: Request):
    return templates.TemplateResponse("SIEM.html", {"request": request})

@app.get("/SIEM", dependencies=[Depends(verify_user)])
async def SIEM2(request: Request):
    return templates.TemplateResponse("layout.html", {"request": request})

@app.get("/f/devices", dependencies=[Depends(verify_user)])
async def devices(request: Request):
    return templates.TemplateResponse("devices.html", {"request": request})

@app.get("/f/ips", dependencies=[Depends(verify_user)])
async def ips(request: Request):
    return templates.TemplateResponse("ips.html", {"request": request})

@app.get("/f/settings", dependencies=[Depends(verify_user)])
async def settings(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request})

@app.get("/f/sniffer", dependencies=[Depends(verify_moderator_or_admin)])
async def sniffer(request: Request):
    return templates.TemplateResponse("sniffer.html", {"request": request})



@app.get("/accounts", dependencies=[Depends(verify_user)])
async def accounts(request: Request):
    return templates.TemplateResponse("layout.html", {"request": request})

@app.get("/honeypot-page", dependencies=[Depends(verify_user)], name="honeypot-page")
async def honeypotPage(request: Request):
    return templates.TemplateResponse("layout.html", {"request": request})



@app.get("/dashboard", dependencies=[Depends(verify_user)])
async def home(request: Request):
    # return templates.TemplateResponse("base.html", {"request": request})
    return templates.TemplateResponse("layout.html", {"request": request})

@app.get("/layout", dependencies=[Depends(verify_user)])
async def layout(request: Request):
    # return templates.TemplateResponse("base.html", {"request": request})
    return templates.TemplateResponse("layout.html", {"request": request})


@app.get("/topology", dependencies=[Depends(verify_user)])
async def topology(request: Request):
    return templates.TemplateResponse("layout.html", {"request": request})

@app.get("/devices", dependencies=[Depends(verify_user)])
async def devices(request: Request):
    return templates.TemplateResponse("layout.html", {"request": request})

@app.get("/ips", dependencies=[Depends(verify_user)])
async def ips(request: Request):
    return templates.TemplateResponse("layout.html", {"request": request})

@app.get("/settings", dependencies=[Depends(verify_user)])
async def settings(request: Request):
    return templates.TemplateResponse("layout.html", {"request": request})

@app.get("/sniffer", dependencies=[Depends(verify_user)])
async def sniffer(request: Request):
    return templates.TemplateResponse("layout.html", {"request": request})


@app.get("/user-settings", dependencies=[Depends(verify_user)])
async def theme(request: Request):
    username = request.session.get("username")
    userID = getUserID(username)
    userTheme = get_theme(userID)
    userFontSize = get_font_size(userID)
    return {"theme": userTheme, "font_size": userFontSize}

class UserSettings(BaseModel):
    theme: str
    font_size: str
    
@app.post("/set-user-settings", dependencies=[Depends(verify_user)])
async def set_user_settings(data: UserSettings, request: Request):
    username = request.session.get("username")
    userID = getUserID(username)
    set_theme(userID, data.theme)
    set_font_size(userID, data.font_size)
    print(f"Theme: {data.theme}, Font Size: {data.font_size}")
    return {"message": "Settings updated successfully"}

class UserNotificationSettings(BaseModel):
    Honeypot: bool
    SNMP: bool
    IPS: bool

@app.post("/set-notification-settings", dependencies=[Depends(verify_user)])
async def set_notification_settings(data: UserNotificationSettings, request: Request):
    print("Parsed Data:", data)
    # Convert the object to a list for your database function
    notifications_list = [data.Honeypot, data.SNMP, data.IPS]
    userID = getUserID(request.session.get("username"))
    for notif in data:
        print(notif)
        print(notif[0])
        print(notif[1])
        set_user_notification_preferences(userID, notif[0], notif[1])
    
    
@app.get("/nav", dependencies=[Depends(verify_user)])
async def nav(request: Request):
    return templates.TemplateResponse("nav.html", {"request": request})


@app.get("/fart")
async def fart():
    return {"message": "fart"}

@app.get("/users", dependencies=[Depends(verify_admin)])
async def users(request: Request):
    users = getUsers()
    return {"users": users}

class passwordResetData (BaseModel):
    username: str
    newPassword: str

class changePasswordData (BaseModel):
    oldPassword: str
    newPassword: str
    
    
class createUserData (BaseModel):
    username: str
    newEmail: str
    newPassword: str
    newUserRole: str
    
def check_role_exists2(role):
    roles = ["admin", "moderator", "guest"]
    return role in roles
    
@app.post("/create-user")
async def fcreate_user(data: createUserData, request: Request, dependencies=[Depends(verify_admin)]):
    # print("create_user called", data)
    
    role = data.newUserRole
    if not check_role_exists2(role):
        raise HTTPException(status_code=401, detail="Role does not exist")
    
    successful = create_user(data.username, data.newEmail, data.newPassword, data.newUserRole)
    if not successful:
        raise HTTPException(status_code=401, detail="User creation unsuccessful")
    return {"message": "User creation successful"}
    
    
@app.post("/reset-user-password")
async def reset_user_password(data: passwordResetData, request: Request, dependencies=[Depends(verify_admin)]):
    print("reset_user_password called", data)
    
    successful = resetPassword(request.session.get("username"), data.username, data.newPassword)

    if not successful:
        raise HTTPException(status_code=401, detail="Password reset unsuccessful")
    return {"message": "Password reset successful"}

@app.post("/change-password")
async def change_password(data: changePasswordData, request: Request, dependencies=[Depends(verify_user)]):
    print("Parsed Data:", data)  
    successful = changePassword(request.session.get("username"), data.oldPassword, data.newPassword)
    # return {"message": "Password change successful"}
    # return an error message if the password change was unsuccessful
    if not successful:
        raise HTTPException(status_code=401, detail="Password change unsuccessful")
    return {"message": "Password change successful"}




# Class for a list of checkbox data with file name and checked status
class CheckBoxData(BaseModel):
    checkBoxList: List[bool]


@app.get("/role", dependencies=[Depends(verify_user)])
def getRole(request:Request):
    role = getUserRole(request.session.get("username"))
    return {"Role": role, "Username": request.session.get("username")}

@app.get("/network-topology", dependencies=[Depends(verify_user)])
def get_network_topology(request: Request):
    file_path = os.path.join(os.path.dirname(__file__), "../Georges_Scripts/network_topology.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Network topology file not found.")
    
    with open(file_path, "r") as file:
        data = json.load(file)  # ✅ Parse JSON into dict
    
    return JSONResponse(content=data)  # ✅ Pass dict as content
@app.post("/checkboxes", dependencies=[Depends(verify_admin)])
async def checkboxes(data: CheckBoxData, request:Request):
    ruleCheckboxChanged = True
    # print(data.checkBoxList)
    files = [f for f in os.listdir(RULES_DIR) if f.endswith(".rules")]
    # print(files)
    for i, file in enumerate(files):
        edit_rules(file, data.checkBoxList[i])
    # edit_rules(files[0], data.checkBoxList[0])
    
    # restart_suricata()

    return {"checkBoxList": data.checkBoxList}

@app.post("/restart-suricata", dependencies=[Depends(verify_admin)])
async def call_restart_suricata(request: Request):  
    restart_suricata()
 
        
def restart_suricata():
    #restartSuricata.sh path in same directory as this file
    subprocess.run(["./restartSuricata.sh"])

@app.post("/clear-snmp", dependencies=[Depends(verify_admin)])
async def call_clear_snmp(request: Request):
    clear_snmp()

def clear_snmp():
    print("Clearing SNMP Table")
    subprocess.run(["./Clear_SNMP.sh"])

@app.post("/clear-honeypot", dependencies=[Depends(verify_admin)])
async def call_clear_honeypot(request: Request):

    clear_honeypot()

def clear_honeypot():
    print("Clearing Honeypot Table")
    subprocess.run(["./Clear_Honeypot.sh"])

@app.post("/clear-suricata", dependencies=[Depends(verify_admin)])
async def call_clear_suricata(request: Request):
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

    # print(f"Updated rules in {file_name} based on checkbox state: {isChecked}")


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

@app.get("/vt-results", dependencies=[Depends(verify_user)])
def get_vt_results_endpoint():
    results, columns = get_vt_results()
    print(len(results))
    print(type(results))
    return {"header_info": columns, "vt_results": results}

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
    #  print(len(results))
    #  print(type(results))
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

class ChartData(BaseModel):
    net_chart_data: dict
    transport_chart_data: dict
    application_chart_data: dict

@app.get("/get_chart_data")
async def get_chart_data(start: Optional[str] = None, end: Optional[str] = None):
    try:
        start_dt = datetime.fromisoformat(start) if start else datetime.min
        end_dt = datetime.fromisoformat(end) if end else datetime.max

        protocol_data = protocol_counter.get_protocol_counts(start=start_dt, end=end_dt)

        return JSONResponse(content={
            "net_chart_data": protocol_data['network_layer'],
            "transport_chart_data": protocol_data['transport_layer'],
            "application_chart_data": protocol_data['application_layer']
        })
    except Exception as e:
        print("Chart data error:", str(e))
        return JSONResponse(status_code=500, content={"error": str(e)})


def read_until_input_needed(process):
    output = []
    while True:
        line = process.stdout.readline()
        if not line:
            break
        output.append(line.strip())
    return output

@app.get("/get_device_list")
async def get_device_list():
    try:
        # Compile the C program
        compilation_command = ["gcc", "-o", "find_device", "../nicks-testing/find_device.c", "-lpcap"]
        subprocess.run(compilation_command, text=True, check=True)  # Ensure error on failure
        
        device_finder_path = "./find_device"

        # Start the process
        process = subprocess.Popen(
            device_finder_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True 
        )
        
        # Read output from the process
        device_info = read_until_input_needed(process)

        # Parse the devices from the output
        devices = []
        for row in device_info:
            if "Device name" in row:
                devices.append(row.split(":")[-1].strip())

        # Wait for the process to complete
        exit_code = process.wait()

        if exit_code != 0:
            raise HTTPException(status_code=500, detail="Error encountered during device search")

        # Format the devices as a list
        numbered_devices = "\n".join([f"{device}" for i, device in enumerate(devices)])

        # Return the formatted list
        return JSONResponse(content={"devices": numbered_devices})
    
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Compilation failed or process encountered an error")

class DeviceRequest(BaseModel):
    device: str

def is_service_running(service_name):
    try:
        result = subprocess.run(
            ["systemctl", "is-active", "--quiet", service_name],
            check=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error checking service status: {e}")
        return False

@app.post("/device")
async def get_device_info(request: DeviceRequest):
    device_name = request.device.strip()

    if not device_name:
        raise HTTPException(status_code=400, detail="Device name cannot be empty.")

    # Compile the C program
    compilation_command = ["gcc", "-o", "display_device_info", "../nicks-testing/display_device_info.c", "-lpcap"]
    compile_process = subprocess.run(compilation_command, capture_output=True, text=True)

    if compile_process.returncode != 0:
        return {"error": "Compilation failed", "details": compile_process.stderr}

    # Run the compiled executable
    packet_capture_command = ["sudo", "./display_device_info", device_name]
    process = subprocess.Popen(packet_capture_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    output_lines = []
    service = "nss_sniffer_" + device_name

    if is_service_running(service):
        output_lines.append("Packet sniffer status: Active")
    else:
        output_lines.append("Packet sniffer status: Inactive")
    for line in process.stdout:
        output_lines.append(line.strip())

    exit_code = process.wait()

    if exit_code != 0:
        return {
            "error": "Error encountered while running the process",
            "details": process.stderr.read().strip()
        }

    return {"output": "\n".join(output_lines)}

def create_service(interface):
    try:
        SERVICE_NAME = f"nss_sniffer_{interface}"
        SERVICE_FILE = f"/etc/systemd/system/{SERVICE_NAME}.service"
        SCRIPT_PATH = "/home/CS425_Capstone/nicks-testing/capture_starter.py"

        SERVICE_CONTENT = f"""[Unit]
Description=NSS Packet Sniffer
After=network.target

[Service]
ExecStart=/usr/bin/python3 {SCRIPT_PATH} {interface}
WorkingDirectory=/home/CS425_Capstone/nicks-testing
Restart=always
User=root
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

[Install]
WantedBy=multi-user.target
"""

        # Write temp file and move it with sudo
        temp_service_path = "/tmp/temp_service.service"
        with open(temp_service_path, "w") as f:
            f.write(SERVICE_CONTENT)

        subprocess.run(["sudo", "mv", temp_service_path, SERVICE_FILE], check=True)
        subprocess.run(["sudo", "chmod", "644", SERVICE_FILE], check=True)
        subprocess.run(["sudo", "chown", "root:root", SERVICE_FILE], check=True)
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
        subprocess.run(["sudo", "systemctl", "enable", SERVICE_NAME], check=True)
        subprocess.run(["sudo", "systemctl", "start", SERVICE_NAME], check=True)

        return {"status": "success", "message": f"Service '{SERVICE_NAME}' started successfully."}

    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Command failed: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}

@app.post("/packet_capture")
async def start_capture(request: DeviceRequest):
    device = request.device.strip()
    
    if not device:
        raise HTTPException(status_code=400, detail="No device selected")

    result = create_service(device)

    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])

    return result

@app.post("/stop_capture")
def stop_capture(request: DeviceRequest):
    device = request.device
    service_name = f"nss_sniffer_{device}"
    
    # Stop and disable the service
    stop_command = f"sudo systemctl stop {service_name}"
    disable_command = f"sudo systemctl disable {service_name}"
    os.system(stop_command)
    os.system(disable_command)

    return {"message": f"Packet capture stopped and disabled for {device}."}

class ConfigUpdate(BaseModel):
    config: str


@app.post(
    "/update-config-file",
    dependencies=[Depends(verify_admin)]
)
async def update_config_file(update: ConfigUpdate):
    # Same file you GET in /config-file
    file_path = os.path.join(
        os.path.dirname(__file__),
        "../Georges_Scripts/config.py"
    )

    try:
        with open(file_path, "w") as f:
            f.write(update.config)
    except Exception as e:
        # Return the actual exception message so you can debug
        raise HTTPException(status_code=500,
            detail=f"Error writing config file: {e}"
        )

    return JSONResponse(content={"message": "Configuration updated successfully."})


@app.get(
    "/config-file",
    dependencies=[Depends(verify_moderator_or_admin)]
)
async def get_config_file(request: Request):
    file_path = os.path.join(
        os.path.dirname(__file__),
        "../Georges_Scripts/config.py"
    )
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Config file not found.")
    with open(file_path, "r") as f:
        data = f.read()
    return JSONResponse(content={"config": data})

@app.post("/restart-suricata-db", dependencies=[Depends(verify_admin)])
async def restart_suricata_to_db():
    """
    Restart the Suricata_to_DB service and timer.
    """
    try:
        # restart both the service and its timer
        subprocess.run(
            ["sudo", "systemctl", "restart", "Suricata_to_DB.service",
                       "Suricata_to_DB.timer"],
            check=True
        )
        return JSONResponse(content={"message": "Suricata_to_DB restarted"}, status_code=200)
    except subprocess.CalledProcessError as e:
        # capture stderr if you want more detail
        return JSONResponse(content={"detail": f"Failed to restart: {e}"}, status_code=500)

@app.get("/status-suricata-db", dependencies=[Depends(verify_admin)])
async def status_suricata_to_db():
    """
    Check whether the Suricata_to_DB service is active.
    """
    try:
        # Query systemd
        proc = subprocess.run(
            ["systemctl", "is-active", "Suricata_to_DB.service"],
            capture_output=True,
            text=True,
            check=False
        )
        state = proc.stdout.strip()  # "active", "inactive", "failed", etc.
        return JSONResponse(content={"status": state})
    except Exception as e:
        return JSONResponse(content={"status": "error", "detail": str(e)}, status_code=500)

@app.get(
    "/status-snmp-collector",
    dependencies=[Depends(verify_user)]
)
async def status_snmp_collector():
    """
    Return the active/inactive/failed state of the snmp_collector.service.
    """
    try:
        proc = subprocess.run(
            ["systemctl", "is-active", "snmp_collector.service"],
            capture_output=True,
            text=True,
            check=False
        )
        state = proc.stdout.strip()  # e.g. "active", "inactive", "failed"
        return JSONResponse(content={"status": state})
    except Exception as e:
        # unexpected errors
        return JSONResponse(
            content={"status": "error", "detail": str(e)},
            status_code=500
        )

# 2) Restart endpoint — admin only
@app.post(
    "/restart-snmp-collector",
    dependencies=[Depends(verify_admin)]
)
async def restart_snmp_collector():
    """
    Restart both snmp_collector.service and its timer.
    """
    try:
        # If your FastAPI runs as root you can drop "sudo"
        subprocess.run(
            ["sudo", "systemctl", "restart",
             "snmp_collector.service", "snmp_collector.timer"],
            check=True
        )
        return JSONResponse(content={"message": "SNMP collector restarted"})
    except subprocess.CalledProcessError as e:
        return JSONResponse(
            content={"detail": f"Failed to restart: {e}"},
            status_code=500
        )
    
@app.get(
    "/status-py-honeypot",
    dependencies=[Depends(verify_user)]
)
async def status_py_honeypot():
    try:
        proc = subprocess.run(
            ["systemctl", "is-active", "py_honeypot.service"],
            capture_output=True,
            text=True,
            check=False
        )
        state = proc.stdout.strip()  # e.g. "active", "inactive", "failed"
        return JSONResponse(content={"status": state})
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "detail": str(e)},
            status_code=500
        )

# 2) Restart endpoint — admin only
@app.post(
    "/restart-py-honeypot",
    dependencies=[Depends(verify_admin)]
)
async def restart_py_honeypot():
    try:
        subprocess.run(
            ["sudo", "systemctl", "restart", "py_honeypot.service"],
            check=True
        )
        return JSONResponse(content={"message": "py_honeypot restarted"})
    except subprocess.CalledProcessError as e:
        return JSONResponse(
            content={"detail": f"Failed to restart: {e}"},
            status_code=500
        )

@app.post("/generate_and_download_pcap")
async def generate_and_download_pcap(request: Request):
    form = await request.form()
    start = form.get("start")
    end = form.get("end")

    try:
        args = ["python", "DB_To_GUI/make_pcap.py"]
        if start:
            args += ["--start", start]
        if end:
            args += ["--end", end]

        result = subprocess.run(args, capture_output=True, text=True)

        if result.returncode != 0:
            return {"status": "error", "stderr": result.stderr}

        pcap_path = "full_output.pcap"
        if os.path.exists(pcap_path):
            return FileResponse(
                path=pcap_path,
                filename="capture.pcap",
                media_type="application/vnd.tcpdump.pcap"
            )
        else:
            return {"status": "error", "message": "PCAP file not found"}

    except Exception as e:
        return {"status": "error", "message": str(e)}