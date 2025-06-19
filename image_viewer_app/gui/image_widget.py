from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QPushButton, QScrollArea, QHBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QPainter, QPaintEvent
from PyQt5.QtCore import Qt, QSize

class ImageWidget(QWidget):
    """
    A custom widget to display QPixmaps.
    Supports "Side-by-Side" and "Overlay" display modes.
    Its size is determined by the content and display mode.
    """
    def __init__(self, parent=None):
        """
        Initializes the ImageWidget.
        """
        super().__init__(parent)
        self.pixmaps: list[QPixmap] = []
        self.spacing = 10  # Space between images in side-by-side mode
        self.display_mode = "Side-by-Side"  # Default display mode
        self.current_overlay_index = 0
        self.setStyleSheet("background-color: #282828;")

    def set_display_mode(self, mode: str):
        """
        Sets the display mode for the widget.

        Args:
            mode (str): The display mode ("Side-by-Side" or "Overlay").
        """
        if mode in ["Side-by-Side", "Overlay"]:
            if self.display_mode != mode:
                self.display_mode = mode
                self.current_overlay_index = 0  # Reset index when mode changes
                self.update_layout_and_repaint()
        else:
            print(f"Warning: Unknown display mode '{mode}' requested.")

    def set_pixmaps(self, pixmaps: list[QPixmap] | None):
        """
        Sets the list of pixmaps to be displayed.

        Args:
            pixmaps (list[QPixmap] | None): The list of pixmaps. Clears if None.
        """
        if pixmaps is None:
            self.pixmaps = []
        else:
            self.pixmaps = [pm for pm in pixmaps if pm and not pm.isNull()]

        self.current_overlay_index = 0 # Reset index when new pixmaps are set
        self.update_layout_and_repaint()

    def clear_images(self):
        """Clears all displayed images."""
        self.pixmaps = []
        self.current_overlay_index = 0
        self.update_layout_and_repaint()

    def update_layout_and_repaint(self):
        """
        Calculates required size based on content and display mode,
        sets the widget's fixed size, and triggers a repaint.
        """
        new_width = 100  # Default minimum width
        new_height = 100 # Default minimum height

        if self.display_mode == "Overlay":
            if self.pixmaps and 0 <= self.current_overlay_index < len(self.pixmaps):
                current_pixmap = self.pixmaps[self.current_overlay_index]
                new_width = current_pixmap.width()
                new_height = current_pixmap.height()
            # else: keep default small size if no image or invalid index

        elif self.display_mode == "Side-by-Side":
            if self.pixmaps:
                total_width_sbs = 0
                max_height_sbs = 0
                for i, pixmap in enumerate(self.pixmaps):
                    total_width_sbs += pixmap.width()
                    if i < len(self.pixmaps) - 1:
                        total_width_sbs += self.spacing
                    if pixmap.height() > max_height_sbs:
                        max_height_sbs = pixmap.height()
                new_width = total_width_sbs
                new_height = max_height_sbs
            # else: keep default small size if no images for side-by-side

        self.setFixedSize(max(100, new_width), max(100, new_height))
        self.update()

    def paintEvent(self, event: QPaintEvent):
        """
        Handles the paint event to draw the pixmaps based on the display mode.
        """
        super().paintEvent(event)
        painter = QPainter(self)

        if not self.pixmaps:
            painter.end()
            return

        if self.display_mode == "Overlay":
            if 0 <= self.current_overlay_index < len(self.pixmaps):
                pixmap_to_draw = self.pixmaps[self.current_overlay_index]
                # Scale to fit widget, keep aspect ratio, center
                scaled_pixmap = pixmap_to_draw.scaled(
                    self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                x = (self.width() - scaled_pixmap.width()) / 2
                y = (self.height() - scaled_pixmap.height()) / 2
                painter.drawPixmap(int(x), int(y), scaled_pixmap)

        elif self.display_mode == "Side-by-Side":
            current_x = 0
            for pixmap in self.pixmaps:
                if not pixmap.isNull():
                    painter.drawPixmap(current_x, 0, pixmap)
                    current_x += pixmap.width() + self.spacing

        painter.end()

    def next_image_overlay(self):
        """Advances to the next image in Overlay mode."""
        if self.display_mode == "Overlay" and self.pixmaps:
            self.current_overlay_index = (self.current_overlay_index + 1) % len(self.pixmaps)
            self.update_layout_and_repaint()
            print(f"Overlay index: {self.current_overlay_index}")


    def prev_image_overlay(self):
        """Goes to the previous image in Overlay mode."""
        if self.display_mode == "Overlay" and self.pixmaps:
            self.current_overlay_index = (self.current_overlay_index - 1 + len(self.pixmaps)) % len(self.pixmaps)
            self.update_layout_and_repaint()
            print(f"Overlay index: {self.current_overlay_index}")


if __name__ == '__main__':
    import sys
    # Ensure os is imported if you use os.path for image loading in tests
    # import os

    app = QApplication(sys.argv)

    # Create some dummy pixmaps for testing
    pm1 = QPixmap(QSize(300, 200))
    pm1.fill(Qt.red)
    painter1 = QPainter(pm1)
    painter1.drawText(pm1.rect(), Qt.AlignCenter, "Image 1\n300x200")
    painter1.end()

    pm2 = QPixmap(QSize(200, 250))
    pm2.fill(Qt.blue)
    painter2 = QPainter(pm2)
    painter2.drawText(pm2.rect(), Qt.AlignCenter, "Image 2\n200x250")
    painter2.end()

    pm3 = QPixmap(QSize(350, 150))
    pm3.fill(Qt.green)
    painter3 = QPainter(pm3)
    painter3.drawText(pm3.rect(), Qt.AlignCenter, "Image 3\n350x150")
    painter3.end()

    image_widget = ImageWidget()

    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setWidget(image_widget)
    scroll_area.setStyleSheet("background-color: #404040;")

    # --- Test Controls ---
    status_label = QLabel("Mode: Side-by-Side | Index: 0")
    def update_status():
        status_label.setText(f"Mode: {image_widget.display_mode} | Index: {image_widget.current_overlay_index} | Pixmaps: {len(image_widget.pixmaps)}")

    btn_sbs_mode = QPushButton("Side-by-Side Mode")
    btn_sbs_mode.clicked.connect(lambda: (image_widget.set_display_mode("Side-by-Side"), update_status()))

    btn_overlay_mode = QPushButton("Overlay Mode")
    btn_overlay_mode.clicked.connect(lambda: (image_widget.set_display_mode("Overlay"), update_status()))

    btn_next = QPushButton("Next (Overlay)")
    btn_next.clicked.connect(lambda: (image_widget.next_image_overlay(), update_status()))

    btn_prev = QPushButton("Prev (Overlay)")
    btn_prev.clicked.connect(lambda: (image_widget.prev_image_overlay(), update_status()))

    btn_set_images = QPushButton("Set [Img1, Img2, Img3]")
    btn_set_images.clicked.connect(lambda: (image_widget.set_pixmaps([pm1, pm2, pm3]), update_status()))

    btn_clear = QPushButton("Clear Images")
    btn_clear.clicked.connect(lambda: (image_widget.clear_images(), update_status()))

    controls_layout = QHBoxLayout()
    controls_layout.addWidget(btn_sbs_mode)
    controls_layout.addWidget(btn_overlay_mode)
    controls_layout.addWidget(btn_prev)
    controls_layout.addWidget(btn_next)
    controls_layout.addWidget(btn_set_images)
    controls_layout.addWidget(btn_clear)

    main_test_widget = QWidget()
    layout = QVBoxLayout(main_test_widget)
    layout.addWidget(status_label)
    layout.addWidget(scroll_area)
    layout.addLayout(controls_layout)

    main_test_widget.resize(800, 600)
    main_test_widget.setWindowTitle("ImageWidget Enhanced Test")
    main_test_widget.show()

    image_widget.set_pixmaps([pm1, pm2, pm3]) # Initial images
    update_status()

    sys.exit(app.exec_())
