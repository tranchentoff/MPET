import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import subprocess
import webbrowser
import threading
import time
import pyautogui
import os
import screeninfo
from datetime import datetime
import mss
import shutil
import tempfile
import requests

# === CONFIGURATION ===

# Définition des couleurs pour le mode sombre et clair
dark_mode = True
bg_color = "#1c1c3c" if dark_mode else "#ffffff"
btn_bg = "#333333" if dark_mode else "#f0f0f0"
btn_fg = "#ffffff" if dark_mode else "#000000"
highlight = "#00c9ff" if dark_mode else "#ff6600"

# Chemins des programmes
DISCORD_PATH = r"C:\Users\%USERNAME%\AppData\Local\Discord\Update.exe --processStart Discord.exe"
GHUB_PATH = r"C:\Program Files\LGHUB\lghub.exe"
TELEGRAM_PATH = r"C:\Program Files\WindowsApps\TelegramMessengerLLP.TelegramDesktop_5.12.3.0_x64__t4vj0pshhgkwm\Telegram.exe"

# Fortnite config
FORTNITE_URL = "https://www.xbox.com/fr-FR/play/launch/fortnite/BT5P2X999VH2"
CHROME_PATH = '"C:/Program Files/Google/Chrome/Application/chrome.exe" --start-fullscreen --kiosk %s'

# Dossier des icônes
ICON_FOLDER = "C:/Users/Utilisateur/Desktop/Menu pratique/icons"

# Dossier de sauvegarde des captures
screenshot_dir = r"C:\Users\Utilisateur\Desktop\Menu pratique\screenshots"

# === FONCTIONS DE BASE ===

# Définir le mode sombre/clair
dark_mode = True

def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    if dark_mode:
        bg_color = "#1c1c3c"
        btn_bg = "#333333"
        btn_fg = "#ffffff"
        highlight = "#00c9ff"
    else:
        bg_color = "#ffffff"
        btn_bg = "#f0f0f0"
        btn_fg = "#000000"
        highlight = "#ff6600"
    update_ui(bg_color, btn_bg, btn_fg, highlight)

def update_ui(bg_color, btn_bg, btn_fg, highlight):
    root.configure(bg=bg_color)
    label.config(bg=bg_color, fg=btn_fg)
    status_label.config(bg=bg_color, fg=btn_fg)
    for widget in root.winfo_children():
        if isinstance(widget, tk.Button):
            widget.config(bg=btn_bg, fg=btn_fg, activebackground=highlight, activeforeground="white")
        elif isinstance(widget, tk.Label):
            widget.config(bg=bg_color, fg=btn_fg)
        elif isinstance(widget, ttk.Combobox):
            widget.config(bg=btn_bg, fg=btn_fg)

# === FONCTIONS D'INSTALLATION ===

logiciels = {
    "Discord": "https://discord.com/api/downloads/distributions/app/installers/latest?channel=stable&platform=win&arch=x64",
    "Telegram": "https://telegram.org/dl/desktop/win64",
    "Logitech G Hub": "https://download01.logi.com/web/ftp/pub/techsupport/gaming/lghub_installer.exe",
    "Python (latest)": "https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe"
}

checkbox_vars = {}

def ouvrir_fenetre_installation():
    fenetre = tk.Toplevel(root)
    fenetre.title("Installer des logiciels")
    fenetre.configure(bg=bg_color)
    
    tk.Label(fenetre, text="Sélectionnez les logiciels à installer :", font=("Arial", 12, "bold"), bg=bg_color, fg=btn_fg).pack(pady=10)

    for nom in logiciels.keys():
        var = tk.BooleanVar()
        cb = tk.Checkbutton(fenetre, text=nom, variable=var, font=("Arial", 12), bg=bg_color, fg=btn_fg, selectcolor=highlight, activebackground=bg_color)
        cb.pack(anchor='w', padx=20)
        checkbox_vars[nom] = var

    bouton_installer = tk.Button(fenetre, text="Installer la sélection", command=valider_installation,
                                 bg=highlight, fg='white', font=("Arial", 12, "bold"))
    bouton_installer.pack(pady=15)

def valider_installation():
    selection = [nom for nom, var in checkbox_vars.items() if var.get()]
    if not selection:
        messagebox.showwarning("Aucun logiciel", "Veuillez sélectionner au moins un logiciel à installer.")
        return
    
    threading.Thread(target=telecharger_et_installer, args=(selection,), daemon=True).start()

