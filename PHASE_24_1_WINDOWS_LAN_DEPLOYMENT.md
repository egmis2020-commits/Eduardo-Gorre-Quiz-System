# V24.2 — Windows LAN Deployment & Connectivity

## Objective
Make a new Windows teacher laptop self-diagnosing for classroom LAN access.

## Startup sequence
`start_lan.bat` runs `lan_setup.py` before importing Flask. This means missing Python packages are reported clearly instead of producing a generic traceback.

### Checks
1. Python version and executable path.
2. Required Python packages.
3. Active Windows network profile.
4. LAN IPv4 and gateway.
5. TCP port 8000 availability.
6. Dedicated Windows Defender Firewall rule for TCP 8000.
7. Final student URL.

## Safe firewall behavior
V24.2 never disables Windows Defender Firewall or antivirus. If the dedicated rule is missing, the teacher may approve a standard UAC prompt to create:

- Direction: Inbound
- Protocol: TCP
- Local port: 8000
- Profile: Private only
- Edge traversal: Block
- Display name: `EGMIS TLE CSS Quiz - LAN TCP 8000`

## Why this fixes common new-laptop failures
A phone can reach the quiz only when:
- the server is listening on the teacher laptop,
- the teacher laptop has a usable LAN IPv4 address,
- the phone is on the same LAN/hotspot,
- Windows permits inbound TCP 8000 on that trusted Private network.

V24.2 reports these conditions separately instead of telling the teacher to disable security controls.

## If the network is Public
Change only the trusted school/home network to **Private** in Windows Settings. V24.2 intentionally does not create a broad Public-network firewall exception.

## If the port is already in use
V24.2 reports the Windows `netstat` owner information and stops before launching Flask. Do not terminate an unknown process automatically.

## Python 3.14
V24.2 checks package availability before importing the app. It does not claim compatibility merely because Python starts. If a required package cannot be installed for the selected Python version, the launcher reports the package problem.

## Offline operation
Internet is not required for quiz operation after the one-time Python/package setup. LAN mode remains the default and SQLite remains the source of truth.
