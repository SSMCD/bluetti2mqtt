import os
import shutil
import subprocess
import time
from threading import Thread

from .log_utils import log
from .led import blink_leds, LoadingAnimation
from .utils import update_status
from .button import delete_files_from_source


def mount_device(device, mountpoint):
    os.makedirs(mountpoint, exist_ok=True)
    result = subprocess.run(['sudo', 'mount', device, mountpoint])
    return result.returncode == 0


def unmount_device(mountpoint):
    subprocess.run(['sudo', 'umount', mountpoint])


def is_device_connected(device_path):
    return os.path.exists(device_path)


def finde_quelle_und_ziel():
    while True:
        output = subprocess.check_output(['lsblk', '-P', '-o', 'NAME,RM,LABEL,TYPE']).decode()
        lines = output.strip().splitlines()
        quelle = None
        ziel = None
        for zeile in lines:
            entry = dict(item.split('=') for item in zeile.strip().split())
            name = entry['NAME'].strip('"')
            typ = entry['TYPE'].strip('"')
            rm = entry['RM'].strip('"')
            label = entry.get('LABEL', '').strip('"')
            if typ != 'part':
                continue
            device = f"/dev/{name}"
            if label == 'BACKUP':
                ziel = device
            elif rm == '1':
                quelle = device
        if not ziel:
            log('⚠️ Backup-Festplatte nicht gefunden. Bitte anschließen.')
            blink_leds((255, 255, 0), 1)
            update_status(state='kein backup ziel', errors=['Backup-Festplatte nicht gefunden'])
            time.sleep(2)
            continue
        if quelle and ziel and quelle != ziel:
            log(f"📥 Quelle: {quelle}")
            log(f"📤 Ziel  : {ziel}")
            update_status(state='bereit', errors=[])
            return quelle, ziel
        blink_leds((0, 0, 255), 1)
        log('🔵 Bitte USB-Stick einstecken...')
        update_status(state='warte auf stick', errors=[])
        time.sleep(2)


def kopiere_daten(quelle, ziel, counter):
    quelle_mount = '/mnt/QUELLE'
    ziel_mount = '/mnt/BACKUP'

    if not mount_device(quelle, quelle_mount):
        log('❌ Fehler beim Mounten der Quelle!')
        blink_leds((255, 0, 0), 10)
        update_status(state='fehler mount quelle', errors=['Fehler beim Mounten der Quelle'])
        return

    if not mount_device(ziel, ziel_mount):
        log('❌ Fehler beim Mounten des Ziels!')
        blink_leds((255, 0, 0), 10)
        unmount_device(quelle_mount)
        update_status(state='fehler mount ziel', errors=['Fehler beim Mounten des Ziels'])
        return

    total_size = 0
    for root, _, files in os.walk(quelle_mount):
        for file in files:
            try:
                total_size += os.path.getsize(os.path.join(root, file))
            except Exception:
                continue
    if total_size == 0:
        log('🟦 Keine Dateien zum Kopieren gefunden!')
        blink_leds((0, 0, 255), 10)
        unmount_device(quelle_mount)
        unmount_device(ziel_mount)
        update_status(state='keine dateien', errors=['Keine Dateien zum Kopieren gefunden'])
        return

    ziel_ordner = os.path.join(ziel_mount, f"USB_Stick_{counter}")
    os.makedirs(ziel_ordner, exist_ok=True)
    copied_size = 0

    log('⚡️ Starte Kopiervorgang...')
    update_status(state='kopiere', progress=0, errors=[])

    progress = 0
    anim = LoadingAnimation(lambda: progress)
    anim.start()

    for root, _, files in os.walk(quelle_mount):
        for file in files:
            src_path = os.path.join(root, file)
            rel_path = os.path.relpath(src_path, quelle_mount)
            dst_path = os.path.join(ziel_ordner, rel_path)
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            try:
                shutil.copy2(src_path, dst_path)
                os.remove(src_path)
            except Exception as e:
                log(f'❌ Fehler beim Kopieren von {src_path}: {e}')
                anim.running = False
                anim.join()
                blink_leds((255, 0, 0), 10)
                unmount_device(quelle_mount)
                unmount_device(ziel_mount)
                update_status(state='fehler kopieren', errors=[f'Fehler beim Kopieren: {e}'])
                return
            copied_size += os.path.getsize(dst_path)
            progress = min((copied_size / total_size) * 100, 100)
            log(f'✅ Kopiert: {rel_path} ({progress:.1f}%)')
            update_status(state='kopiere', progress=progress, errors=[])

    anim.running = False
    anim.join()
    log('✅ Backup erfolgreich abgeschlossen!')
    update_status(state='erfolgreich', progress=100, errors=[])

    while is_device_connected(quelle):
        blink_leds((0, 255, 0), 1)
        time.sleep(1)
    blink_leds((0, 255, 0), 10)
    unmount_device(quelle_mount)
    unmount_device(ziel_mount)


def backup_loop(counter_start=1):
    counter = counter_start
    update_status(state='starte', errors=[])
    while True:
        quelle, ziel = finde_quelle_und_ziel()
        kopiere_daten(quelle, ziel, counter)
        counter += 1
        log('🟦 Warten auf nächsten Stick...')
        update_status(state='warte', errors=[])
        time.sleep(3)
