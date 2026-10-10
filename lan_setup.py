"""
Windows LAN deployment preflight for TLE CSS Quiz V24.2.
Safe checks only: Python, dependencies, network profile, LAN IPv4, port 8000,
and Windows Defender Firewall rule. It never disables antivirus/firewall.
"""
import ctypes, importlib.util, json, os, re, socket, subprocess, sys, time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RULE_NAME = "EGMIS TLE CSS Quiz - LAN TCP 8000"
PORT = 8000

def run(cmd, timeout=8):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           shell=isinstance(cmd, str), encoding="utf-8", errors="replace")
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except Exception as e:
        return 1, "", str(e)

def is_windows():
    return os.name == "nt"

def is_admin():
    if not is_windows():
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False

def python_info():
    return sys.version.split()[0], sys.executable

def module_status():
    required = ["flask", "werkzeug", "qrcode", "PIL", "waitress", "duckdb"]
    out = {}
    for m in required:
        out[m] = bool(importlib.util.find_spec(m))
    return out

def powershell(script):
    return run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script])

def network_info():
    if not is_windows():
        return {"profiles": [], "configs": [], "raw": ""}
    ps = r"""
$ErrorActionPreference='SilentlyContinue'
$profiles = Get-NetConnectionProfile | Select-Object Name,InterfaceAlias,NetworkCategory,IPv4Connectivity,IPv6Connectivity
$configs = Get-NetIPConfiguration | Where-Object {$_.IPv4Address} | ForEach-Object {
  [PSCustomObject]@{
    InterfaceAlias=$_.InterfaceAlias
    IPv4=($_.IPv4Address | Select-Object -First 1 -ExpandProperty IPAddress)
    Gateway=($_.IPv4DefaultGateway | Select-Object -First 1 -ExpandProperty NextHop)
    DNSServer=(($_.DNSServer.ServerAddresses) -join ',')
  }
}
[PSCustomObject]@{profiles=$profiles;configs=$configs} | ConvertTo-Json -Depth 5 -Compress
"""
    code, out, err = powershell(ps)
    if code != 0 or not out:
        return {"profiles": [], "configs": [], "raw": err}
    try:
        data = json.loads(out)
        profiles = data.get("profiles") or []
        configs = data.get("configs") or []
        if isinstance(profiles, dict): profiles=[profiles]
        if isinstance(configs, dict): configs=[configs]
        return {"profiles":profiles, "configs":configs, "raw":""}
    except Exception:
        return {"profiles": [], "configs": [], "raw":out}

def lan_ipv4(info):
    # Prefer an IPv4 interface with a default gateway and a private RFC1918 address.
    for c in info.get("configs", []):
        ip = c.get("IPv4") or ""
        if ip.startswith(("192.168.", "10.", "172.")) and c.get("Gateway"):
            return ip
    for c in info.get("configs", []):
        ip = c.get("IPv4") or ""
        if ip and not ip.startswith("127."):
            return ip
    return "127.0.0.1"

def active_profile(info, ip):
    profiles = info.get("profiles", [])
    configs = info.get("configs", [])
    alias = None
    for c in configs:
        if c.get("IPv4") == ip:
            alias = c.get("InterfaceAlias")
            break
    if alias:
        for p in profiles:
            if p.get("InterfaceAlias") == alias:
                return p
    return profiles[0] if profiles else {}

def firewall_status():
    if not is_windows():
        return {"exists":False,"enabled":False,"profiles":""}
    script = r"""
$ErrorActionPreference='SilentlyContinue'
$r = Get-NetFirewallRule -DisplayName 'EGMIS TLE CSS Quiz - LAN TCP 8000'
if (-not $r) { [PSCustomObject]@{exists=$false;enabled=$false;profiles=''} | ConvertTo-Json -Compress; exit }
$p = $r | Get-NetFirewallProfile
[PSCustomObject]@{
 exists=$true
 enabled=(@($r | Where-Object Enabled -eq 'True').Count -gt 0)
 profiles=(($p | Where-Object Enabled -eq 'True' | Select-Object -ExpandProperty Name) -join ',')
} | ConvertTo-Json -Compress
"""
    code,out,err=powershell(script)
    if code==0 and out:
        try: return json.loads(out)
        except Exception: pass
    return {"exists":False,"enabled":False,"profiles":"","error":err or out}

def port_test(host="127.0.0.1", port=PORT):
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM); s.settimeout(1.2)
    try:
        return s.connect_ex((host,port)) == 0
    finally:
        s.close()

def port_owner(port=PORT):
    if not is_windows():
        return ""
    code,out,err=run(f'netstat -ano -p tcp | findstr :{port}', timeout=5)
    if code != 0 or not out:
        return ""
    return out

