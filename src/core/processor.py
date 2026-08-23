from pathlib import Path
import zipfile
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
        self.is_batch = len(xml_files) > 1 or len(png_files) > 1
        self.zip_file = None
        self.zip_path = None

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
                    "x",
                    "y",
                    "width",
                    "height",
                    "frameX",
                    "frameY",
                    "frameWidth",
                    "frameHeight",
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

            resample_filter = (
                Image.Resampling.LANCZOS
                if self.use_aliasing
                else Image.Resampling.NEAREST
            )
            resized_img = img.resize(new_size, resample_filter)
            resized_img.save(output_path)
            return True
        except Exception as e:
            self.progress.emit(f"Error processing image {input_path}: {e}")
            return False

    def initialize_zip(self):
        if self.is_batch:
            output_folder = Path(self.output_folder)
            self.zip_path = output_folder / "optimized_characters.zip"
            if self.zip_path.exists():
                self.zip_path.unlink()
            self.zip_file = zipfile.ZipFile(self.zip_path, "a", zipfile.ZIP_DEFLATED)
            self.progress.emit("Batch mode: ZIP archive initialized")

    def add_file_to_zip(self, file_path, arcname):
        if self.zip_file and file_path.exists():
            self.zip_file.write(file_path, arcname)
            return True
        return False

    def close_zip(self):
        if self.zip_file:
            self.zip_file.close()
            self.zip_file = None

    def cleanup_files(self, output_folder):
        if self.is_batch:
            for file_path in output_folder.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in [".xml", ".png"]:
                    try:
                        file_path.unlink()
                    except Exception:
                        pass

    def run(self):
        try:
            output_folder = Path(self.output_folder)
            output_folder.mkdir(parents=True, exist_ok=True)

            self.initialize_zip()

            processed_files = []
            xml_processed = 0

            if self.xml_files and HAS_LXML:
                self.progress.emit(f"Processing {len(self.xml_files)} XML file(s)...")
                for xml_file in self.xml_files:
                    base_name = Path(xml_file).name
                    output_path = output_folder / base_name

                    tree = self.process_xml(xml_file)
                    if tree is not None:
                        tree.write(output_path, encoding="utf-8", xml_declaration=True)
                        xml_processed += 1
                        processed_files.append(output_path)
                        self.progress.emit(f"Processed XML: {base_name}")

                        if self.is_batch:
                            self.add_file_to_zip(output_path, base_name)

            png_processed = 0
            if self.png_files and HAS_PIL:
                self.progress.emit(f"Processing {len(self.png_files)} image file(s)...")
                for png_file in self.png_files:
                    base_name = Path(png_file).name
                    output_path = output_folder / base_name

                    if self.process_image(png_file, output_path, 50):
                        png_processed += 1
                        processed_files.append(output_path)
                        self.progress.emit(f"Processed image: {base_name}")

                        if self.is_batch:
                            self.add_file_to_zip(output_path, base_name)

            self.close_zip()

            if self.is_batch and self.zip_path and self.zip_path.exists():
                self.cleanup_files(output_folder)
                zip_size = self.zip_path.stat().st_size / (1024 * 1024)
                self.progress.emit(
                    f"Batch mode: All files compressed into {self.zip_path.name} ({zip_size:.2f} MB)"
                )
                success_message = f"Completed! Processed {xml_processed} XML file(s) and {png_processed} image(s)\nAll files compressed into: {self.zip_path.name}"
            else:
                success_message = f"Completed! Processed {xml_processed} XML file(s) and {png_processed} image(s)"

            self.finished.emit(True, success_message)

        except Exception as e:
            self.close_zip()
            self.finished.emit(False, f"Error during processing: {str(e)}")
