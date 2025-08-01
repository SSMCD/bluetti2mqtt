import os
import subprocess
import json
from flask import Flask, jsonify, request, send_from_directory
from .config import STATUS_FILE, LOG_FILE
from .led import set_led_enabled, set_led_brightness, LED_ENABLED, get_led_brightness
from .utils import update_status, get_disk_info

app = Flask(__name__, static_folder='web')


@app.route('/')
def index():
    return send_from_directory('web', 'index.html')


@app.route('/api/status')
def api_status():
    if not os.path.exists(STATUS_FILE):
        update_status(state='unbekannt')
    with open(STATUS_FILE, encoding='utf-8') as f:
        return jsonify(json.load(f))


@app.route('/api/log')
def api_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, encoding='utf-8') as f:
            return '<pre>' + f.read() + '</pre>'
    return '<pre>Keine Logs vorhanden.</pre>'


@app.route('/api/led', methods=['GET', 'POST'])
def api_led():
    if request.method == 'POST':
        data = request.json or {}
        if 'enabled' in data:
            set_led_enabled(data['enabled'])
        if 'brightness' in data:
            set_led_brightness(data['brightness'])
        return jsonify({'ok': True})
    else:
        return jsonify({'enabled': LED_ENABLED, 'brightness': get_led_brightness()})

@app.route('/web/<path:path>')
def send_web_static(path):
    return send_from_directory('web', path)

@app.route('/settings')
def settings():
    return send_from_directory('web', 'settings.html')

@app.route('/log')
def log_html():
    return send_from_directory('web', 'log.html')

@app.route('/api/list_drives')
def api_list_drives():
    output = subprocess.check_output(['lsblk', '-P', '-o', 'NAME,RM,SIZE,LABEL,TYPE']).decode()
    drives = []
    for line in output.strip().splitlines():
        entry = dict(item.split('=') for item in line.strip().split())
        name = entry['NAME'].strip('"')
        if entry['TYPE'].strip('"') == 'part' and not name.startswith('mmcblk') and not name.startswith('loop') and not name.startswith('nvme'):
            drives.append({
                'name': name,
                'device': '/dev/' + name,
                'removable': entry['RM'].strip('"'),
                'size': entry['SIZE'].strip('"'),
                'label': entry.get('LABEL', '').strip('"')
            })
    return jsonify(drives)

@app.route('/api/format_drive', methods=['POST'])
def api_format_drive():
    data = request.get_json(force=True)
    device = data.get('device', '')
    label = data.get('label', 'BACKUP')
    if not device or not device.startswith('/dev/'):
        return jsonify({'ok': False, 'msg': 'Ungültiges Gerät!'})
    try:
        subprocess.run(['sudo', 'umount', device], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        res = subprocess.run(['sudo', 'mkfs.exfat', '-n', label, device], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode == 0:
            return jsonify({'ok': True, 'msg': 'Laufwerk erfolgreich formatiert und gelabelt.'})
        return jsonify({'ok': False, 'msg': res.stderr.decode()})
    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)})

@app.route('/api/mount_drive', methods=['POST'])
def api_mount_drive():
    data = request.get_json(force=True)
    device = data.get('device', '')
    mountpoint = data.get('mountpoint', '/mnt/BACKUP')
    if not device or not device.startswith('/dev/'):
        return jsonify({'ok': False, 'msg': 'Ungültiges Gerät!'})
    try:
        os.makedirs(mountpoint, exist_ok=True)
        output = subprocess.check_output(['mount']).decode()
        if mountpoint in output:
            return jsonify({'ok': True, 'msg': 'Bereits gemountet.'})
        res = subprocess.run(['sudo', 'mount', device, mountpoint], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode == 0:
            return jsonify({'ok': True, 'msg': 'Laufwerk erfolgreich gemountet.'})
        return jsonify({'ok': False, 'msg': res.stderr.decode()})
    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)})

@app.route('/api/unmount_drive', methods=['POST'])
def api_unmount_drive():
    data = request.get_json(force=True)
    device = data.get('device', '')
    if not device or not device.startswith('/dev/'):
        return jsonify({'ok': False, 'msg': 'Ungültiges Gerät!'})
    try:
        res = subprocess.run(['sudo', 'umount', device], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode == 0:
            return jsonify({'ok': True, 'msg': 'Laufwerk erfolgreich ausgehängt.'})
        return jsonify({'ok': False, 'msg': res.stderr.decode()})
    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)})

@app.route('/api/set_label_drive', methods=['POST'])
def api_set_label_drive():
    data = request.get_json(force=True)
    device = data.get('device', '')
    label = data.get('label', 'BACKUP')
    if not device or not device.startswith('/dev/'):
        return jsonify({'ok': False, 'msg': 'Ungültiges Gerät!'})
    try:
        subprocess.run(['sudo', 'umount', device], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        res = subprocess.run(['sudo', 'exfatlabel', device, label], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode == 0:
            return jsonify({'ok': True, 'msg': f"Laufwerk-Label erfolgreich auf '{label}' gesetzt."})
        return jsonify({'ok': False, 'msg': res.stderr.decode()})
    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)})