def telecharger_et_installer(selection):
    for nom in selection:
        url = logiciels[nom]
        telecharger_installeur(nom, url)

def telecharger_installeur(nom, url):
    try:
        status_label.config(text=f"Téléchargement de {nom}...", fg="blue")
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"{nom}_setup.exe")

        # Télécharger le fichier d'installation en arrière-plan
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Vérifie les erreurs de téléchargement

        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        status_label.config(text=f"{nom} téléchargé ✅", fg="green")

        # Lancer l'installation en mode silencieux
        # L'argument "/S" fonctionne pour beaucoup de programmes Windows pour une installation silencieuse
        subprocess.Popen([file_path, '/S'], shell=True)  # '/S' pour installation silencieuse
    except requests.exceptions.RequestException as e:
        status_label.config(text=f"Erreur de téléchargement {nom}: {str(e)}", fg="red")
        messagebox.showerror("Erreur", f"Erreur de téléchargement pour {nom}: {str(e)}")
    except Exception as e:
        status_label.config(text=f"Erreur avec {nom}: {str(e)}", fg="red")
        messagebox.showerror("Erreur", f"Erreur pour {nom}: {str(e)}")

# === FONCTIONS PRINCIPALES ===

def start_timer_60min():
    global timer_thread, stop_timer
    if timer_thread and timer_thread.is_alive():
        stop_timer = True
        timer_thread.join()
    stop_timer = False
    timer_thread = threading.Thread(target=run_timer_60min, daemon=True)
    timer_thread.start()

def run_timer_60min():
    total_seconds = 60 * 60  # 60 minutes
    for elapsed in range(total_seconds + 1):
        if stop_timer:
            return
        remaining = total_seconds - elapsed
        minutes, seconds = divmod(remaining, 60)
        timer_label.config(text=f"Temps restant : {minutes:02}:{seconds:02}")
        progress = (elapsed / total_seconds) * 100
        progress_bar['value'] = progress
        time.sleep(1)
    status_label.config(text="⏰ Timer terminé !", fg="orange")

def ouvrir_fortnite():
    webbrowser.get(CHROME_PATH).open(FORTNITE_URL)
    time.sleep(2)
    pyautogui.press('f11')
    status_label.config(text="Fortnite lancé en plein écran ✅", fg="green")

def lancer_minecraft():
    minecraft_uri = "minecraft://"  # URI pour ouvrir Minecraft directement
    try:
        webbrowser.open(minecraft_uri)  # Ouvre Minecraft via l'URI
        status_label.config(text="Minecraft lancé ✅", fg="green")
    except Exception as e:
        status_label.config(text=f"Erreur lors du lancement de Minecraft", fg="red")
        messagebox.showerror("Erreur", f"Erreur : {str(e)}")

def lancer_app(path, nom):
    try:
        subprocess.Popen(path, shell=True)
        status_label.config(text=f"{nom} lancé ✅", fg="green")
    except Exception as e:
        status_label.config(text=f"Erreur lors du lancement de {nom}", fg="red")

def prendre_capture_ecran():
    try:
        ecran_choisi = ecran_combo.get()
        ecrans = screeninfo.get_monitors()

        with mss.mss() as sct:
            if ecran_choisi == "Écran principal":
                capture = sct.grab(sct.monitors[1])
            else:
                ecran_index = int(ecran_choisi.split()[1]) - 1
                ecran_selectionne = ecrans[ecran_index]
                capture = sct.grab({
                    "top": ecran_selectionne.y,
                    "left": ecran_selectionne.x,
                    "width": ecran_selectionne.width,
                    "height": ecran_selectionne.height
                })

        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        capture_path = os.path.join(screenshot_dir, f"{timestamp}.png")
        capture_image = Image.frombytes("RGB", (capture.width, capture.height), capture.rgb)
        capture_image.save(capture_path)

        status_label.config(text="Capture d'écran enregistrée !", fg="green")
    except Exception as e:
        status_label.config(text=f"Erreur : {str(e)}", fg="red")
        messagebox.showerror("Erreur", f"Une erreur s'est produite lors de la capture d'écran : {str(e)}")

