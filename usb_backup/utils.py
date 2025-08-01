import os
import json
import subprocess
import time
from .config import STATUS_FILE
from .log_utils import log


def get_disk_info():
    try:
        output = subprocess.check_output(['lsblk', '-P', '-o', 'NAME,LABEL,MOUNTPOINT,TYPE']).decode()
        for line in output.strip().splitlines():
            entry = dict(item.split('=') for item in line.strip().split())
            label = entry.get('LABEL', '').strip('"')
            name = entry.get('NAME', '').strip('"')
            mountpoint = entry.get('MOUNTPOINT', '').strip('"')
            typ = entry.get('TYPE', '').strip('"')
            if label == 'BACKUP' and typ == 'part':
                device = f"/dev/{name}"
                if not mountpoint:
                    mountpoint = '/mnt/BACKUP'
                    os.makedirs(mountpoint, exist_ok=True)
                    res = subprocess.run(['sudo', 'mount', device, mountpoint], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if res.returncode != 0:
                        return {
                            'total': 'Nicht gemountet',
                            'used': '-',
                            'free': '-',
                            'total_raw': 0,
                            'used_raw': 0,
                            'free_raw': 0
                        }
                st = os.statvfs(mountpoint)
                total = st.f_blocks * st.f_frsize
                free = st.f_bavail * st.f_frsize
                used = total - free
                total_gb = round(total / (1024 ** 3), 1)
                used_gb = round(used / (1024 ** 3), 1)
                free_gb = round(free / (1024 ** 3), 1)
                return {
                    'total': f'{total_gb} GB',
                    'used': f'{used_gb} GB',
                    'free': f'{free_gb} GB',
                    'total_raw': int(total // (1024 ** 2)),
                    'used_raw': int(used // (1024 ** 2)),
                    'free_raw': int(free // (1024 ** 2))
                }
    except Exception as e:
        log(f'Fehler beim Lesen der Festplatteninfos: {e}')
    return {
        'total': 'Nicht verbunden',
        'used': 'Nicht verbunden',
        'free': 'Nicht verbunden',
        'total_raw': 0,
        'used_raw': 0,
        'free_raw': 0
    }


def update_status(progress=0, state='warten', errors=None):
    if errors is None:
        errors = []
    status = {
        'progress': progress,
        'state': state,
        'errors': errors,
        'disk': get_disk_info()
    }
    with open(STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(status, f)
