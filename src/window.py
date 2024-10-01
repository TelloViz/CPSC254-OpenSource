# window.py
#
# Copyright 2023 Nokse
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw
from gi.repository import Gtk
from gi.repository import Gdk, Gio, GObject, GdkPixbuf


from .palette import Palette
from .new_palette_window import NewPaletteDialog

from .tools import *
from .canvas import Canvas

import unicodedata
import os
import webbrowser

class ImageViewer(Gtk.Window):
    def __init__(self):
        super().__init__(title="Image Viewer")
        self.set_default_size(400, 300)

        # Load the image from file
        image_path = path
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file("/home/lollisjosh/Desktop/ascii-draw/data/resources/")
        except Exception as e:
            print(f"Error loading image: {e}")
            return

        # Create an image widget
        image = Gtk.Image.new_from_pixbuf(pixbuf)

        # Add the image to the window
        self.add(image)

@Gtk.Template(resource_path='/io/github/nokse22/asciidraw/ui/window.ui')
class AsciiDrawWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'AsciiDrawWindow'

    overlay_split_view = Gtk.Template.Child()

    toast_overlay = Gtk.Template.Child()

    # Headerbar
    undo_button = Gtk.Template.Child()
    redo_button = Gtk.Template.Child()
    save_import_button = Gtk.Template.Child()
    title_widget = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings.new('io.github.nokse22.asciidraw')

        self.settings.bind("window-width", self, "default-width", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-height", self, "default-height", Gio.SettingsBindFlags.DEFAULT)

        self.styles = [
                ["─", "─", "│", "│", "┌", "┐", "┘","└", "┼", "├", "┤", "┴","┬", "∧", "∨", ">", "<"],
                ["╶", "╶", "╎", "╎", "┌", "┐", "┘","└", "┼", "├", "┤", "┴","┬", "∧", "∨", ">", "<"],
                ["─", "─", "│", "│", "╭", "╮", "╯","╰", "┼", "├", "┤", "┴","┬", "▲", "▼", ">", "<"],
                ["▁", "▔", "▏", "▕", "▁", "▁", "▔","▔", " ", "▏", "▕", "▔","▁", "∧", "∨", ">", "<"],
                ["━", "━", "┃", "┃", "┏", "┓", "┛","┗", "╋", "┣", "┫", "┻","┳", "▲", "▼", "▶", "◀"],
                ["╺", "╺", "╏", "╏", "┏", "┓", "┛","┗", "╋", "┣", "┫", "┻","┳", "▲", "▼", "▶", "◀"],
                ["═", "═", "║", "║", "╔", "╗", "╝","╚", "╬", "╠", "╣", "╩","╦", "A", "V", ">", "<"],
                ["-", "-", "|", "|", "+", "+", "+","+", "+", "+", "+", "+","+", "↑", "↓", "→", "←"],
                ["_", "_", "│", "│", " ", " ", "│","│", "│", "│", "│", "│","_", "▲", "▼", "▶", "◀"],
                ["•", "•", "•", "•", "•", "•", "•","•", "•", "•", "•", "•","•", "▲", "▼", ">", "<"],
                ["·", "·", "·", "·", ".", ".", "'","'", "·", "·", "·", "·","·", "∧", "∨", ">", "<"],
                ["═", "═", "│", "│", "╒", "╕", "╛","╘", "╪", "╞", "╡", "╧","╤", "▲", "▼", "▶", "◀"],
                ["─", "─", "║", "║", "╓", "╖", "╜","╙", "╫", "╟", "╢", "╨","╥", "▲", "▼", ">", "<"],
                ["─", "─", "│", "│", "╔", "╗", "╝","╚", "┼", "├", "┤", "┴","┬", "▲", "▼", ">", "<"],
                ["▄", "▀", "▐", "▌", "▗", "▖", "▘","▝", "▛", "▐", "▌", "▀","▄", "▲", "▼", "▶", "◀"],
                ["▀", "▄", "▌", "▐", "▛", "▜", "▟","▙", "▜", "▙", "▟", "▟","▜", "▲", "▼", "▶", "◀"],
        ]

        text_direction = self.save_import_button.get_child().get_direction()

        if text_direction == Gtk.TextDirection.LTR:
            self.flip = False
        elif text_direction == Gtk.TextDirection.RTL:
            self.flip = True

        self.canvas = Canvas(self.styles, self.flip)
        self.canvas.connect("undo-added", self.on_undo_added)
        self.canvas.connect("undo-removed", self.on_undo_removed)
        self.canvas.connect("redo-removed", self.on_redo_removed)
        self.toast_overlay.set_child(self.canvas)

        prev_btn = None

        for style in self.styles:
            if self.flip:
                name = style[5] + style[1] + style[1] + style[1] + style[4] + " " + style[3] + " " + style[15] + style[1] + style[1] + style[4] + "  " + style[3] + "  "  + style[13] + "\n"
                name += style[3] + "   " + style[2] + " " + style[3] + "    " + style[2] + "  " + style[3] + "  " + style[3] + "\n"
                name += style[6] + style[0] + style[0] + style[0] + style[7] + " " + style[6] + style[0] + style[0] + style[16] + " " + style[2] + "  " + style[14] + "  " + style[3]
            else:
                name = style[4] + style[0] + style[0] + style[0] + style[5] + "  " + style[2] + " " + style[16] + style[0] + style[0] + style[5] + "  " + style[3] + "  "  + style[13] + "\n"
                name += style[2] + "   " + style[3] + "  " + style[2] + "    " + style[3] + "  " + style[3] + "  " + style[3] + "\n"
                name += style[7] + style[1] + style[1] + style[1] + style[6] + "  " + style[7] + style[1] + style[1] + style[15] + " " + style[3] + "  " + style[14] + "  " + style[3]
            label = Gtk.Label(label = name)

        default_palettes_ranges = [
            {"name" : "ASCII", "ranges" : [(0x0020, 0x007F)]},
            {"name" : "Extended ASCII", "ranges" : [(0x00A1, 0x00AD), (0x00AE, 0x0180), (0x0100, 0x0180)]},
            {"name" : "Box Drawing", "ranges" : [(0x2500, 0x2580)]},
            {"name" : "Block Elements", "ranges" : [(0x2580, 0x25A0)]},
            {"name" : "Geometric Shapes", "ranges" : [(0x25A0, 0x25FC), (0x25FF, 0x2600)]},
            {"name" : "Arrows", "ranges" : [(0x2190, 0x21FF)]},
            {"name" : "Mathematical", "ranges" : [(0x2200, 0x22C7), (0x22CB, 0x22EA)]},

        ]

        for raw_palette in default_palettes_ranges:
            palette_chars = ""
            for code_range in raw_palette["ranges"]:
                for code_point in range(code_range[0], code_range[1]):
                    palette_chars += chr(code_point)

            new_palette = Palette(raw_palette["name"], palette_chars)

        self.drawing_area_width = 0

        self.file_path = ""

        self.data_dir = ""

        xdg_data_home = os.environ.get('XDG_DATA_HOME')
        if 'FLATPAK_ID' in os.environ:
            self.data_dir = xdg_data_home
        else:
            if xdg_data_home and xdg_data_home.strip():
                data_dir = os.path.join(xdg_data_home, 'ascii-draw', 'data')
            else:
                home = os.path.expanduser("~")
                data_dir = os.path.join(home, '.local', 'share', 'ascii-draw', 'data')
            self.data_dir = data_dir

        self.palettes = []

        directory_path = f"{self.data_dir}/palettes"
        os.makedirs(directory_path, exist_ok=True)

        for filename in os.listdir(directory_path):
            filepath = os.path.join(directory_path, filename)
            if os.path.isfile(filepath):
                with open(filepath, 'r') as file:
                    chars = file.read().replace("\t", "").replace("\n", "")
                palette_name = os.path.splitext(filename)[0]
                palette = Palette(palette_name, chars)
                self.palettes.append(palette)
                self.add_palette_to_ui(palette)

        self.style_manager = Adw.StyleManager()
        self.style_manager.connect("notify::dark", self.change_theme)

        self.change_theme()

    def open_palettes_dir(self):
        webbrowser.open(f"{self.data_dir}/palettes/")

    def change_theme(self, manager=Adw.StyleManager(), *args):
        self.canvas.color = 1 if manager.get_dark() else 0
        self.canvas.update()

    def show_new_palette_window(self, chars=''):
        win = NewPaletteDialog(self, palette_chars=chars)
        win.present(self)
        win.connect("on-add-clicked", self.on_new_palette_add_clicked)

    def on_new_palette_add_clicked(self, win, palette_name, palette_chars):
        palette = Palette(palette_name, palette_chars)
        self.save_new_palette(palette)
        self.palettes.append(palette)
        self.add_palette_to_ui(palette)

    def add_palette_to_ui(self, palette):
        flow_box = Gtk.FlowBox(homogeneous=True, selection_mode=0, margin_top=3, margin_bottom=3, margin_start=3, margin_end=3, valign=Gtk.Align.START)
        for char in palette.chars:
            new_button = Gtk.Button(label=char, css_classes=["flat", "ascii"])
            new_button.connect("clicked", self.change_char, flow_box)
            new_button.set_has_tooltip(True)
            new_button.connect("query-tooltip", self.on_show_char_tooltip, char)
            flow_box.append(new_button)
        scrolled_window = Gtk.ScrolledWindow(name=palette.name, hexpand=True, vexpand=True)
        scrolled_window.set_child(flow_box)
        self.chars_carousel.append(scrolled_window)

        pos = self.chars_carousel.get_position()
        if pos != self.chars_carousel.get_n_pages() - 1:
            self.char_carousel_go_next.set_sensitive(True)

    def on_show_char_tooltip(self, btn, x, y, keyboard, tooltip, _char):
        builder = Gtk.Builder.new_from_resource("/io/github/nokse22/asciidraw/ui/unicode_tooltip.ui")

        main_box = builder.get_object("main_box")
        char_label = builder.get_object("char_label")
        unicode_label = builder.get_object("unicode_label")
        char_name_label = builder.get_object("char_name_label")

        char_label.set_label(_char)
        unicode_label.set_label(f"U+{hex(ord(_char))[2:].upper().rjust(4, '0')}")
        char_name_label.set_label(unicodedata.name(_char).title())

        tooltip.set_custom(main_box)

        return True

    def save_new_palette(self, palette):
        with open(f"{self.data_dir}/palettes/{palette.name}.txt", 'w') as file:
            file.write(palette.chars)

    @Gtk.Template.Callback("save_button_clicked")
    def save_button_clicked(self, btn):
        self.save()

    def save(self, callback=None):
        if self.file_path != "":
            self.save_file(self.file_path)
            if callback:
                callback()
            return
        self.open_save_file_chooser(callback)

    def open_file(self):
        if not self.canvas.is_saved:
            self.save_changes_message(self.open_file_callback)
        else:
            self.open_file_callback()

    def open_file_callback(self):
        dialog = Gtk.FileDialog(
            title=_("Open File"),
        )
        dialog.open(self, None, self.on_open_file_response)
        self.canvas.clear_preview()

    def on_open_file_response(self, dialog, response):
        file = dialog.open_finish(response)
        print(f"Selected File: {file.get_path()}")

        if file:
            path = file.get_path()
            try:
                with open(path, 'r') as file:
                    input_string = file.read()
                self.canvas.set_content(input_string)
                self.file_path = path
                file_name = os.path.basename(self.file_path)
                self.title_widget.set_subtitle(file_name)
            except IOError:
                print(f"Error reading {path}.")

    def brightness_to_ascii(self, brightness):
        # Wide range of ASCII characters from dark to light
        ascii_chars = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'."

        # Map brightness to the appropriate ASCII character
        index = int(brightness * (len(ascii_chars) - 1))  # Scale brightness to index range
        return ascii_chars[index]


    def pixbuf_to_rgb_hsb(self, pixels, width, height, channels, rowstride):
        rgb_values = []
        hsb_values = []

        for y in range(height):
            for x in range(width):
                # Calculate pixel's position in the byte array
                pixel_index = y * rowstride + x * channels
                r = pixels[pixel_index]
                g = pixels[pixel_index + 1]
                b = pixels[pixel_index + 2]

                # Store RGB values
                rgb_values.append((r, g, b))

                # Convert RGB to HSB
                h, s, v = self.rgb_to_hsb(r, g, b)
                hsb_values.append((h, s, v))

        return rgb_values, hsb_values

    def rgb_to_hsb(self, r, g, b):
        # Normalize RGB values to the range [0, 1]
        rd = r / 255.0
        gd = g / 255.0
        bd = b / 255.0

        # Find the maximum and minimum RGB values
        max_val = max(rd, gd, bd)
        min_val = min(rd, gd, bd)
        delta = max_val - min_val

        # Calculate Hue
        if delta == 0:
            h = 0
        elif max_val == rd:
            h = 60 * (((gd - bd) / delta) % 6)
        elif max_val == gd:
            h = 60 * (((bd - rd) / delta) + 2)
        else:
            h = 60 * (((rd - gd) / delta) + 4)

        if h < 0:
            h += 360

        # Calculate Saturation
        s = 0 if max_val == 0 else (delta / max_val)

        # Brightness is just the max value
        v = max_val

        return h, s, v

    def import_image(self):
        print("import_image called")

        # copy/pasted code from open_file()
        if not self.canvas.is_saved:
            self.save_changes_message(self.import_image_callback)
        else:
            self.import_image_callback()

    # Copied open_file_callback(self) function
    def import_image_callback(self):
        dialog = Gtk.FileDialog(
            title=_("Import Image"),
        )
        dialog.open(self, None, self.on_import_image_response)
        self.canvas.clear_preview()

    # Copied on_open_file_response(self, dialog, response) function
    def on_import_image_response(self, dialog, response):
        file = dialog.open_finish(response)
        print(f"Selected File: {file.get_path()}")

        if file:
            path = file.get_path()
            try:
                # Load an image from a file
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)

                pixels = pixbuf.get_pixels()
                width = pixbuf.get_width()
                height = pixbuf.get_height()
                channels = pixbuf.get_n_channels()
                rowstride = pixbuf.get_rowstride()

                rgb, hsb = self.pixbuf_to_rgb_hsb(pixels, width, height, channels, rowstride)

                # Print the RGB and HSB values for demonstration
                # for i in range(len(rgb)):
                #     print(f"RGB: {rgb[i]}, HSB: {hsb[i]}")

                # for i in range(len(rgb)):
                #     print(f"{hsb[i][2]}")

                output_path = os.path.expanduser("~/Desktop/ascii-draw/output.txt")
                # Open the specified path for writing
                with open(output_path, 'w') as file_out:
                    for y in range(height):
                        for x in range(width):
                            # Correctly calculate the index for the HSB values
                            pixel_index = (y * rowstride + x * channels)  # Accessing the RGB values
                            brightness = hsb[pixel_index // channels][2]  # Accessing brightness value
                            ascii_char = self.brightness_to_ascii(brightness)  # Get ASCII character based on brightness
                            file_out.write(ascii_char)  # Write the ASCII character
                        file_out.write("\n")  # New line after each row

                print(f"HSB values written to {output_path}")

                try:
                    with open(output_path, 'r') as file:
                        input_string = file.read()
                    self.canvas.set_content(input_string)
                    self.file_path = path
                    file_name = os.path.basename(self.file_path)
                    self.title_widget.set_subtitle(file_name)
                except IOError:
                    print(f"Error reading {path}.")

            except IOError:
                print(f"Error reading {path}.")

    def new_canvas(self):
        if not self.canvas.is_saved:
            self.save_changes_message(self.make_new_canvas)
        else:
            self.make_new_canvas()

    def save_changes_message(self, callback=None):
        dialog = Adw.AlertDialog(
            heading=_("Save Changes?"),
            body=_("The opened file contains unsaved changes. Changes which are not saved will be permanently lost."),
            close_response="cancel",
        )

        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("discard", _("Discard"))
        dialog.add_response("save", _("Save"))

        dialog.set_response_appearance("discard", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_response_appearance("save", Adw.ResponseAppearance.SUGGESTED)

        dialog.choose(self, None, self.on_save_changes_message_response, callback)

    def on_save_changes_message_response(self, dialog, task, callback=None):
        response = dialog.choose_finish(task)
        print(f'Selected "{response}" response.')
        match response:
            case "discard":
                if callback:
                    callback()
            case "save":
                self.save(callback)
            case "cancel":
                pass

    def make_new_canvas(self):
        self.canvas.wipe_canvas()
        self.canvas.clear_preview()
        self.canvas.change_canvas_size(40, 20)
        self.file_path = ""
        self.title_widget.set_subtitle("")
        self.canvas.undo_changes = []
        self.canvas.redo_changes = []
        self.undo_button.set_sensitive(False)
        self.undo_button.set_tooltip_text("")
        self.redo_button.set_sensitive(False)
        self.redo_button.set_tooltip_text("")
        self.canvas.is_saved = True
        toast = Adw.Toast(title=_("New Canvas"), timeout=2)
        self.toast_overlay.add_toast(toast)

    def save_as_action(self):
        self.open_save_file_chooser()

    def open_save_file_chooser(self, callback=None):
        dialog = Gtk.FileDialog(
            title=_("Save File"),
            initial_name=_("drawing.txt"),
        )
        dialog.save(self, None, self.on_save_file_response, callback)

    def on_save_file_response(self, dialog, response, callback=None):
        try:
            file = dialog.save_finish(response)
        except Exception:
            return

        print(f"Selected File: {file.get_path()}")

        if file:
            file_path = file.get_path()
            self.save_file(file_path)

            if callback:
                callback()

    def save_file(self, file_path):
        self.file_path = file_path
        file_name = os.path.basename(file_path)
        self.title_widget.set_subtitle(file_name)
        try:
            with open(file_path, 'w') as file:
                file.write(self.canvas.get_content())
            print(f"Content written to {file_path} successfully.")
            toast = Adw.Toast(title=_("Saved successfully"), timeout=2)
            self.toast_overlay.add_toast(toast)
            self.canvas.is_saved = True
        except IOError:
            print(f"Error writing to {file_path}.")
    def copy_to_clipboard(self):
        text = self.canvas.get_content()

        clipboard = Gdk.Display().get_default().get_clipboard()
        clipboard.set(text)

    def on_style_changed(self, btn, box):
        child = box.get_first_child()
        index = 1
        while child != None:
            if child.get_active():
                self.style = index
                self.canvas.style = index
                break
            child = child.get_next_sibling()
            index += 1

        self.tree_tool.preview()
        self.table_tool.preview()

    def on_delete_clicked(self):
        if self.move_tool.active:
            self.move_tool.delete_selection()

    def new_palette_from_canvas(self):
        content = self.canvas.get_content()
        content = content.replace('\n', '')
        unique_chars = set()

        for char in content:
            if char not in unique_chars:
                unique_chars.add(char)

        unique_string = ''.join(sorted(unique_chars))

        self.show_new_palette_window(unique_string)

    def on_undo_added(self, widget, undo_name):
        self.undo_button.set_sensitive(True)
        self.undo_button.set_tooltip_text(_("Undo") + " " + undo_name)

    def on_undo_removed(self, widget):
        if len(self.canvas.undo_changes) == 0:
            self.undo_button.set_sensitive(False)
            self.undo_button.set_tooltip_text("")
        else:
            self.undo_button.set_tooltip_text(_("Undo ") + self.canvas.undo_changes[-1].name)

        self.redo_button.set_sensitive(True)
        self.redo_button.set_tooltip_text(_("Redo ") + self.canvas.redo_changes[-1].name)

    def on_redo_removed(self, widget):
        if len(self.canvas.redo_changes) == 0:
            self.redo_button.set_sensitive(False)
            self.redo_button.set_tooltip_text("")
        else:
            self.redo_button.set_tooltip_text(_("Redo ") + self.canvas.redo_changes[-1].name)

    @Gtk.Template.Callback("undo_first_change")
    def undo_first_change(self, *args):
        self.canvas.undo()

    @Gtk.Template.Callback("redo_last_change")
    def redo_last_change(self, *args):
        self.canvas.redo()

