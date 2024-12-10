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