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

    # Tools
    free_button = Gtk.Template.Child()
    rectangle_button = Gtk.Template.Child()
    filled_rectangle_button = Gtk.Template.Child()
    line_button = Gtk.Template.Child()
    move_button = Gtk.Template.Child()
    text_button = Gtk.Template.Child()
    tree_button = Gtk.Template.Child()
    table_button = Gtk.Template.Child()
    picker_button = Gtk.Template.Child()
    eraser_button = Gtk.Template.Child()
    fill_button = Gtk.Template.Child()

    primary_char_button = Gtk.Template.Child()
    secondary_char_button = Gtk.Template.Child()

    # Sidebar
    sidebar_stack = Gtk.Template.Child()
    sidebar_stack_switcher = Gtk.Template.Child()
    chars_carousel = Gtk.Template.Child()
    char_group_label = Gtk.Template.Child()
    char_carousel_go_back = Gtk.Template.Child()
    char_carousel_go_next = Gtk.Template.Child()
    lines_styles_box = Gtk.Template.Child()

    # Canvas side popover
    width_spin = Gtk.Template.Child()
    height_spin = Gtk.Template.Child()

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
        self.canvas.bind_property('primary_selected', self.primary_char_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)
        self.canvas.bind_property('primary_char', self.primary_char_button, 'label', GObject.BindingFlags.BIDIRECTIONAL)
        self.canvas.bind_property('secondary_char', self.secondary_char_button, 'label', GObject.BindingFlags.BIDIRECTIONAL)
        self.canvas.connect("undo-added", self.on_undo_added)
        self.canvas.connect("undo-removed", self.on_undo_removed)
        self.canvas.connect("redo-removed", self.on_redo_removed)
        self.toast_overlay.set_child(self.canvas)

        self.freehand_tool = Freehand(self.canvas)
        self.freehand_tool.bind_property('active', self.free_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)
        self.freehand_tool.add_sidebar_to(self.sidebar_stack)

        self.eraser_tool = Eraser(self.canvas)
        self.eraser_tool.bind_property('active', self.eraser_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)
        self.eraser_tool.add_sidebar_to(self.sidebar_stack)

        self.rectangle_tool = Rectangle(self.canvas)
        self.rectangle_tool.bind_property('active', self.rectangle_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)

        self.filled_rectangle_tool = FilledRectangle(self.canvas)
        self.filled_rectangle_tool.bind_property('active', self.filled_rectangle_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)

        self.line_tool = Line(self.canvas)
        self.line_tool.bind_property('active', self.line_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)
        self.line_tool.add_sidebar_to(self.sidebar_stack)

        self.move_tool = Select(self.canvas)
        self.move_tool.bind_property('active', self.move_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)
        self.move_tool.add_sidebar_to(self.sidebar_stack)

        self.text_tool = Text(self.canvas)
        self.text_tool.bind_property('active', self.text_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)
        self.text_tool.add_sidebar_to(self.sidebar_stack)

        self.table_tool = Table(self.canvas)
        self.table_tool.bind_property('active', self.table_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)
        self.table_tool.add_sidebar_to(self.sidebar_stack)

        self.picker_tool = Picker(self.canvas)
        self.picker_tool.bind_property('active', self.picker_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)

        self.tree_tool = Tree(self.canvas)
        self.tree_tool.bind_property('active', self.tree_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)
        self.tree_tool.add_sidebar_to(self.sidebar_stack)

        self.fill_tool = Fill(self.canvas)
        self.fill_tool.bind_property('active', self.fill_button, 'active', GObject.BindingFlags.BIDIRECTIONAL)

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
            style_btn = Gtk.ToggleButton(css_classes=["flat", "styles-preview"])
            style_btn.set_child(label)
            if prev_btn != None:
                style_btn.set_group(prev_btn)
            prev_btn = style_btn
            style_btn.connect("toggled", self.on_style_changed, self.lines_styles_box)
            self.lines_styles_box.append(style_btn)

        self.lines_styles_box.get_first_child().set_active(True)

        default_palettes_ranges = [
            {"name" : "ASCII", "ranges" : [(0x0020, 0x007F)]},
            {"name" : "Extended ASCII", "ranges" : [(0x00A1, 0x00AD), (0x00AE, 0x0180), (0x0100, 0x0180)]},
            {"name" : "Box Drawing", "ranges" : [(0x2500, 0x2580)]},
            {"name" : "Block Elements", "ranges" : [(0x2580, 0x25A0)]},
            {"name" : "Geometric Shapes", "ranges" : [(0x25A0, 0x25FC), (0x25FF, 0x2600)]},
            {"name" : "Arrows", "ranges" : [(0x2190, 0x21FF)]},
            # {"name" : "Braille Patterns", "ranges" : [(0x2800, 0x28FF)]},
            {"name" : "Mathematical", "ranges" : [(0x2200, 0x22C7), (0x22CB, 0x22EA)]},
            # {"name" : "Greek and Coptic", "ranges" : [(0x0370,0x03FF)]},
            # {"name" : "Cyrillic", "ranges" : [(0x0400,0x04FF)]},
            # {"name" : "Hebrew", "ranges" : [(0x0590,0x05FF)]},
            # {"name" : "Hiragana", "ranges" : [(0x3040,0x309F)]},
            # {"name" : "Katakana", "ranges" : [(0x30A0,0x30FF)]},
        ]

        for raw_palette in default_palettes_ranges:
            palette_chars = ""
            for code_range in raw_palette["ranges"]:
                for code_point in range(code_range[0], code_range[1]):
                    palette_chars += chr(code_point)

            new_palette = Palette(raw_palette["name"], palette_chars)
            self.add_palette_to_ui(new_palette)

        self.drawing_area_width = 0

        self.file_path = ""

        self.sidebar_stack.set_visible_child_name("character_page")

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

        self.update_canvas_size_spins()

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
            # new_button.set_tooltip_text(f"{char} : {unicodedata.name(char).title()}")
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

    @Gtk.Template.Callback("char_pages_go_back")
    def char_pages_go_back(self, btn):
        pos = self.chars_carousel.get_position()
        if pos == 0:
            return
        new_page = self.chars_carousel.get_nth_page(pos - 1)
        self.chars_carousel.scroll_to(new_page, False)
        self.char_group_label.set_label(new_page.get_name())
        self.char_carousel_go_next.set_sensitive(True)
        if pos - 1 == 0:
            btn.set_sensitive(False)

    @Gtk.Template.Callback("char_pages_go_next")
    def char_pages_go_next(self, btn):
        pos = self.chars_carousel.get_position()
        if pos == self.chars_carousel.get_n_pages() - 1:
            return
        new_page = self.chars_carousel.get_nth_page(pos + 1)
        self.chars_carousel.scroll_to(new_page, False)
        self.char_group_label.set_label(new_page.get_name())
        self.char_carousel_go_back.set_sensitive(True)
        if pos + 1 == self.chars_carousel.get_n_pages() - 1:
            btn.set_sensitive(False)

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

