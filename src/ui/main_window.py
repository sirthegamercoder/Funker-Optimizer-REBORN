import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QCheckBox,
    QLabel, QFileDialog, QListWidget, QHBoxLayout, QFrame,
    QGraphicsDropShadowEffect, QSizePolicy, QScrollArea,
    QMessageBox
)
from PySide6.QtCore import Qt, QSize, QPoint
from PySide6.QtGui import (
    QFont, QPalette, QColor, QLinearGradient, QBrush,
    QScreen
)

from core.constants import (
    APP_NAME, COLOR_PRIMARY, COLOR_SECONDARY, COLOR_DARK,
    COLOR_TEXT, COLOR_WHITE, COLOR_YELLOW, DIVISION_NUMBER,
    DEFAULT_ANTIALIASING
)
from core.processor import ProcessingThread, HAS_LXML, HAS_PIL
from ui.widgets import ModernButton, IconLabel

try:
    import qtawesome as qta
    HAS_QTAWESOME = True
except ImportError:
    HAS_QTAWESOME = False


class FunkerOptimizerREBORN(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(800, 680)

        self.xml_file_paths = []
        self.png_file_paths = []
        self.division_number = DIVISION_NUMBER
        self.output_folder = ""
        self.processing_thread = None

        self.setup_theme()
        self.center_window()
        self.setup_ui()

    def center_window(self):
        screen = QScreen.availableGeometry(QApplication.primaryScreen())
        window_frame = self.frameGeometry()
        window_frame.moveCenter(screen.center())
        self.move(window_frame.topLeft())

    def setup_theme(self):
        self.setAutoFillBackground(True)
        palette = self.palette()

        gradient = QLinearGradient(0, 0, 0, 1)
        gradient.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
        gradient.setColorAt(0, QColor(8, 12, 35))
        gradient.setColorAt(0.3, QColor(13, 17, 45))
        gradient.setColorAt(0.7, QColor(13, 17, 45))
        gradient.setColorAt(1, QColor(8, 12, 35))

        palette.setBrush(QPalette.Window, QBrush(gradient))
        palette.setColor(QPalette.WindowText, QColor(176, 190, 197))
        palette.setColor(QPalette.Base, QColor(26, 35, 126))
        palette.setColor(QPalette.AlternateBase, QColor(26, 35, 126))
        palette.setColor(QPalette.Text, QColor(176, 190, 197))
        palette.setColor(QPalette.Button, QColor(26, 35, 126))
        palette.setColor(QPalette.ButtonText, QColor(176, 190, 197))
        palette.setColor(QPalette.BrightText, QColor(79, 195, 247))
        palette.setColor(QPalette.Highlight, QColor(79, 195, 247))
        palette.setColor(QPalette.HighlightedText, QColor(13, 17, 45))

        self.setPalette(palette)

    def setup_ui(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: rgba(13, 17, 45, 120);
                width: 16px;
                border-radius: 8px;
                margin: 4px 2px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1A237E,
                    stop:1 #283593);
                border-radius: 8px;
                min-height: 30px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #283593,
                    stop:1 #303F9F);
            }
            QScrollBar::add-line:vertical, 
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::add-page:vertical, 
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        central_widget = QWidget()
        scroll_area.setWidget(central_widget)
        self.setCentralWidget(scroll_area)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(40, 30, 40, 30)

        header_widget = self.create_header()
        main_layout.addWidget(header_widget)

        separator = self.create_separator()
        main_layout.addWidget(separator)

        file_section = self.create_file_section()
        main_layout.addWidget(file_section)

        output_section = self.create_output_section()
        main_layout.addWidget(output_section)

        list_container = self.create_file_lists()
        main_layout.addWidget(list_container)

        aa_container = self.create_aa_checkbox()
        main_layout.addWidget(aa_container)

        self.process_button = self.create_process_button()
        main_layout.addWidget(self.process_button)

        main_layout.addStretch(1)

        status_container = self.create_status_bar()
        main_layout.addWidget(status_container)

    def create_header(self):
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setAlignment(Qt.AlignCenter)
        header_layout.setSpacing(10)

        if HAS_QTAWESOME:
            title_icon = IconLabel("fa5s.heart", COLOR_WHITE, 28, self)
            header_layout.addWidget(title_icon)

        app_title = QLabel(APP_NAME)
        app_title.setAlignment(Qt.AlignCenter)
        title_font = QFont("Segoe UI", 24, QFont.Bold)
        app_title.setFont(title_font)
        app_title.setStyleSheet(f"""
            QLabel {{
                color: {COLOR_PRIMARY};
                background: transparent;
                padding: 5px 10px;
                letter-spacing: 1px;
            }}
        """)
        header_layout.addWidget(app_title)

        if HAS_QTAWESOME:
            title_icon2 = IconLabel("fa5s.star", COLOR_YELLOW, 28, self)
            header_layout.addWidget(title_icon2)

        return header_widget

    def create_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Plain)
        separator.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(79,195,247,0),
                    stop:0.2 rgba(79,195,247,180),
                    stop:0.5 rgba(79,195,247,255),
                    stop:0.8 rgba(79,195,247,180),
                    stop:1 rgba(79,195,247,0));
                max-height: 2px;
                border: none;
                margin: 5px 0;
            }
        """)
        return separator

    def create_file_section(self):
        file_section = QWidget()
        file_section.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(26, 35, 126, 40),
                    stop:1 rgba(26, 35, 126, 20));
                border-radius: 8px;
                border: 1px solid rgba(79, 195, 247, 20);
            }
        """)
        file_layout = QVBoxLayout(file_section)
        file_layout.setSpacing(12)
        file_layout.setContentsMargins(20, 15, 20, 15)

        section_label_container = self.create_section_label("File Selection", "fa5s.folder-open")
        file_layout.addWidget(section_label_container)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        self.xml_button = self.create_file_button(
            "  Load XML Files", "fa5s.file-code", self.load_xml_files
        )
        buttons_layout.addWidget(self.xml_button)

        self.png_button = self.create_file_button(
            "  Load Image Files", "fa5s.image", self.load_png_files
        )
        buttons_layout.addWidget(self.png_button)

        file_layout.addLayout(buttons_layout)
        return file_section

    def create_section_label(self, text, icon_name):
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: rgba(79, 195, 247, 8);
                border-radius: 8px;
                padding: 6px 12px;
            }
        """)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(10)

        if HAS_QTAWESOME:
            icon = IconLabel(icon_name, COLOR_PRIMARY, 16, self)
            layout.addWidget(icon)

        label = QLabel(text)
        label.setStyleSheet(f"""
            QLabel {{
                color: {COLOR_PRIMARY};
                font-size: 11px;
                font-weight: bold;
                background: transparent;
                padding: 0px;
            }}
        """)
        layout.addWidget(label)
        layout.addStretch()

        return container

    def create_file_button(self, text, icon_name, callback):
        icon = icon_name if HAS_QTAWESOME else None
        button = ModernButton(text, icon, COLOR_PRIMARY)
        button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1A237E,
                    stop:1 #283593);
                color: #E0E0E0;
                border: 1px solid #2C3E6B;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 600;
                padding: 10px 18px;
                text-align: left;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #283593,
                    stop:1 #303F9F);
                border-color: {COLOR_PRIMARY};
                color: {COLOR_PRIMARY};
            }}
            QPushButton:pressed {{
                background: #0D112D;
            }}
        """)
        button.clicked.connect(callback)
        return button

    def create_output_section(self):
        output_section = QWidget()
        output_section.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(26, 35, 126, 30),
                    stop:1 rgba(26, 35, 126, 15));
                border-radius: 8px;
                border: 1px solid rgba(79, 195, 247, 15);
            }
        """)
        output_layout = QHBoxLayout(output_section)
        output_layout.setContentsMargins(20, 12, 20, 12)
        output_layout.setSpacing(12)

        if HAS_QTAWESOME:
            output_icon = IconLabel("fa5s.folder", COLOR_PRIMARY, 18, self)
            output_layout.addWidget(output_icon)

        self.output_label = QLabel("Output folder: not set")
        self.output_label.setStyleSheet("color: #B0BEC5; font-size: 11px; padding: 0px;")
        self.output_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        output_layout.addWidget(self.output_label)

        self.output_button = self.create_output_button()
        output_layout.addWidget(self.output_button)

        return output_section

    def create_output_button(self):
        button = ModernButton("Select Output Folder", "fa5s.folder-open", COLOR_PRIMARY)
        button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1A237E,
                    stop:1 #283593);
                color: #E0E0E0;
                border: 1px solid #2C3E6B;
                border-radius: 10px;
                font-size: 12px;
                font-weight: 600;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #283593,
                    stop:1 #303F9F);
                border-color: {COLOR_PRIMARY};
                color: {COLOR_PRIMARY};
            }}
            QPushButton:pressed {{
                background: #0D112D;
            }}
        """)
        button.clicked.connect(self.select_output_folder)
        return button

    def create_file_lists(self):
        list_container = QWidget()
        list_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(26, 35, 126, 30),
                    stop:1 rgba(26, 35, 126, 15));
                border-radius: 15px;
                border: 1px solid rgba(79, 195, 247, 15);
            }
        """)
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(20, 15, 20, 15)
        list_layout.setSpacing(10)

        list_header = self.create_list_headers()
        list_layout.addLayout(list_header)

        file_list_layout = QHBoxLayout()
        file_list_layout.setSpacing(12)

        self.xml_list = self.create_list_widget()
        file_list_layout.addWidget(self.xml_list)

        self.png_list = self.create_list_widget()
        file_list_layout.addWidget(self.png_list)

        list_layout.addLayout(file_list_layout)
        return list_container

    def create_list_headers(self):
        list_header = QHBoxLayout()
        list_header.setSpacing(12)

        xml_header = self.create_list_header("XML Files", "fa5s.file-code")
        list_header.addWidget(xml_header)

        png_header = self.create_list_header("Image Files", "fa5s.image")
        list_header.addWidget(png_header)

        return list_header

    def create_list_header(self, text, icon_name):
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background-color: rgba(79, 195, 247, 8);
                border-radius: 8px;
                padding: 6px 10px;
            }
        """)
        header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(10)

        if HAS_QTAWESOME:
            icon = IconLabel(icon_name, COLOR_PRIMARY, 16, self)
            layout.addWidget(icon)

        label = QLabel(text)
        label.setStyleSheet(f"""
            QLabel {{
                color: {COLOR_PRIMARY};
                font-size: 11px;
                font-weight: bold;
                background: transparent;
                padding: 0px;
            }}
        """)
        layout.addWidget(label)
        layout.addStretch()

        return header

    def create_list_widget(self):
        list_widget = QListWidget()
        list_widget.setMinimumHeight(120)
        list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        list_widget.setStyleSheet("""
            QListWidget {
                background-color: rgba(13, 17, 45, 60);
                color: #B0BEC5;
                border: 1px solid #2C3E6B;
                border-radius: 8px;
                font-size: 11px;
                padding: 8px;
                font-family: 'Segoe UI';
            }
            QListWidget::item {
                padding: 6px 10px;
                border-radius: 4px;
                margin: 2px 0;
            }
            QListWidget::item:hover {
                background-color: rgba(79, 195, 247, 15);
                color: #4FC3F7;
            }
            QListWidget::item:selected {
                background-color: rgba(79, 195, 247, 25);
                color: #4FC3F7;
            }
            QListWidget::item:selected:active {
                background-color: rgba(79, 195, 247, 30);
            }
        """)
        return list_widget

    def create_aa_checkbox(self):
        aa_container = QWidget()
        aa_container.setStyleSheet("""
            QWidget {
                background-color: rgba(26, 35, 126, 20);
                border-radius: 10px;
                padding: 8px 15px;
            }
        """)
        aa_layout = QHBoxLayout(aa_container)
        aa_layout.setContentsMargins(12, 8, 12, 8)
        aa_layout.setSpacing(10)

        if HAS_QTAWESOME:
            aa_icon = IconLabel("fa5s.magic", COLOR_PRIMARY, 18, self)
            aa_layout.addWidget(aa_icon)

        self.aa_checkbox = QCheckBox("  Anti-aliasing")
        self.aa_checkbox.setStyleSheet("""
            QCheckBox {
                color: #B0BEC5;
                font-size: 14px;
                font-weight: 500;
                padding: 0px;
            }
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
                border-radius: 6px;
            }
            QCheckBox::indicator:unchecked {
                background-color: rgba(26, 35, 126, 50);
                border: 2px solid #2C3E6B;
            }
            QCheckBox::indicator:checked {
                background-color: #4FC3F7;
                border: 2px solid #4FC3F7;
            }
            QCheckBox::indicator:hover {
                border-color: #4FC3F7;
            }
        """)
        self.aa_checkbox.setChecked(DEFAULT_ANTIALIASING)
        aa_layout.addWidget(self.aa_checkbox)
        aa_layout.addStretch()

        return aa_container

    def create_process_button(self):
        icon = "fa5s.play" if HAS_QTAWESOME else None
        button = ModernButton("  Modify and Resize", icon, COLOR_WHITE)
        button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0D47A1,
                    stop:0.3 #1565C0,
                    stop:0.7 #1565C0,
                    stop:1 #0D47A1);
                color: {COLOR_PRIMARY};
                border: 2px solid {COLOR_PRIMARY};
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                padding: 14px 20px;
                letter-spacing: 1.5px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1565C0,
                    stop:0.3 #1976D2,
                    stop:0.7 #1976D2,
                    stop:1 #1565C0);
                color: #FFFFFF;
                border-color: #64D8FF;
            }}
            QPushButton:pressed {{
                background: #0D112D;
                border-color: {COLOR_PRIMARY};
            }}
            QPushButton:disabled {{
                background: rgba(13, 17, 45, 80);
                color: #455A64;
                border-color: #455A64;
            }}
        """)
        button.clicked.connect(self.process_files)
        return button

    def create_status_bar(self):
        status_container = QWidget()
        status_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(26, 35, 126, 30),
                    stop:1 rgba(26, 35, 126, 10));
                border-radius: 10px;
                border: 1px solid rgba(79, 195, 247, 15);
                padding: 8px 15px;
            }
        """)
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(12, 8, 12, 8)
        status_layout.setSpacing(10)

        if HAS_QTAWESOME:
            status_icon = IconLabel("fa5s.circle", COLOR_PRIMARY, 12, self)
            status_layout.addWidget(status_icon)

        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #B0BEC5;
                font-size: 12px;
                font-weight: 500;
                padding: 0px;
            }
        """)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        return status_container

    def load_xml_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select XML Files", "", "XML Files (*.xml)"
        )
        if files:
            self.xml_file_paths = files
            self.xml_list.clear()
            for file in files:
                self.xml_list.addItem(os.path.basename(file))
            self.status_label.setText(f"Loaded {len(files)} XML file(s)")
            self.update_batch_status()

    def load_png_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select PNG Image Files", "", "PNG Images (*.png)"
        )
        if files:
            self.png_file_paths = files
            self.png_list.clear()
            for file in files:
                self.png_list.addItem(os.path.basename(file))
            self.status_label.setText(f"Loaded {len(files)} PNG file(s)")
            self.update_batch_status()

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder
            self.output_label.setText(f"Output folder: {folder}")
            self.status_label.setText("Output folder set")

    def update_batch_status(self):
        xml_count = len(self.xml_file_paths)
        png_count = len(self.png_file_paths)

        if xml_count > 1 or png_count > 1:
            self.status_label.setText(
                f"Batch mode: {xml_count} XML, {png_count} PNG files loaded"
            )
        elif xml_count == 1 and png_count == 1:
            self.status_label.setText("Single mode: 1 XML, 1 PNG file loaded")
        elif xml_count > 0 or png_count > 0:
            self.status_label.setText("Waiting for matching files...")

    def process_files(self):
        xml_count = len(self.xml_file_paths)
        png_count = len(self.png_file_paths)

        if xml_count == 0 and png_count == 0:
            QMessageBox.warning(
                self, "No Files", "Please load XML and/or PNG files first!"
            )
            self.status_label.setText("Please load XML and/or PNG files first!")
            return

        if not self.output_folder:
            QMessageBox.warning(
                self, "No Output Folder", "Please select an output folder first!"
            )
            self.status_label.setText("Please select an output folder first!")
            return

        if xml_count > 0 and not HAS_LXML:
            QMessageBox.critical(
                self,
                "Missing Dependency",
                "lxml is required for XML processing.\nInstall with: pip install lxml",
            )
            return

        if png_count > 0 and not HAS_PIL:
            QMessageBox.critical(
                self,
                "Missing Dependency",
                "Pillow is required for image processing.\nInstall with: pip install Pillow",
            )
            return

        mode = "BATCH" if (xml_count > 1 or png_count > 1) else "SINGLE"
        aa_status = "ON" if self.aa_checkbox.isChecked() else "OFF"

        self.status_label.setText(
            f"Processing {mode} mode with Anti-aliasing {aa_status}..."
        )

        self.process_button.setEnabled(False)
        self.process_button.setText("Processing...")

        self.processing_thread = ProcessingThread(
            self.xml_file_paths,
            self.png_file_paths,
            self.output_folder,
            self.division_number,
            self.aa_checkbox.isChecked(),
        )
        self.processing_thread.progress.connect(self.update_status)
        self.processing_thread.finished.connect(self.finish_processing)
        self.processing_thread.start()

    def update_status(self, message):
        self.status_label.setText(message)

    def finish_processing(self, success, message):
        self.process_button.setEnabled(True)
        self.process_button.setText("  Modify and Resize")
        if HAS_QTAWESOME:
            self.process_button.setIcon(qta.icon("fa5s.play", color="#FFFFFF"))

        if success:
            QMessageBox.information(self, "Processing Complete", message)
            self.status_label.setText(message)
        else:
            QMessageBox.critical(self, "Processing Error", message)
            self.status_label.setText(f"Error: {message}")