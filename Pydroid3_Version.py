import os
import shutil
from datetime import datetime
from PIL import Image
from PIL import Image as PILImage
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import BooleanProperty
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.image import Image as KivyImage
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import SlideTransition
import cv2
from kivy.properties import StringProperty

# SPEZIELLE VERSION FÜR PYDROID 3
print("=== PYDROID 3 VERSION ===")
print("App startet...")

# Für Pydroid 3 - Verwende das interne App-Verzeichnis
try:
    # Pydroid 3 spezifische Pfade
    from android.storage import primary_external_storage_path
    from android.permissions import request_permissions, Permission

    # Berechtigungen explizit anfordern
    request_permissions([
        Permission.READ_EXTERNAL_STORAGE,
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.CAMERA
    ])

    # Pydroid 3 Pfade
    external_path = primary_external_storage_path()
    print(f"External Storage Path: {external_path}")

    # Mögliche Kamera-Pfade für Pydroid 3
    possible_paths = [
        os.path.join(external_path, 'DCIM', 'Camera'),
        os.path.join(external_path, 'Pictures'),
        os.path.join(external_path, 'DCIM'),
        '/storage/emulated/0/DCIM/Camera',
        '/storage/emulated/0/Pictures',
        '/sdcard/DCIM/Camera',
        '/sdcard/Pictures'
    ]

    IMAGE_FOLDER = None
    for path in possible_paths:
        if os.path.exists(path) and os.access(path, os.R_OK):
            try:
                # Test ob wir wirklich lesen können
                test_files = os.listdir(path)
                IMAGE_FOLDER = path
                print(f"✓ Kamera-Pfad gefunden: {IMAGE_FOLDER}")
                print(f"  Anzahl Dateien: {len(test_files)}")
                break
            except (OSError, PermissionError) as e:
                print(f"✗ Kein Zugriff auf {path}: {e}")
                continue

    # Fallback
    if IMAGE_FOLDER is None:
        IMAGE_FOLDER = os.path.join(external_path, 'DCIM', 'Camera')
        print(f"⚠ Fallback-Pfad: {IMAGE_FOLDER}")

except ImportError:
    print("Android-Module nicht verfügbar - vermutlich auf PC")
    # Fallback für PC/Development
    possible_paths = [
        r'C:\voere\test',
        r'C:\Users\Public\Pictures',
        os.path.expanduser('~/Pictures')
    ]

    IMAGE_FOLDER = None
    for path in possible_paths:
        if os.path.exists(path):
            IMAGE_FOLDER = path
            break

    if IMAGE_FOLDER is None:
        IMAGE_FOLDER = r'C:\voere\test'

except Exception as e:
    print(f"Fehler bei Android-Initialisierung: {e}")
    IMAGE_FOLDER = '/storage/emulated/0/DCIM/Camera'

print(f"Finaler IMAGE_FOLDER: {IMAGE_FOLDER}")

# Für Pydroid 3 - Verwende lokale Ordner statt Netzlaufwerke
try:
    # Versuche externes Verzeichnis zu verwenden
    if 'external_path' in locals():
        SAVE_FOLDER_IMAGE = os.path.join(external_path, 'VOERE_Scan', 'Images')
        SAVE_FOLDER_VIDEO = os.path.join(external_path, 'VOERE_Scan', 'Videos')
        SAVE_FOLDER_IMAGE_SERIAL = os.path.join(
            external_path, 'VOERE_Scan', 'Serial_Images')
        SAVE_FOLDER_VIDEO_SERIAL = os.path.join(
            external_path, 'VOERE_Scan', 'Serial_Videos')
    else:
        # Fallback für PC
        SAVE_FOLDER_IMAGE = r'C:\voere\test\output\images'
        SAVE_FOLDER_VIDEO = r'C:\voere\test\output\videos'
        SAVE_FOLDER_IMAGE_SERIAL = r'C:\voere\test\output\serial_images'
        SAVE_FOLDER_VIDEO_SERIAL = r'C:\voere\test\output\serial_videos'

    print(f"Save folders erstellt unter: {SAVE_FOLDER_IMAGE}")

except Exception as e:
    print(f"Fehler bei Save-Folder Setup: {e}")
    # Original Netzwerk-Pfade als Fallback
    SAVE_FOLDER_IMAGE = r'\\voe-og-ser-04\Einkauf\Rechnungseingang\Scan\Test'
    SAVE_FOLDER_VIDEO = r'\\voe-og-ser-04\Einkauf\Rechnungseingang\Scan\Test'
    SAVE_FOLDER_IMAGE_SERIAL = r'\\voe-og-ser-04\Einkauf\Rechnungseingang\Scan_WB\Test'
    SAVE_FOLDER_VIDEO_SERIAL = r'\\voe-og-ser-04\Einkauf\Rechnungseingang\Scan_WB\Test'

