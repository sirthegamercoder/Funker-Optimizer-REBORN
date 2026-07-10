import os
from PySide6.QtCore import QThread, Signal

try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class ProcessingThread(QThread):
    progress = Signal(str)
    finished = Signal(bool, str)

    def __init__(
        self, xml_files, png_files, output_folder, division_number=2, use_aliasing=True
    ):
        super().__init__()
        self.xml_files = xml_files
        self.png_files = png_files
        self.output_folder = output_folder
        self.division_number = division_number
        self.use_aliasing = use_aliasing

    def smart_divide(self, value, attr):
        try:
            result = int(value) / self.division_number

            if attr in ["x", "y", "frameX", "frameY"]:
                result = round(result * 2) / 2
                return str(int(result)) if result.is_integer() else str(result)
            else:
                result = round(result)
                result = max(1, result)
                return str(int(result))
        except Exception:
            return str(int(value) // self.division_number)

    def process_xml(self, input_path):
        try:
            tree = etree.parse(input_path)
            root = tree.getroot()
            subtextures = tree.xpath("//SubTexture")

            for subtexture in subtextures:
                for attr in [
                    "x", "y", "width", "height",
                    "frameX", "frameY", "frameWidth", "frameHeight"
                ]:
                    value = subtexture.get(attr)
                    if value is not None:
                        new_value = self.smart_divide(value, attr)
                        subtexture.set(attr, new_value)

            return tree
        except Exception as e:
            self.progress.emit(f"Error processing XML {input_path}: {e}")
            return None

    def process_image(self, input_path, output_path, percentage=50):
        try:
            img = Image.open(input_path)
            original_width, original_height = img.size
            new_width = int(original_width * (percentage / 100))
            new_height = int(original_height * (percentage / 100))
            new_size = (new_width, new_height)

            resample_filter = Image.Resampling.LANCZOS if self.use_aliasing else Image.Resampling.NEAREST
            resized_img = img.resize(new_size, resample_filter)
            resized_img.save(output_path)
            return True
        except Exception as e:
            self.progress.emit(f"Error processing image {input_path}: {e}")
            return False

    def run(self):
        try:
            xml_processed = 0
            if self.xml_files and HAS_LXML:
                self.progress.emit(f"Processing {len(self.xml_files)} XML file(s)...")
                for xml_file in self.xml_files:
                    base_name = os.path.basename(xml_file)
                    output_path = os.path.join(self.output_folder, base_name)

                    tree = self.process_xml(xml_file)
                    if tree is not None:
                        tree.write(output_path, encoding="utf-8", xml_declaration=True)
                        xml_processed += 1
                        self.progress.emit(f"Processed XML: {base_name}")

            png_processed = 0
            if self.png_files and HAS_PIL:
                self.progress.emit(f"Processing {len(self.png_files)} image file(s)...")
                for png_file in self.png_files:
                    base_name = os.path.basename(png_file)
                    output_path = os.path.join(self.output_folder, base_name)

                    if self.process_image(png_file, output_path, 50):
                        png_processed += 1
                        self.progress.emit(f"Processed image: {base_name}")

            success_message = f"Completed! Processed {xml_processed} XML file(s) and {png_processed} image(s)"
            self.finished.emit(True, success_message)

        except Exception as e:
            self.finished.emit(False, f"Error during processing: {str(e)}")