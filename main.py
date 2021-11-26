from os import path
import gi
import requests

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject

builder = Gtk.Builder()
builder.add_from_file(path.join(path.abspath(path.dirname(__file__)), "ui.glade"))

window = builder.get_object("window1")
keybuffer = builder.get_object("key_textbuffer")
userSearch = builder.get_object("user_search")
keyListStore = builder.get_object("liststore1")

global gpg_keys, ssh_keys
gpg_keys = []
ssh_keys = []

class Handler:
    def window1_destroy(self, *args):
        Gtk.main_quit()

    def user_search_activate(self, *args):
        user = userSearch.get_text()
        gpg_request = requests.get("https://api.github.com/users/"+user+"/gpg_keys")
        ssh_request = requests.get("https://api.github.com/users/"+user+"/keys")
        keyListStore.clear()
        keybuffer.set_text("")
        if gpg_request.status_code != 200 or ssh_request.status_code != 200:
            keybuffer.set_text("Key retrieval failed, check your connection or make sure the username exists")
            return
        global gpg_keys, ssh_keys
        gpg_keys = gpg_request.json()
        ssh_keys = ssh_request.json()

        if len(gpg_keys) == 0 and len(ssh_keys) == 0:
            keybuffer.set_text("The user " + user + " has no SSH or GPG keys on their GitHub account")

        for key in ssh_keys:
            keyListStore.append(["ssh: "+str(key["id"])])

        for key in gpg_keys:
            keyListStore.append(["gpg: "+key["key_id"]])

    def key_tree_cursor_changed(self, data):
        selectedPath, selectedColumn = data.get_cursor()
        if selectedPath is None:
            return
        selectedPath = selectedPath.get_indices()[0]

        if selectedPath < len(ssh_keys):
            keybuffer.set_text(ssh_keys[selectedPath]["key"])
        else:
            keybuffer.set_text(gpg_keys[selectedPath-len(ssh_keys)]["raw_key"])

builder.connect_signals(Handler())
window.show_all()
Gtk.main()