# ==========================
# Our Functions Start Here
# ==========================
    def brightness_to_ascii(self, brightness):
        """
        Convert a brightness value to an ASCII character.
        This method maps a given brightness value to a corresponding ASCII character
        from a predefined set of characters ranging from dark to light.
        Parameters:
        brightness (float): A float value representing the brightness, expected to be
                            in the range [0.0, 1.0], where 0.0 is the darkest 
                            and 1.0 is the brightest.
        Returns:
        str: A single ASCII character that corresponds to the given brightness level.
        """
        # Wide range of ASCII characters from dark to light
        ascii_chars = r"$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'."

        # Map brightness to the appropriate ASCII character
        index = int(brightness * (len(ascii_chars) - 1))  # Scale brightness to index range
        return ascii_chars[index]

    def downsample_pixbuf(self, pixels, width, height, channels, rowstride, block_size):
        """
        Downsamples an image represented by a pixel buffer.
        Args:
            pixels (list): A flat list of pixel values in RGB format.
            width (int): The width of the original image.
            height (int): The height of the original image.
            channels (int): The number of color channels (typically 3 for RGB).
            rowstride (int): The number of bytes per row in the pixel buffer.
            block_size (int): The size of the block to downsample by.
        Returns:
            tuple: A tuple containing:
                - downsampled_rgb (list): A list of downsampled RGB values.
                - downsampled_brightness (list): A list of brightness values 
                    for the downsampled image.
                - new_width (int): The width of the downsampled image.
                - new_height (int): The height of the downsampled image.
        """
        # Calculate the dimensions of the downsampled image
        new_width = width // block_size
        new_height = height // block_size
        downsampled_rgb = []
        downsampled_brightness = []

        for y in range(0, height, block_size):
            row_rgb = []
            row_brightness = []

            for x in range(0, width, block_size):
                # Accumulate RGB values within each block
                total_r, total_g, total_b = 0, 0, 0
                pixel_count = 0

                for by in range(block_size):
                    for bx in range(block_size):
                        px = x + bx
                        py = y + by
                        if px < width and py < height:
                            # Calculate the position of the pixel in the array
                            pixel_index = py * rowstride + px * channels
                            r = pixels[pixel_index]
                            g = pixels[pixel_index + 1]
                            b = pixels[pixel_index + 2]
                            total_r += r
                            total_g += g
                            total_b += b
                            pixel_count += 1

                # Compute the average color for the block
                avg_r = total_r // pixel_count
                avg_g = total_g // pixel_count
                avg_b = total_b // pixel_count

                # Convert RGB to brightness (use the max component for simplicity)
                brightness = max(avg_r, avg_g, avg_b) / 255.0
                row_rgb.append((avg_r, avg_g, avg_b))
                row_brightness.append(brightness)

            # Append the row to maintain the correct top-to-bottom layout
            downsampled_rgb.extend(row_rgb)
            downsampled_brightness.extend(row_brightness)

        return downsampled_rgb, downsampled_brightness, new_width, new_height

    def downsample_to_ascii(self, pixels, width, height, channels, rowstride, block_size):
        """
        Downsample an image and convert it to ASCII art.

        Args:
            pixels (list): The pixel data of the image.
            width (int): The width of the image.
            height (int): The height of the image.
            channels (int): The number of color channels in the image.
            rowstride (int): The number of bytes between the start of one row and the start of the next.
            block_size (int): The size of the block to downsample.

        Returns:
            str: The ASCII art representation of the image.
        """
        # Step 1: Downsample and get brightness values
        _, brightness_values, new_width, _ = self.downsample_pixbuf(
            pixels, width, height, channels, rowstride, block_size
        )

        # Step 2: Map brightness to ASCII characters
        ascii_art = ""
        for i, brightness in enumerate(brightness_values):
            if i > 0 and i % new_width == 0:
                ascii_art += "\n"  # Newline at the end of each row
            ascii_art += self.brightness_to_ascii(brightness)

        return ascii_art

    def pixbuf_downsampled_to_rgb_hsb(self, pixels, width, height, channels, rowstride, block_size):
        """
        Downsample an image and convert the downsampled pixels to RGB and HSB values.

        Args:
            pixels (list): The pixel data of the image.
            width (int): The width of the image.
            height (int): The height of the image.
            channels (int): The number of color channels in the image.
            rowstride (int): The number of bytes between the start 
            of one row and the start of the next.
            block_size (int): The size of the block to downsample.

        Returns:
            tuple: A tuple containing the RGB values, HSB values, new width, and new height.
        """
        downsampled_rgb, _, new_width, new_height = self.downsample_pixbuf(
            pixels, width, height, channels, rowstride, block_size
        )
        rgb_values = []
        hsb_values = []

        for r, g, b in downsampled_rgb:
            rgb_values.append((r, g, b))
            h, s, v = self.rgb_to_hsb(r, g, b)
            hsb_values.append((h, s, v))

        return rgb_values, hsb_values, new_width, new_height

    def pixbuf_to_rgb_hsb(self, pixels, width, height, channels, rowstride):
        """
        Convert the pixels of an image to RGB and HSB values.

        Args:
            pixels (list): The pixel data of the image.
            width (int): The width of the image.
            height (int): The height of the image.
            channels (int): The number of color channels in the image.
            rowstride (int): The number of bytes between the start of 
            one row and the start of the next.

        Returns:
            tuple: A tuple containing the RGB values and HSB values.
        """
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
        """
        Convert RGB color values to HSB (Hue, Saturation, Brightness).
        Parameters:
        r (int): Red component (0-255)
        g (int): Green component (0-255)
        b (int): Blue component (0-255)
        Returns:
        tuple: A tuple containing the HSB values:
            - h (float): Hue (0-360 degrees)
            - s (float): Saturation (0-1)
            - v (float): Brightness (0-1)
        """
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
        """
        Handles the import of an image into the application.
        This method first checks if there are unsaved changes on the canvas.
        If there are unsaved changes, it prompts the user to save them before
        proceeding with the import. If there are no unsaved changes, it directly
        calls the import_image_callback method to perform the import.
        Note:
            This method uses a callback function `import_image_callback` to
            complete the import process after handling unsaved changes.
                    
        Note: 
            We were able to reuse some existing functionality to create this function.
        """
        print("import_image called")

        # copy/pasted then modified code from open_file()
        if not self.canvas.is_saved:
            self.save_changes_message(self.import_image_callback)
        else:
            self.import_image_callback()

    # NOTE: Copied existing open_file_callback(self) function
    def import_image_callback(self):
        """
        Callback function to handle the import image action.

        This function opens a file dialog to allow the user to select an image file
        to import. Once the file is selected, it triggers the `on_import_image_response`
        method to handle the response. Additionally, it clears the current preview
        on the canvas.
        
        Note: 
            We were able to reuse some existing functionality to create this function.

        Args:
            None

        Returns:
            None
        """
        dialog = Gtk.FileDialog(
            title=_("Import Image"),
        )
        dialog.open(self, None, self.on_import_image_response)
        self.canvas.clear_preview()

    # NOTE: Copied existing on_open_file_response(self, dialog, response) function
    def on_import_image_response(self, dialog, response):
        """
        Handles the response from the import image dialog.
        This method is triggered when the user selects an image file to import. It performs the following steps:
        1. Opens the selected file.
        2. Loads the image from the file using GdkPixbuf.
        3. Downsamples the image to obtain RGB and brightness values.
        4. Converts the brightness values to ASCII characters and writes them to an output file.
        5. Loads and displays the ASCII art on the canvas.
        
        Note: 
            We were able to reuse some existing functionality to create this function.
        Args:
            dialog: The file dialog instance.
            response: The response from the dialog indicating the user's action.
        Raises:
            IOError: If there is an error reading the selected file or the output file.
        """
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

                # Set a block size for downsampling (e.g., 4 for a lower-resolution ASCII output)
                block_size = 1

                # Perform downsampling to get RGB and brightness values
                _, downsampled_brightness, new_width, new_height = self.downsample_pixbuf(
                    pixels, width, height, channels, rowstride, block_size
                )

                output_path = os.path.expanduser("~/Desktop/ascii-draw/output.txt")
                # Open the specified path for writing
                with open(output_path, 'w') as file_out:
                    for y in range(new_height):
                        for x in range(new_width):
                            # Calculate the index for the downsampled brightness values
                            index = y * new_width + x
                            brightness = downsampled_brightness[index]  # Accessing brightness value
                            ascii_char = self.brightness_to_ascii(brightness)  # Get ASCII character based on brightness
                            file_out.write(ascii_char)  # Write the ASCII character
                        file_out.write("\n")  # New line after each row

                print(f"ASCII art written to {output_path}")

                # Load and display the ASCII art on the canvas
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
# ========================
# Our Functions End Here
# ========================

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

    def change_char(self, btn, flow_box):
        if self.primary_char_button.get_active():
            self.primary_char_button.set_label(btn.get_label())
            self.canvas.primary_char = btn.get_label()
        else:
            self.secondary_char_button.set_label(btn.get_label())
            self.canvas.secondary_char = btn.get_label()

    def copy_to_clipboard(self):
        text = self.canvas.get_content()

        clipboard = Gdk.Display().get_default().get_clipboard()
        clipboard.set(text)

    @Gtk.Template.Callback("on_change_canvas_size_btn_clicked")
    def on_change_canvas_size_btn_clicked(self, btn):
        x = int(self.width_spin.get_value())
        y = int(self.height_spin.get_value())

        self.canvas.change_canvas_size(x, y)

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

    @Gtk.Template.Callback("on_increase_size_activated")
    def update_canvas_size_spins(self, *args):
        width, height = self.canvas.get_canvas_size()
        self.width_spin.set_value(width)
        self.height_spin.set_value(height)

    @Gtk.Template.Callback("on_choose_picker")
    def on_choose_picker(self, btn):
        print("picker")
        current_sidebar = self.sidebar_stack.get_visible_child_name()
        if current_sidebar != "character_page" and current_sidebar != "style_page":
            self.sidebar_stack.set_visible_child_name("character_page")
        self.canvas.clear_preview()

    @Gtk.Template.Callback("on_choose_rectangle")
    def on_choose_rectangle(self, btn):
        print("rect")
        current_sidebar = self.sidebar_stack.get_visible_child_name()
        if current_sidebar != "character_page" and current_sidebar != "style_page":
            self.sidebar_stack.set_visible_child_name("style_page")
        self.canvas.clear_preview()

    @Gtk.Template.Callback("on_choose_filled_rectangle")
    def on_choose_filled_rectangle(self, btn):
        print("f rect")
        current_sidebar = self.sidebar_stack.get_visible_child_name()
        if current_sidebar != "character_page" and current_sidebar != "style_page":
            self.sidebar_stack.set_visible_child_name("character_page")
        self.canvas.clear_preview()

    @Gtk.Template.Callback("on_choose_line")
    def on_choose_line(self, btn):
        print("line")
        current_sidebar = self.sidebar_stack.get_visible_child_name()
        if current_sidebar != "character_page" and current_sidebar != "style_page":
            self.sidebar_stack.set_visible_child_name("line_page")
        self.canvas.clear_preview()

    @Gtk.Template.Callback("on_choose_text")
    def on_choose_text(self, btn):
        print("text")
        current_sidebar = self.sidebar_stack.get_visible_child_name()
        if current_sidebar != "character_page" and current_sidebar != "style_page":
            self.sidebar_stack.set_visible_child_name("text_page")
        self.canvas.clear_preview()
        self.text_tool.preview_text()

    @Gtk.Template.Callback("on_choose_table")
    def on_choose_table(self, btn):
        print("table")
        current_sidebar = self.sidebar_stack.get_visible_child_name()
        if current_sidebar != "character_page" and current_sidebar != "style_page":
            self.sidebar_stack.set_visible_child_name("table_page")
        self.table_tool.preview()

    @Gtk.Template.Callback("on_choose_tree_list")
    def on_choose_tree_list(self, btn):
        print("tree")
        current_sidebar = self.sidebar_stack.get_visible_child_name()
        if current_sidebar != "character_page" and current_sidebar != "style_page":
            self.sidebar_stack.set_visible_child_name("tree_page")
        self.tree_tool.preview()

    @Gtk.Template.Callback("on_choose_select")
    def on_choose_select(self, btn):
        print("move")
        current_sidebar = self.sidebar_stack.get_visible_child_name()
        if current_sidebar != "character_page" and current_sidebar != "style_page":
            self.sidebar_stack.set_visible_child_name("move_page")
        self.canvas.clear_preview()

    @Gtk.Template.Callback("on_choose_free")
    def on_choose_free(self, btn):
        print("free")
        current_sidebar = self.sidebar_stack.get_visible_child_name()
        if current_sidebar != "character_page" and current_sidebar != "style_page":
            self.sidebar_stack.set_visible_child_name("freehand_page")
        self.canvas.clear_preview()

    @Gtk.Template.Callback("on_choose_eraser")
    def on_choose_eraser(self, btn):
        print("eraser")
        current_sidebar = self.sidebar_stack.get_visible_child_name()
        if current_sidebar != "character_page" and current_sidebar != "style_page":
            self.sidebar_stack.set_visible_child_name("eraser_page")
        self.canvas.clear_preview()

    @Gtk.Template.Callback("on_choose_fill")
    def on_choose_fill(self, btn):
        print("fill")
        current_sidebar = self.sidebar_stack.get_visible_child_name()
        if current_sidebar != "character_page" and current_sidebar != "style_page":
            self.sidebar_stack.set_visible_child_name("character_page")
        self.canvas.clear_preview()

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

    @Gtk.Template.Callback("close_sidebar")
    def close_sidebar(self, *args):
        self.overlay_split_view.set_show_sidebar(False)

    def select_rectangle_tool(self):
        self.rectangle_button.set_active(True)

    def select_filled_rectangle_tool(self):
        self.filled_rectangle_button.set_active(True)

    def select_line_tool(self):
        self.line_button.set_active(True)

    def select_text_tool(self):
        self.text_button.set_active(True)

    def select_table_tool(self):
        self.table_button.set_active(True)

    def select_tree_tool(self):
        self.tree_button.set_active(True)

    def select_free_tool(self):
        self.free_button.set_active(True)

    def select_eraser_tool(self):
        self.eraser_button.set_active(True)

    def select_arrow_tool(self):
        self.arrow_button.set_active(True)

    def select_free_line_tool(self):
        self.free_line_button.set_active(True)

    def select_picker_tool(self):
        self.picker_button.set_active(True)

    def select_move_tool(self):
        self.move_button.set_active(True)

    def select_fill_tool(self):
        self.fill_button.set_active(True)