# Ensure folders exist
print("Erstelle Verzeichnisse...")
directories_to_create = [
    os.path.join(IMAGE_FOLDER, 'thumbnails'),
    SAVE_FOLDER_IMAGE,
    SAVE_FOLDER_VIDEO,
    SAVE_FOLDER_IMAGE_SERIAL,
    SAVE_FOLDER_VIDEO_SERIAL
]

for directory in directories_to_create:
    try:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Verzeichnis: {directory}")
    except Exception as e:
        print(f"✗ Fehler bei {directory}: {e}")

KV = '''
ScreenManager:
    MainMenuScreen:
    ImageScreen:
    VideoScreen:
    SerialImageScreen:
    SerialVideoScreen:

<MainMenuScreen>:
    name: 'main_menu'
    BoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "VOERE SCAN (Pydroid3)"
            font_size: "120sp"
            md_bg_color: '#FF7F00'
            specific_text_color: "#000000"
            elevation: 10

        MDBoxLayout:
            orientation: 'vertical'
            size_hint_y: 2.3
            md_bg_color: '#333333'
            spacing: dp(10)
            padding: dp(27)

            MDRaisedButton:
                text: "[size=60]Bilder[/size]\\n[size=50]Fertigungsauftrag\\nKundenauftrag\\nwebshop[/size]"
                markup: True
                halign: "center"
                md_bg_color: '#FF7F00'
                text_color: 'black'
                pos: 800, 0
                size_hint_x: 1
                size_hint_y: 3
                pos_hint: {'center_x':0.5}
                on_release: app.change_screen('image_screen')

            MDRaisedButton:
                text: "[size=60]Videos[/size] (in Arbeit)\\n[size=50]Fertigungsauftrag\\nKundenauftrag\\nwebshop[/size]"
                markup: True
                halign: "center"
                md_bg_color: '#FF7F00'
                text_color: 'black'
                size_hint_x: 1
                size_hint_y: 3
                pos_hint: {'center_x':0.5}
                on_release: app.change_screen('video_screen')

            MDRaisedButton:
                text: "[size=60]Bilder[/size]\\n[size=50]Endkontrolle Waffe\\nReparaturauftrag Waffe[/size]"
                markup: True
                halign: "center"
                md_bg_color: '#FF7F00'
                text_color: 'black'
                size_hint_x: 1
                size_hint_y: 3
                pos_hint: {'center_x':0.5}
                on_release: app.change_screen('serial_image_screen')
                
            MDRaisedButton:
                text: "[size=60]Videos[/size] (in Arbeit)\\n[size=50]Endkontrolle Waffe\\nReparaturauftrag Waffe[/size]"
                markup: True
                halign: "center"
                md_bg_color: '#FF7F00'
                text_color: 'black'
                size_hint_x: 1
                size_hint_y: 3
                pos_hint: {'center_x':0.5}
                on_release: app.change_screen('serial_video_screen')

<ImageScreen>:
    name: 'image_screen'
    BoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "Bilder auswählen"
            md_bg_color: '#FF7F00'
            specific_text_color: "#000000"
            elevation: 10

        MDLabel:
            text: "Erstes Bild muss mit QR-Code sein"
            font_size: "20sp"
            md_bg_color: '#FF7F00'
            text_color: 'black'
            padding: dp(30)
            size_hint: 2, 0.1
            pos_hint: {'center_x':0.5}
            halign: "center"

        MDBoxLayout:
            orientation: 'vertical'
            size_hint_y: 2.3
            md_bg_color: '#333333'
            spacing: dp(2)
            padding: dp(20)

            MDRaisedButton:
                text: "Zurück zum Hauptmenü"
                font_size: "20sp"
                md_bg_color: '#FF7F00'
                text_color: 'black'
                pos: 800, 0
                padding: dp(30)
                size_hint: 0.8, None
                pos_hint: {'center_x':0.5}
                on_release: app.change_screen('main_menu', back=True)

            ScrollView:
                GridLayout:
                    id: image_grid
                    cols: 1
                    spacing: dp(100)
                    padding: dp(90)
                    size_hint_y: None
                    height: self.minimum_height
                    row_default_height: 130
                    row_force_default: True

            MDRaisedButton:
                text: "Speichern"
                font_size: "20sp"
                md_bg_color: '#FF7F00'
                text_color: 'black'
                padding: dp(30)
                size_hint: 0.8, None
                pos_hint: {'center_x':0.5}
                on_release: app.convert_images_to_pdf()

<VideoScreen>:
    name: 'video_screen'
    BoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "Videos auswählen"
            md_bg_color: '#FF7F00'
            specific_text_color: "#000000"
            elevation: 10

        MDBoxLayout:
            orientation: 'vertical'
            size_hint_y: 2.3
            md_bg_color: '#333333'
            spacing: dp(2)
            padding: dp(20)

            MDRaisedButton:
                text: "Zurück zum Hauptmenü"
                font_size: "20sp"
                md_bg_color: '#FF7F00'
                text_color: 'black'
                pos: 800, 0
                padding: dp(30)
                size_hint: 0.8, None
                pos_hint: {'center_x':0.5}
                on_release: app.change_screen('main_menu', back=True)

            ScrollView:
                GridLayout:
                    id: image_grid
                    cols: 1
                    spacing: dp(100)
                    padding: dp(90)
                    size_hint_y: None
                    height: self.minimum_height
                    row_default_height: 130
                    row_force_default: True

            MDRaisedButton:
                text: "Speichern"
                font_size: "20sp"
                md_bg_color: '#FF7F00'
                text_color: 'black'
                padding: dp(30)
                size_hint: 0.8, None
                pos_hint: {'center_x':0.5}
                on_release: app.save_selected_videos()

<SerialImageScreen>:
    name: 'serial_image_screen'
    BoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "Bilder auswählen"
            md_bg_color: '#FF7F00'
            specific_text_color: "#000000"
            elevation: 10

        MDLabel:
            text: "Erstes Bild muss mit QR-Code sein"
            font_size: "20sp"
            md_bg_color: '#FF7F00'
            text_color: 'black'
            padding: dp(30)
            size_hint: 2, 0.1
            pos_hint: {'center_x':0.5}
            halign: "center"

        MDBoxLayout:
            orientation: 'vertical'
            size_hint_y: 2.3
            md_bg_color: '#333333'
            spacing: dp(2)
            padding: dp(20)

            MDRaisedButton:
                text: "Zurück zum Hauptmenü"
                font_size: "20sp"
                md_bg_color: '#FF7F00'
                text_color: 'black'
                pos: 800, 0
                padding: dp(30)
                size_hint: 0.8, None
                pos_hint: {'center_x':0.5}
                on_release: app.change_screen('main_menu', back=True)

            ScrollView:
                GridLayout:
                    id: image_grid
                    cols: 1
                    spacing: dp(100)
                    padding: dp(90)
                    size_hint_y: None
                    height: self.minimum_height
                    row_default_height: 130
                    row_force_default: True

            MDRaisedButton:
                text: "Speichern"
                font_size: "20sp"
                md_bg_color: '#FF7F00'
                text_color: 'black'
                padding: dp(30)
                size_hint: 0.8, None
                pos_hint: {'center_x':0.5}
                on_release: app.serial_convert_images_to_pdf()

<SerialVideoScreen>:
    name: 'serial_video_screen'
    BoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "Videos auswählen"
            md_bg_color: '#FF7F00'
            specific_text_color: "#000000"
            elevation: 10

        MDBoxLayout:
            orientation: 'vertical'
            size_hint_y: 2.3
            md_bg_color: '#333333'
            spacing: dp(2)
            padding: dp(20)

            MDRaisedButton:
                text: "Zurück zum Hauptmenü"
                font_size: "20sp"
                md_bg_color: '#FF7F00'
                text_color: 'black'
                pos: 800, 0
                padding: dp(30)
                size_hint: 0.8, None
                pos_hint: {'center_x':0.5}
                on_release: app.change_screen('main_menu', back=True)

            ScrollView:
                GridLayout:
                    id: image_grid
                    cols: 1
                    spacing: dp(100)
                    padding: dp(90)
                    size_hint_y: None
                    height: self.minimum_height
                    row_default_height: 130
                    row_force_default: True

            MDRaisedButton:
                text: "Speichern"
                font_size: "20sp"
                md_bg_color: '#FF7F00'
                text_color: 'black'
                padding: dp(30)
                size_hint: 0.8, None
                pos_hint: {'center_x':0.5}
                on_release: app.serial_save_selected_videos()
'''

