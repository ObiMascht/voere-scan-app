#!/usr/bin/env python3
"""
VOERE Scan App - Hauptdatei für Buildozer
Optimiert für Android APK-Erstellung
"""

__version__ = '1.0'

# Import der Hauptapp
from Pydroid3_Version import VOEREApp

if __name__ == '__main__':
    print("🚀 VOERE Scan App v1.0 startet...")
    try:
        VOEREApp().run()
    except Exception as e:
        print(f"❌ Fehler beim Starten: {e}")
        import traceback
        traceback.print_exc()
