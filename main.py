from threading import Thread
from assistant.state import AppState
from assistant.overlay import OverlayIndicator
from assistant.listener import WakeWordListener
from assistant.tray import TrayApp

def main():
    state = AppState()

    overlay = OverlayIndicator(state)
    overlay_thread = Thread(target=overlay.run, daemon=True, name="overlay")
    overlay_thread.start()

    listener = WakeWordListener(state, overlay)
    listener_thread = Thread(target=listener.run, daemon=True, name="listener")
    listener_thread.start()

    #TrayApp.run() #blocks on the main thread until Quit
    tray = TrayApp(state, listener, overlay)
    #listener.setTray(tray) # allows listener to signal tray to update menu
    tray.run()


if __name__ == "__main__":
    main()