Window.size = (360, 640)  # Set window size for easier testing


class SelectableImage(ToggleButtonBehavior, KivyImage):
    selected = BooleanProperty(False)
    original_path = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_path = kwargs.get("original_path", "")

    def on_state(self, widget, state):
        if state == 'down':
            self.selected = True
            self.color = (0, 1, 0, 1)
        else:
            self.selected = False
            self.color = (1, 1, 1, 1)
        MDApp.get_running_app().on_image_selected(self)


class MainMenuScreen(MDScreen):
    pass


def create_thumbnail(img_path, thumb_path):
    try:
        if img_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            with PILImage.open(img_path) as img:
                img.thumbnail((400, 400))
                img.save(thumb_path)
        elif img_path.lower().endswith(('.mp4', '.mov', '.wmv', '.avi')):
            vidcap = cv2.VideoCapture(img_path)
            success, image = vidcap.read()
            if success:
                pil_image = PILImage.fromarray(
                    cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                pil_image.thumbnail((300, 300))
                pil_image.save(thumb_path)
            vidcap.release()
        else:
            raise ValueError("Unsupported file type for thumbnail creation")
    except Exception as e:
        print(f"Fehler beim Erstellen des Thumbnails für {img_path}: {e}")


def show_error_dialog(title, message):
    """Hilfsfunktion für Fehlerdialoge"""
    dialog = MDDialog(
        title=title,
        text=message,
        buttons=[MDFlatButton(
            text="OK", on_release=lambda x: dialog.dismiss())],
    )
    dialog.open()
    return dialog


def find_image_folders():
    """Sucht alle Ordner mit Bildern und gibt sie zurück"""
    print("=== SUCHE NACH BILD-ORDNERN ===")

    # Alle möglichen Pfade erweitern
    try:
        from android.storage import primary_external_storage_path
        external_path = primary_external_storage_path()
        base_paths = [external_path, '/storage/emulated/0', '/sdcard']
    except ImportError:
        base_paths = ['/storage/emulated/0', '/sdcard']
    except Exception:
        base_paths = ['/storage/emulated/0', '/sdcard']

    # Erweiterte Pfad-Liste
    search_paths = []
    for base in base_paths:
        if base and os.path.exists(base):
            search_paths.extend([
                os.path.join(base, 'DCIM', 'Camera'),
                os.path.join(base, 'DCIM'),
                os.path.join(base, 'Pictures'),
                os.path.join(base, 'Pictures', 'Screenshots'),
                os.path.join(base, 'Download'),
                os.path.join(base, 'WhatsApp', 'Media', 'WhatsApp Images'),
                os.path.join(base, 'Instagram'),
                os.path.join(base, 'Snapchat'),
                base  # Root-Ordner selbst
            ])

    # Zusätzliche bekannte Pfade
    search_paths.extend([
        '/storage/emulated/0/DCIM/Camera',
        '/storage/emulated/0/Pictures',
        '/storage/emulated/0/Download',
        '/sdcard/DCIM/Camera',
        '/sdcard/Pictures'
    ])

    found_folders = []

    for path in set(search_paths):  # set() um Duplikate zu entfernen
        if not path or not os.path.exists(path):
            continue

        try:
            all_files = os.listdir(path)
            image_files = [f for f in all_files if f.lower().endswith(
                ('.png', '.jpg', '.jpeg', '.gif'))]

            if image_files:
                found_folders.append({
                    'path': path,
                    'image_count': len(image_files),
                    'total_files': len(all_files),
                    # Erste 3 Bilder als Beispiel
                    'sample_files': image_files[:3]
                })
                print(f"✓ {path} - {len(image_files)} Bilder gefunden")
            else:
                print(f"○ {path} - Ordner leer oder keine Bilder")

        except PermissionError:
            print(f"✗ {path} - Keine Berechtigung")
        except Exception as e:
            print(f"✗ {path} - Fehler: {e}")

    # Sortiere nach Anzahl der Bilder (absteigend)
    found_folders.sort(key=lambda x: x['image_count'], reverse=True)

    print(f"=== GEFUNDEN: {len(found_folders)} Ordner mit Bildern ===")
    return found_folders


class ImageScreen(MDScreen):
    def on_enter(self):
        print("ImageScreen: on_enter aufgerufen")
        self.load_images()

    def load_images(self):
        print(f"ImageScreen: Lade Bilder aus {IMAGE_FOLDER}")
        self.ids.image_grid.clear_widgets()

        if not os.path.exists(IMAGE_FOLDER):
            print(f"Fehler: Kamera-Ordner nicht gefunden: {IMAGE_FOLDER}")
            show_error_dialog(
                "Kamera-Ordner nicht gefunden",
                f"Der Ordner '{IMAGE_FOLDER}' wurde nicht gefunden.\nBitte überprüfen Sie die Berechtigungen oder verwenden Sie einen anderen Pfad."
            )
            return

        try:
            all_files = os.listdir(IMAGE_FOLDER)
            print(f"Gefundene Dateien: {len(all_files)}")

            images = sorted(
                [f for f in all_files if f.lower().endswith(
                    ('.png', '.jpg', '.jpeg', '.gif'))],
                key=lambda x: os.path.getmtime(os.path.join(IMAGE_FOLDER, x)),
                reverse=True
            )[:20]

            print(f"Gefilterte Bilder: {len(images)}")

            if not images:
                print("Keine Bilder im Standard-Ordner - suche in anderen Ordnern...")
                # Suche in allen verfügbaren Ordnern
                found_folders = find_image_folders()

                if found_folders:
                    # Zeige die besten Alternativen
                    alternatives = found_folders[:3]  # Zeige top 3

                    alt_text = "Gefundene Alternativen:\n"
                    for folder in alternatives:
                        alt_text += f"• {folder['path']}: {folder['image_count']} Bilder\n"
                        sample_files_str = ', '.join(folder['sample_files'])
                        alt_text += f"  Beispiele: {sample_files_str}\n\n"

                    # Dialog mit "Ordner wechseln" Button
                    def switch_to_best_folder(*args):
                        global IMAGE_FOLDER
                        IMAGE_FOLDER = found_folders[0]['path']
                        print(f"Wechsle zu bestem Ordner: {IMAGE_FOLDER}")
                        dialog.dismiss()
                        self.load_images()  # Neu laden

                    dialog = MDDialog(
                        title="Keine Bilder im Standard-Ordner",
                        text=f"Standard-Ordner: '{IMAGE_FOLDER}'\n\n{alt_text}"
                        "Tipp: Machen Sie ein paar Fotos mit der Kamera-App!",
                        buttons=[
                            MDFlatButton(text="Besten Ordner verwenden",
                                         on_release=switch_to_best_folder),
                            MDFlatButton(text="OK",
                                         on_release=lambda x: dialog.dismiss())
                        ],
                    )
                    dialog.open()
                else:
                    # Keine Bilder gefunden - biete Testbilder-Erstellung an
                    def create_test_images_action(*args):
                        dialog.dismiss()
                        self.create_test_images_on_device()

                    def open_camera_tip(*args):
                        dialog.dismiss()
                        show_error_dialog(
                            "Kamera-Anleitung",
                            "1. Öffnen Sie die Kamera-App\n"
                            "2. Machen Sie 3-5 Testfotos\n"
                            "3. Kommen Sie zur VOERE App zurück\n"
                            "4. Klicken Sie erneut auf 'Bilder'"
                        )

                    dialog = MDDialog(
                        title="Keine Bilder auf dem Gerät",
                        text="Es wurden keine Bilder in den verfügbaren Ordnern gefunden.\n\n"
                             "Was möchten Sie tun?",
                        buttons=[
                            MDFlatButton(text="Testbilder erstellen",
                                         on_release=create_test_images_action),
                            MDFlatButton(text="Kamera öffnen",
                                         on_release=open_camera_tip),
                            MDFlatButton(text="Abbrechen",
                                         on_release=lambda x: dialog.dismiss())
                        ],
                    )
                    dialog.open()
                return

        except PermissionError as e:
            print(f"Berechtigung fehlt: {e}")
            show_error_dialog(
                "Berechtigung fehlt",
                f"Keine Berechtigung für Zugriff auf '{IMAGE_FOLDER}'.\nBitte erteilen Sie der App Speicher-Berechtigungen in den Android-Einstellungen."
            )
            return
        except Exception as e:
            print(f"Fehler beim Laden der Bilder: {e}")
            show_error_dialog(
                "Fehler", f"Fehler beim Laden der Bilder: {str(e)}")
            return

        for filename in images:
            img_path = os.path.join(IMAGE_FOLDER, filename)
            thumb_path = os.path.join(IMAGE_FOLDER, 'thumbnails', filename)

            try:
                if not os.path.exists(thumb_path):
                    create_thumbnail(img_path, thumb_path)

                image = SelectableImage(
                    source=thumb_path if os.path.exists(
                        thumb_path) else img_path,
                    original_path=img_path,
                    allow_stretch=True,
                    size_hint=(None, None),
                    size=(400, 400)
                )
                self.ids.image_grid.add_widget(image)
                print(f"Bild hinzugefügt: {filename}")

            except Exception as e:
                print(f"Fehler bei Bild {filename}: {e}")
                continue

    def create_test_images_on_device(self):
        """Erstellt Testbilder direkt auf dem Gerät"""
        print("Erstelle Testbilder auf dem Gerät...")

        # Finde schreibbaren Ordner
        test_folders = [
            '/storage/emulated/0/DCIM/Camera',
            '/storage/emulated/0/Pictures',
            '/storage/emulated/0/Download'
        ]

        target_folder = None
        for folder in test_folders:
            if os.path.exists(folder):
                try:
                    # Test ob schreibbar
                    test_file = os.path.join(folder, '.test_write')
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                    target_folder = folder
                    break
                except Exception:
                    continue

        if not target_folder:
            show_error_dialog(
                "Fehler",
                "Kein schreibbarer Ordner gefunden.\nBitte überprüfen Sie die App-Berechtigungen."
            )
            return

        # Erstelle Testbilder
        try:
            from PIL import Image

            test_images = [
                {'name': 'VOERE_Test_QR.jpg', 'color': (255, 255, 255)},
                {'name': 'VOERE_Test_1.jpg', 'color': (255, 100, 100)},
                {'name': 'VOERE_Test_2.jpg', 'color': (100, 255, 100)},
                {'name': 'VOERE_Test_3.jpg', 'color': (100, 100, 255)}
            ]

            created_count = 0
            for img_info in test_images:
                try:
                    img = Image.new('RGB', (800, 600), img_info['color'])
                    filepath = os.path.join(target_folder, img_info['name'])
                    img.save(filepath, 'JPEG', quality=85)
                    created_count += 1
                except Exception as e:
                    print(f"Fehler bei {img_info['name']}: {e}")

            if created_count > 0:
                # Update IMAGE_FOLDER und neu laden
                global IMAGE_FOLDER
                IMAGE_FOLDER = target_folder

                show_error_dialog(
                    "Testbilder erstellt!",
                    f"{created_count} Testbilder wurden in '{target_folder}' erstellt.\n\n"
                    f"Die Bilderliste wird automatisch aktualisiert."
                )

                # Neu laden
                self.load_images()
            else:
                show_error_dialog(
                    "Fehler",
                    "Testbilder konnten nicht erstellt werden."
                )

        except ImportError:
            show_error_dialog(
                "Fehler",
                "PIL (Python Imaging Library) ist nicht verfügbar.\n"
                "Bitte machen Sie manuell Fotos mit der Kamera-App."
            )
        except Exception as e:
            show_error_dialog(
                "Fehler",
                f"Fehler beim Erstellen der Testbilder: {str(e)}"
            )


class VideoScreen(MDScreen):
    def on_enter(self):
        print("VideoScreen: on_enter aufgerufen")
        self.load_videos()

    def load_videos(self):
        print(f"VideoScreen: Lade Videos aus {IMAGE_FOLDER}")
        self.ids.image_grid.clear_widgets()

        if not os.path.exists(IMAGE_FOLDER):
            print(f"Fehler: Kamera-Ordner nicht gefunden: {IMAGE_FOLDER}")
            show_error_dialog(
                "Kamera-Ordner nicht gefunden",
                f"Der Ordner '{IMAGE_FOLDER}' wurde nicht gefunden."
            )
            return

        try:
            all_files = os.listdir(IMAGE_FOLDER)
            videos = sorted(
                [f for f in all_files if f.lower().endswith(
                    ('.mp4', '.mov', '.wmv', '.avi'))],
                key=lambda x: os.path.getmtime(os.path.join(IMAGE_FOLDER, x)),
                reverse=True
            )[:20]

            print(f"Gefundene Videos: {len(videos)}")

            if not videos:
                show_error_dialog(
                    "Keine Videos gefunden",
                    f"Im Ordner '{IMAGE_FOLDER}' wurden keine Videos gefunden."
                )
                return

        except PermissionError as e:
            print(f"Berechtigung fehlt: {e}")
            show_error_dialog(
                "Berechtigung fehlt",
                f"Keine Berechtigung für Zugriff auf '{IMAGE_FOLDER}'."
            )
            return
        except Exception as e:
            print(f"Fehler beim Laden der Videos: {e}")
            show_error_dialog(
                "Fehler", f"Fehler beim Laden der Videos: {str(e)}")
            return

        for filename in videos:
            video_path = os.path.join(IMAGE_FOLDER, filename)
            thumb_path = os.path.join(
                IMAGE_FOLDER, 'thumbnails', filename.rsplit('.', 1)[0] + '.jpg')

            try:
                if not os.path.exists(thumb_path):
                    create_thumbnail(video_path, thumb_path)

                image = SelectableImage(
                    source=thumb_path if os.path.exists(
                        thumb_path) else video_path,
                    original_path=video_path,
                    allow_stretch=True,
                    size_hint=(None, None),
                    size=(400, 400)
                )
                self.ids.image_grid.add_widget(image)
                print(f"Video hinzugefügt: {filename}")

            except Exception as e:
                print(f"Fehler bei Video {filename}: {e}")
                continue


class SerialImageScreen(MDScreen):
    def on_enter(self):
        self.load_images()

    def load_images(self):
        self.ids.image_grid.clear_widgets()

        if not os.path.exists(IMAGE_FOLDER):
            show_error_dialog("Kamera-Ordner nicht gefunden",
                              f"Der Ordner '{IMAGE_FOLDER}' wurde nicht gefunden.")
            return

        try:
            images = sorted(
                [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(
                    ('.png', '.jpg', '.jpeg', '.gif'))],
                key=lambda x: os.path.getmtime(os.path.join(IMAGE_FOLDER, x)),
                reverse=True
            )[:20]

        except PermissionError:
            show_error_dialog(
                "Berechtigung fehlt", f"Keine Berechtigung für Zugriff auf '{IMAGE_FOLDER}'.")
            return
        except Exception as e:
            show_error_dialog(
                "Fehler", f"Fehler beim Laden der Bilder: {str(e)}")
            return

        for filename in images:
            img_path = os.path.join(IMAGE_FOLDER, filename)
            thumb_path = os.path.join(IMAGE_FOLDER, 'thumbnails', filename)

            try:
                if not os.path.exists(thumb_path):
                    create_thumbnail(img_path, thumb_path)

                image = SelectableImage(
                    source=thumb_path if os.path.exists(
                        thumb_path) else img_path,
                    original_path=img_path,
                    allow_stretch=True,
                    size_hint=(None, None),
                    size=(400, 400)
                )
                self.ids.image_grid.add_widget(image)

            except Exception as e:
                print(f"Fehler bei Bild {filename}: {e}")
                continue


class SerialVideoScreen(MDScreen):
    def on_enter(self):
        self.load_videos()

    def load_videos(self):
        self.ids.image_grid.clear_widgets()

        if not os.path.exists(IMAGE_FOLDER):
            show_error_dialog("Kamera-Ordner nicht gefunden",
                              f"Der Ordner '{IMAGE_FOLDER}' wurde nicht gefunden.")
            return

        try:
            videos = sorted(
                [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(
                    ('.mp4', '.mov', '.wmv', '.avi'))],
                key=lambda x: os.path.getmtime(os.path.join(IMAGE_FOLDER, x)),
                reverse=True
            )[:20]

        except PermissionError:
            show_error_dialog(
                "Berechtigung fehlt", f"Keine Berechtigung für Zugriff auf '{IMAGE_FOLDER}'.")
            return
        except Exception as e:
            show_error_dialog(
                "Fehler", f"Fehler beim Laden der Videos: {str(e)}")
            return

        for filename in videos:
            video_path = os.path.join(IMAGE_FOLDER, filename)
            thumb_path = os.path.join(
                IMAGE_FOLDER, 'thumbnails', filename.rsplit('.', 1)[0] + '.jpg')

            try:
                if not os.path.exists(thumb_path):
                    create_thumbnail(video_path, thumb_path)

                image = SelectableImage(
                    source=thumb_path if os.path.exists(
                        thumb_path) else video_path,
                    original_path=video_path,
                    allow_stretch=True,
                    size_hint=(None, None),
                    size=(400, 400)
                )
                self.ids.image_grid.add_widget(image)

            except Exception as e:
                print(f"Fehler bei Video {filename}: {e}")
                continue


class VOEREApp(MDApp):
    def build(self):
        self.selected_images = []
        print("App wird gebaut...")
        return Builder.load_string(KV)

    def change_screen(self, screen_name, back=False):
        print(f"Wechsel zu Screen: {screen_name}")
        transition = SlideTransition(direction='left' if not back else 'right')
        self.root.transition = transition
        self.root.current = screen_name

    def add_image_to_selection(self, image):
        if image.selected:
            if image.original_path not in self.selected_images:
                self.selected_images.append(image.original_path)
        else:
            if image.original_path in self.selected_images:
                self.selected_images.remove(image.original_path)

    def convert_images_to_pdf(self):
        if not self.selected_images:
            show_error_dialog("Fehler", "Keine Bilder ausgewählt.")
            return

        try:
            images = []
            for file in self.selected_images:
                img = Image.open(file)
                img = img.convert('RGB')
                images.append(img)

            now = datetime.now().isoformat().replace(
                "T", "_").replace(":", "-").replace(".", "-")
            save_path = os.path.join(SAVE_FOLDER_IMAGE, f"{now}.pdf")

            # Stelle sicher, dass das Verzeichnis existiert
            os.makedirs(SAVE_FOLDER_IMAGE, exist_ok=True)

            images[0].save(save_path, save_all=True, append_images=images[1:])

            show_error_dialog("Erfolg", f"PDF gespeichert: {save_path}")

        except Exception as e:
            show_error_dialog(
                "Fehler", f"PDF konnte nicht gespeichert werden: {str(e)}")

        self.change_screen('main_menu')

    def save_selected_videos(self):
        current_screen = self.root.get_screen('video_screen')

        if not hasattr(current_screen.ids, 'image_grid'):
            show_error_dialog("Fehler", "Kein Grid gefunden")
            return

        selected_videos = [
            img.original_path for img in current_screen.ids.image_grid.children if img.selected
        ]

        if not selected_videos:
            show_error_dialog("Fehler", "Keine Videos ausgewählt.")
            return

        try:
            os.makedirs(SAVE_FOLDER_VIDEO, exist_ok=True)

            for video_path in selected_videos:
                video_name = os.path.basename(video_path)
                shutil.copy(video_path, os.path.join(
                    SAVE_FOLDER_VIDEO, video_name))

            show_error_dialog(
                "Erfolg", f"Videos gespeichert in: {SAVE_FOLDER_VIDEO}")

        except Exception as e:
            show_error_dialog(
                "Fehler", f"Videos konnten nicht gespeichert werden: {str(e)}")

        self.change_screen('main_menu')

    def serial_convert_images_to_pdf(self):
        if not self.selected_images:
            show_error_dialog("Fehler", "Keine Bilder ausgewählt.")
            return

        try:
            images = []
            for file in self.selected_images:
                img = Image.open(file)
                img = img.convert('RGB')
                images.append(img)

            now = datetime.now().isoformat().replace(
                "T", "_").replace(":", "-").replace(".", "-")
            save_path = os.path.join(SAVE_FOLDER_IMAGE_SERIAL, f"{now}.pdf")

            os.makedirs(SAVE_FOLDER_IMAGE_SERIAL, exist_ok=True)

            images[0].save(save_path, save_all=True, append_images=images[1:])

            show_error_dialog("Erfolg", f"PDF gespeichert: {save_path}")

        except Exception as e:
            show_error_dialog(
                "Fehler", f"PDF konnte nicht gespeichert werden: {str(e)}")

        self.change_screen('main_menu')

    def on_image_selected(self, image):
        self.add_image_to_selection(image)

    def serial_save_selected_videos(self):
        selected_videos = [
            img.original_path
            for img in self.root.get_screen('serial_video_screen').ids.image_grid.children
            if img.selected
        ]

        if not selected_videos:
            show_error_dialog("Fehler", "Keine Videos ausgewählt.")
            return

        try:
            os.makedirs(SAVE_FOLDER_VIDEO_SERIAL, exist_ok=True)

            for video_path in selected_videos:
                video_name = os.path.basename(video_path)
                shutil.copy(video_path, os.path.join(
                    SAVE_FOLDER_VIDEO_SERIAL, video_name))

            show_error_dialog(
                "Erfolg", f"Videos gespeichert in: {SAVE_FOLDER_VIDEO_SERIAL}")

        except Exception as e:
            show_error_dialog(
                "Fehler", f"Videos konnten nicht gespeichert werden: {str(e)}")

        self.change_screen('main_menu')


if __name__ == '__main__':
    print("Starte VOERE App...")
    try:
        VOEREApp().run()
    except Exception as e:
        print(f"Fehler beim Starten der App: {e}")
        import traceback
        traceback.print_exc()