def firewall_add_elevated():
    if not is_windows(): return False
    if is_admin():
        cmd = f'New-NetFirewallRule -DisplayName "{RULE_NAME}" -Direction Inbound -Action Allow -Protocol TCP -LocalPort {PORT} -Profile Private -EdgeTraversalPolicy Block | Out-Null'
        code,_,err=powershell(cmd)
        return code==0
    # Ask Windows UAC for one narrowly-scoped Private-network firewall rule.
    ps = f'Start-Process powershell -Verb RunAs -ArgumentList \'-NoProfile -ExecutionPolicy Bypass -Command "New-NetFirewallRule -DisplayName \\"{RULE_NAME}\\" -Direction Inbound -Action Allow -Protocol TCP -LocalPort {PORT} -Profile Private -EdgeTraversalPolicy Block | Out-Null"\''
    code,_,err=powershell(ps)
    if code != 0: return False
    time.sleep(1.5)
    return firewall_status().get("exists",False)

def install_requirements():
    req = BASE_DIR / "requirements.txt"
    print("\nInstalling the required Python packages once. Internet is needed for this setup step.")
    cmd=[sys.executable,"-m","pip","install","-r",str(req)]
    p=subprocess.run(cmd)
    return p.returncode==0

def print_report(auto_fix=False):
    version, exe = python_info()
    mods=module_status()
    net=network_info()
    ip=lan_ipv4(net)
    prof=active_profile(net,ip)
    fw=firewall_status()

    print("\n" + "="*72)
    print(" EGMIS TLE CSS QUIZ V24.2 — WINDOWS LAN DEPLOYMENT CHECK")
    print("="*72)
    print(f"Python:          {version}")
    print(f"Python executable:{exe}")
    print(f"LAN IPv4:        {ip}")
    print(f"Gateway:         {prof.get('Name','') or 'detected from adapter'}")
    print(f"Network profile: {prof.get('NetworkCategory','UNKNOWN')}")
    listening = port_test('127.0.0.1',PORT)
    print(f"Port {PORT}:      {'ALREADY IN USE' if listening else 'free (ready for quiz server)'}")
    if listening:
        owner = port_owner(PORT)
        if owner:
            print("Port owner info:")
            print(owner[:1200])
    print(f"Firewall rule:   {'READY (Private only)' if fw.get('exists') and fw.get('enabled') else 'NOT READY'}")
    print("-"*72)
    print("Required packages:")
    for m,ok in mods.items(): print(f"  {'OK  ' if ok else 'MISS'} {m}")
    print("-"*72)

    missing=[m for m,v in mods.items() if not v]
    if missing:
        print("ACTION: Required Python packages are missing.")
        print("Fix: run this launcher again and choose the automatic package installation.")
        if auto_fix and install_requirements():
            mods=module_status()
            missing=[m for m,v in mods.items() if not v]
            print("Package installation completed." if not missing else "Some packages are still missing.")
    if listening:
        print("\nACTION: TCP port 8000 is already in use by another process.")
        print("FIX: close the other program using port 8000, then run start_lan.bat again.")
        print("Do not kill an unknown process just to make the quiz start.")
    if is_windows() and prof.get("NetworkCategory") == "Public":
        print("\nACTION: Windows currently marks this Wi-Fi/Ethernet network as PUBLIC.")
        print("FIX: Set the trusted school/home network to PRIVATE in Windows Settings.")
        print("     Windows Settings > Network & Internet > Wi-Fi/Ethernet > Network profile > Private")
        print("Why: V24.2 creates the quiz firewall rule for PRIVATE networks only.")
    if is_windows() and not fw.get("exists"):
        print("\nACTION: Windows Defender Firewall has no EGMIS quiz rule for TCP 8000.")
        print("SAFE FIX: allow only TCP port 8000 on PRIVATE networks. Firewall/antivirus is NOT disabled.")
        if auto_fix:
            ans=input("Create the Private-network-only TCP 8000 rule now? [Y/N]: ").strip().lower()
            if ans=="y":
                if firewall_add_elevated():
                    fw=firewall_status()
                    print("Firewall rule created successfully.")
                else:
                    print("Firewall rule was not created. No security settings were disabled.")
    print("\n" + "-"*72)
    if missing:
        print("RESULT: NOT READY — install the missing packages, then start again.")
        return False
    if listening:
        print("RESULT: NOT READY — TCP port 8000 is already in use.")
        return False
    if listening:
        print("\nACTION: TCP port 8000 is already in use by another process.")
        print("FIX: close the other program using port 8000, then run start_lan.bat again.")
        print("Do not kill an unknown process just to make the quiz start.")
    if is_windows() and prof.get("NetworkCategory") == "Public":
        print("RESULT: NEEDS NETWORK PROFILE FIX — change the trusted network to PRIVATE.")
        return False
    if is_windows() and not fw.get("exists"):
        print("RESULT: NEEDS FIREWALL RULE — choose the safe automatic rule creation above.")
        return False
    print("RESULT: READY — start_lan.py will bind to 0.0.0.0:8000.")
    print(f"STUDENT URL: http://{ip}:{PORT}")
    print("Phones/tablets must be connected to the SAME Wi-Fi/hotspot as this laptop.")
    print("Internet is not required after the one-time software installation.")
    return True

if __name__ == "__main__":
    ok=print_report(auto_fix=True)
    input("\nPress Enter to continue to the quiz server..." if ok else "\nPress Enter to close this diagnostic...")
    if not ok:
        sys.exit(2)