def reset_screenshots():
    confirmation = messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer tous les screenshots ?")
    if confirmation:
        try:
            if os.path.exists(screenshot_dir):
                for filename in os.listdir(screenshot_dir):
                    file_path = os.path.join(screenshot_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                status_label.config(text="Tous les screenshots ont été supprimés.", fg="green")
            else:
                messagebox.showwarning("Dossier introuvable", "Le dossier des screenshots n'existe pas.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur s'est produite : {str(e)}")

# Définir la variable globale timer_thread
timer_thread = None
stop_timer = False

def start_timer_60min():
    global timer_thread, stop_timer
    if timer_thread and timer_thread.is_alive():
        stop_timer = True
        timer_thread.join()  # Attendre que le thread précédent se termine
    stop_timer = False
    timer_thread = threading.Thread(target=run_timer_60min, daemon=True)
    timer_thread.start()


# === INTERFACE ===

root = tk.Tk()
root.title("Menu Pratique - Edition Tranchent")
root.geometry("450x1100")
root.resizable(False, False)
root.configure(bg=bg_color)

# Titre
label = tk.Label(root, text="Menu Pratique\nEnderman Edition 🟪⬛", font=("Arial", 18, "bold"), fg=btn_fg, bg=bg_color)
label.pack(pady=15)

# Sélecteur d'écran
ecrans = screeninfo.get_monitors()
ecran_options = ["Écran principal"]
for i, ecran in enumerate(ecrans, start=1):
    ecran_options.append(f"Écran {i}")

frame_bas = tk.Frame(root, bg=bg_color)
frame_bas.pack(side="bottom", fill="both", pady=20)

ecran_label = tk.Label(frame_bas, text="Choisir un écran", font=("Arial", 12), fg=btn_fg, bg=bg_color)
ecran_label.pack(side="left", padx=10)

ecran_combo = ttk.Combobox(frame_bas, values=ecran_options, state="readonly", font=("Arial", 12))
ecran_combo.set("Écran principal")
ecran_combo.pack(side="left", padx=10)

# Affichage timer et barre de progression
timer_label = tk.Label(root, text="Temps restant : 60:00", font=("Arial", 14, "bold"), fg=btn_fg, bg=bg_color)
timer_label.pack(pady=20)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate", maximum=100, value=0)
progress_bar.pack(pady=20)

status_label = tk.Label(root, text="Statut: Prêt", font=("Arial", 12), fg="gray", bg=bg_color)
status_label.pack(pady=10)

# Boutons
toggle_button = tk.Button(root, text="Basculer le thème", command=toggle_theme, bg=highlight, fg='white', font=("Arial", 12, "bold"))
toggle_button.pack(pady=10)

# Ajouter les boutons pour lancer les programmes
def bouton_avec_icone(icon_name, text, command):
    icon_path = os.path.join(ICON_FOLDER, icon_name)
    if os.path.exists(icon_path):
        img = Image.open(icon_path)
        img = img.resize((30, 30))
        icon = ImageTk.PhotoImage(img)
        btn = tk.Button(root, text=text, command=command, image=icon, compound="left", bg=btn_bg, fg=btn_fg)
        btn.image = icon  # Keep a reference to avoid garbage collection
        btn.pack(pady=5)
    else:
        print(f"Icone {icon_name} introuvable")

# Ajouter les boutons avec icônes
# Boutons
bouton_avec_icone("discord.png", "Lancer Discord", lambda: lancer_app(DISCORD_PATH, "Discord"))
bouton_avec_icone("ghub.png", "Lancer Logitech G Hub", lambda: lancer_app(GHUB_PATH, "Logitech G Hub"))
bouton_avec_icone("telegram.png", "Lancer Telegram", lambda: lancer_app(TELEGRAM_PATH, "Telegram"))
bouton_avec_icone("fortnite.png", "Lancer Fortnite (Plein écran)", lambda: threading.Thread(target=ouvrir_fortnite, daemon=True).start())
bouton_avec_icone("screenshot.png", "Prendre capture d'écran", lambda: threading.Thread(target=prendre_capture_ecran, daemon=True).start())
bouton_avec_icone("reset.png", "Réinitialiser les screenshots", lambda: threading.Thread(target=reset_screenshots, daemon=True).start())
bouton_avec_icone("timer.png", "Lancer minuteur 60 min", start_timer_60min)
bouton_avec_icone("minecraft.png", "Lancer Minecraft Bedrock", lancer_minecraft)
bouton_avec_icone("install.png", "Installer Logiciels", ouvrir_fenetre_installation)


root.mainloop()
