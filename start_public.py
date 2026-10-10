import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
URL_FILE = BASE_DIR / 'public_url.txt'
URL_RE = re.compile(r'https://[a-z0-9-]+\.trycloudflare\.com', re.I)


def find_cloudflared():
    exe = shutil.which('cloudflared')
    if exe:
        return exe
    candidates = [
        Path(os.environ.get('USERPROFILE', '')) / 'cloudflared.exe',
        Path('C:/Program Files/cloudflared/cloudflared.exe'),
        Path('C:/Program Files (x86)/cloudflared/cloudflared.exe'),
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


def run_server():
    os.environ.pop('QUIZ_PUBLIC_URL', None)
    import app
    app.init_db()
    try:
        from waitress import serve
        serve(app.app, host='0.0.0.0', port=8000, threads=12,
              channel_timeout=120, asyncore_use_poll=True,
              expose_tracebacks=False)
    except ImportError:
        app.app.run(host='0.0.0.0', port=8000, debug=False,
                    use_reloader=False, threaded=True)


def origin_ready():
    for _ in range(30):
        try:
            with urllib.request.urlopen('http://127.0.0.1:8000/login', timeout=2) as r:
                if 200 <= r.status < 500:
                    return True
        except Exception:
            time.sleep(0.5)
    return False


def start_tunnel(cloudflared):
    # Quick Tunnels are temporary. If the connector dies, restart it so the
    # teacher gets a fresh working URL instead of leaving a dead URL behind.
    return subprocess.Popen(
        [cloudflared, 'tunnel', '--protocol', 'http2', '--no-autoupdate',
         '--url', 'http://127.0.0.1:8000'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )


def main():
    cloudflared = find_cloudflared()
    if not cloudflared:
        print('\nCloudflare Tunnel is not installed.')
        print('Install it with:')
        print('  winget install --id Cloudflare.cloudflared')
        sys.exit(1)

    try:
        URL_FILE.unlink()
    except FileNotFoundError:
        pass

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    print('\n' + '=' * 68)
    print('       TLE-ICT CSS QUIZ - PUBLIC CLASSROOM SERVER')
    print('=' * 68)
    print('Local origin: http://127.0.0.1:8000')
    print('Waiting for the local quiz server before starting Cloudflare...')

    if not origin_ready():
        print('\nERROR: The quiz server did not become ready on port 8000.')
        print('Check the Python/Flask error above and try again.')
        sys.exit(1)

    print('Origin is ready.')
    print('Cloudflare Quick Tunnel will automatically restart if its connector stops.')
    print('IMPORTANT: Every Quick Tunnel restart creates a NEW public URL.')
    print('Keep this window open while students are taking the quiz.')
    print('=' * 68 + '\n')

    current_proc = None
    try:
        while True:
            current_proc = start_tunnel(cloudflared)
            found_url = False
            for line in current_proc.stdout:
                print(line, end='')
                match = URL_RE.search(line)
                if match and not found_url:
                    url = match.group(0).rstrip('/')
                    URL_FILE.write_text(url, encoding='utf-8')
                    found_url = True
                    print('\n' + '=' * 68)
                    print('PUBLIC STUDENT ACCESS:')
                    print(url)
                    print('QR code on the Teacher Dashboard now uses this URL.')
                    print('If this URL ever shows Cloudflare Error 1033,')
                    print('the tunnel connector has stopped; this launcher will restart it.')
                    print('After a restart, scan the NEW QR code shown on the dashboard.')
                    print('=' * 68 + '\n')
            code = current_proc.wait()
            print(f'\nCloudflare connector stopped (exit code {code}).')
            print('Restarting a fresh Quick Tunnel in 3 seconds...')
            try:
                URL_FILE.unlink()
            except FileNotFoundError:
                pass
            time.sleep(3)
    except KeyboardInterrupt:
        print('\nStopping public server...')
    finally:
        if current_proc is not None and current_proc.poll() is None:
            current_proc.terminate()
            try:
                current_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                current_proc.kill()
        try:
            URL_FILE.unlink()
        except FileNotFoundError:
            pass


os.environ['QUIZ_ACCESS_MODE'] = 'public'

if __name__ == '__main__':
    main()
