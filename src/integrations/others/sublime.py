"""
Sublime Text Plugin for NJ IDE Copier.

Receives code from the local server and inserts it at the cursor position.
"""

import sublime
import sublime_plugin
import json
import threading
import http.server


class DeepSeekCopierCommand(sublime_plugin.TextCommand):
    """Insert code from DeepSeek at the current cursor position."""

    def run(self, edit):
        clipboard = sublime.get_clipboard()
        if clipboard:
            for region in self.view.sel():
                self.view.insert(edit, region.begin(), clipboard)
            sublime.status_message("NJ IDE Copier: Code inserted")

    def is_enabled(self):
        return self.view is not None


class DeepSeekServerCommand(sublime_plugin.WindowCommand):
    """Start the NJ IDE Copier server in Sublime Text."""

    server = None

    def run(self):
        if DeepSeekServerCommand.server:
            sublime.status_message("NJ IDE Copier server already running")
            return

        def start():
            handler = type('Handler', (http.server.BaseHTTPRequestHandler,), {
                'do_POST': self.handle_post,
                'log_message': lambda *args: None,
            })
            DeepSeekServerCommand.server = http.server.HTTPServer(('localhost', 8765), handler)
            sublime.status_message("NJ IDE Copier server started on port 8765")
            DeepSeekServerCommand.server.serve_forever()

        thread = threading.Thread(target=start, daemon=True)
        thread.start()

    def handle_post(self):
        pass  # Implementation for handling POST requests


def plugin_loaded():
    """Called when the plugin is loaded."""
    sublime.status_message("NJ IDE Copier plugin loaded")
