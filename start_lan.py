"""V24.1 Windows LAN/offline launcher with automatic safe connectivity checks."""
import os, sys, webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
os.environ['QUIZ_ACCESS_MODE'] = 'lan'

# Preflight runs before importing Flask so missing packages are diagnosed clearly.
setup = BASE_DIR / "lan_setup.py"
if setup.exists():
    import subprocess
    result = subprocess.run([sys.executable, str(setup)], cwd=str(BASE_DIR))
    if result.returncode != 0:
        sys.exit(result.returncode)

from app import app, init_db, get_lan_ip
from waitress import serve

def print_terminal_qr(url):
    try:
        import qrcode
        qr = qrcode.QRCode(version=None, box_size=1, border=1)
        qr.add_data(url)
        qr.make(fit=True)
        matrix = qr.get_matrix()
        print("\nQR CODE — STUDENT ACCESS")
        for row in matrix:
            print("".join("██" if cell else "  " for cell in row))
        print()
    except Exception as exc:
        print(f"[WARNING] Could not render QR code in terminal: {exc}")

if __name__ == '__main__':
    init_db()
    lan_ip = get_lan_ip()
    url = f'http://{lan_ip}:8000'
    print('\n' + '=' * 72)
    print('       EGMIS TLE-ICT-CSS QUIZ SERVER — V24.4 LAN / OFFLINE')
    print('=' * 72)
    print('Internet required for quiz use: NO')
    print('Teacher access:                 http://127.0.0.1:8000')
    print(f'Student/phone access:           {url}')
    print('Binding:                         0.0.0.0:8000')
    print('Firewall:                        Private-network TCP 8000 only')
    print('Server:                          Waitress (production LAN server)')
    print('Public access:                   OPTIONAL — use start_public.bat')
    print('=' * 72)
    print_terminal_qr(url)
    print('IMPORTANT: Keep this window open while students are taking the quiz.')
    print('If phones cannot connect, stop here and read the PRE-FLIGHT result above.')
    print('Press Ctrl+C to stop the server.\n')
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        serve(app, host='0.0.0.0', port=8000, threads=16, connection_limit=256, backlog=1024, channel_timeout=120)
    except KeyboardInterrupt:
        print('\nServer stopped.')
