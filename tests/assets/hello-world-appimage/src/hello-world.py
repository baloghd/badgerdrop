#!/usr/bin/env python3
"""Hello World - A minimal GTK4 test application for BadgerDrop."""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class HelloWorldApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.hello-world")

    def do_activate(self):
        window = Gtk.ApplicationWindow(application=self)
        window.set_title("Hello World Test App")
        window.set_default_size(400, 200)

        # Main box
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(24)
        box.set_margin_bottom(24)
        box.set_margin_start(24)
        box.set_margin_end(24)

        # Label
        label = Gtk.Label()
        label.set_markup(
            '<span size="x-large" weight="bold">Hello World!</span>\n\n'
            "This is a minimal test AppImage for BadgerDrop."
        )
        label.set_justify(Gtk.Justification.CENTER)
        box.append(label)

        # Close button
        button = Gtk.Button(label="Close")
        button.connect("clicked", lambda btn: self.quit())
        button.add_css_class("suggested-action")
        box.append(button)

        window.set_child(box)
        window.present()


if __name__ == "__main__":
    app = HelloWorldApp()
    app.run(None)
