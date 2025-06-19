from PyQt5.QtWidgets import (QMainWindow, QWidget, QApplication, QAction,
                             QFileDialog, QListWidget, QDockWidget, QListWidgetItem,
                             QRadioButton, QButtonGroup, QHBoxLayout, QLabel, QToolBar,
                             QScrollArea)
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QKeyEvent # For keyboard navigation
from .image_widget import ImageWidget
from image_viewer_app.core.watcher import FolderWatcher
from image_viewer_app.core.series_identifier import SeriesIdentifier
from image_viewer_app.core.image_loader import load_qpixmap

class MainWindow(QMainWindow):
    """
    Main application window for the Image Series Viewer.
    """
    def __init__(self, parent=None):
        """
        Initializes the MainWindow.
        """
        super().__init__(parent)

        self.setWindowTitle("Image Series Viewer")
        self.setGeometry(100, 100, 1024, 768)

        # Image display widget (the one that draws images)
        self.image_display_widget = ImageWidget() # No parent if it's scroll area content

        # ScrollArea to contain the ImageWidget
        self.image_scroll_area = QScrollArea()
        self.image_scroll_area.setWidgetResizable(True) # Crucial!
        self.image_scroll_area.setWidget(self.image_display_widget)
        # Optional: set scroll bar policies if needed, AsNeeded is default
        # self.image_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # self.image_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.setCentralWidget(self.image_scroll_area) # ScrollArea is now the central widget

        # Instance variable to store the currently selected folder
        self.current_folder = None

        # Setup series list widget (docked)
        self._create_series_list_dock()

        # Setup display controls toolbar
        self._create_display_controls_toolbar()

        # Setup menu bar
        self._create_menu_bar()

        # Setup status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

        # Initialize FolderWatcher
        self.folder_watcher = FolderWatcher(self)
        self.folder_watcher.new_images_detected.connect(self._handle_new_images)

        # Initialize SeriesIdentifier
        self.series_identifier = SeriesIdentifier()

        # Initialize storage for pixmaps and series data
        self.loaded_pixmaps = {} # Maps image_path: QPixmap
        self.identified_series = {} # Maps series_key: list_of_image_paths

        # Further UI components will be added here later
        # Example: self.image_display_widget.set_pixmap(QPixmap("path/to/default/image.png"))

    def _create_display_controls_toolbar(self):
        """
        Creates the toolbar for display mode controls (radio buttons).
        """
        display_toolbar = QToolBar("Display Modes")
        display_toolbar.setMovable(False) # Keep it fixed

        # Widget to hold the controls for layout purposes
        control_widget = QWidget()
        layout = QHBoxLayout(control_widget)
        layout.setContentsMargins(5, 0, 5, 0) # Add some spacing

        layout.addWidget(QLabel("Display Mode:"))

        self.side_by_side_radio = QRadioButton("Side-by-Side")
        self.side_by_side_radio.setChecked(True)
        self.current_display_mode = "Side-by-Side"
        self.image_display_widget.set_display_mode(self.current_display_mode) # Initialize ImageWidget's mode

        self.overlay_radio = QRadioButton("Overlay")

        self.display_mode_group = QButtonGroup(self)
        self.display_mode_group.addButton(self.side_by_side_radio)
        self.display_mode_group.addButton(self.overlay_radio)

        # Connect to a single slot using QButtonGroup's signal
        # The lambda passes the button object that was toggled
        self.display_mode_group.buttonToggled.connect(self._on_display_mode_changed)

        layout.addWidget(self.side_by_side_radio)
        layout.addWidget(self.overlay_radio)
        layout.addStretch() # Add stretch to push controls to the left if toolbar is wider

        control_widget.setLayout(layout) # Set the layout on the widget
        display_toolbar.addWidget(control_widget)

        self.addToolBar(Qt.TopToolBarArea, display_toolbar)

    def _on_display_mode_changed(self, button: QRadioButton, checked: bool):
        """
        Handles changes in the display mode selection.
        Called when a radio button in the display_mode_group is toggled.
        """
        if checked: # Only act on the button that became checked
            if button == self.side_by_side_radio:
                self.current_display_mode = "Side-by-Side"
            elif button == self.overlay_radio:
                self.current_display_mode = "Overlay"

            print(f"Display mode changed to: {self.current_display_mode}")
            self.image_display_widget.set_display_mode(self.current_display_mode) # Set mode on ImageWidget first
            self._trigger_series_display_update() # Then update display

    def _create_series_list_dock(self):
        """
        Creates the dock widget containing the list of image series.
        """
        self.series_list_widget = QListWidget()
        self.series_list_widget.setMaximumWidth(250) # Example constraint

        # For testing purposes, add some dummy items
        self.series_list_widget.addItems(["Series A / Scan 001", "Series A / Scan 002", "Photo Set B", "Single Item XYZ"])

        series_dock_widget = QDockWidget("Image Series", self)
        series_dock_widget.setWidget(self.series_list_widget)
        series_dock_widget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.addDockWidget(Qt.LeftDockWidgetArea, series_dock_widget)

        # Connect series list selection changes
        self.series_list_widget.currentItemChanged.connect(self._on_series_selection_changed)

    def _create_menu_bar(self):
        """
        Creates the main menu bar and its actions.
        """
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("&File")

        # "Open Folder..." action
        open_folder_action = QAction("&Open Folder...", self)
        open_folder_action.setStatusTip("Select a folder to watch for images")
        open_folder_action.triggered.connect(self._open_folder_dialog)
        file_menu.addAction(open_folder_action)

    def _open_folder_dialog(self):
        """
        Opens a dialog for the user to select a folder.
        If a folder is selected, its path is stored and printed.
        """
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            self.current_folder if self.current_folder else ""  # Start from current/last folder or default
        )

        if folder_path:
            self.current_folder = folder_path
            print(f"Selected folder: {self.current_folder}")
            # Clear previous state when opening a new folder
            self.loaded_pixmaps.clear()
            self.identified_series.clear()
            self.series_list_widget.clear()
            self.image_display_widget.clear_images() # Use the new method name

            self.folder_watcher.set_folder(self.current_folder)
            self.status_bar.showMessage(f"Watching folder: {self.current_folder}")

    def _handle_new_images(self, new_image_paths: list[str]):
        """
        Handles the new_images_detected signal from the FolderWatcher.
        Loads images, identifies series, and updates the UI.
        """
        if not new_image_paths:
            self.status_bar.showMessage("No new image paths received.", 3000)
            return

        print(f"MainWindow._handle_new_images received: {new_image_paths}")

        newly_loaded_pixmap_count = 0
        actually_new_paths_for_series_id = []

        for path in new_image_paths:
            if path not in self.loaded_pixmaps:
                pixmap = load_qpixmap(path)
                if pixmap:
                    self.loaded_pixmaps[path] = pixmap
                    newly_loaded_pixmap_count += 1
                    actually_new_paths_for_series_id.append(path)
                    print(f"Successfully loaded: {path}")
                else:
                    self.status_bar.showMessage(f"Failed to load image: {path}", 5000)

        if not actually_new_paths_for_series_id and self.identified_series:
            # This can happen if FolderWatcher sends existing files again
            # and no *new* files were actually loaded in this batch.
            # We don't need to re-identify series if no new valid images were added.
            print("No new valid pixmaps loaded in this batch, series identification skipped.")
            self.status_bar.showMessage(f"Processed {len(new_image_paths)} paths. No new images loaded.", 5000)
            return

        # Update list of all known image paths for series identification
        all_known_image_paths = sorted(list(self.loaded_pixmaps.keys()))
        self.identified_series = self.series_identifier.identify_series(all_known_image_paths)
        print(f"Series identified: {self.identified_series}")
        self._update_series_list_widget()

        self.status_bar.showMessage(
            f"Processed {len(new_image_paths)} paths. {newly_loaded_pixmap_count} new images loaded. Total series: {len(self.identified_series)}.",
            10000
        )

    def _update_series_list_widget(self):
        """
        Updates the series list widget based on self.identified_series.
        Attempts to preserve selection if the selected series (by its image paths) still exists.
        """
        current_selection_data = None
        current_item = self.series_list_widget.currentItem()
        if current_item:
            current_selection_data = current_item.data(Qt.UserRole) # This is list of paths

        self.series_list_widget.blockSignals(True)
        self.series_list_widget.clear()

        if not self.identified_series:
            self.image_display_widget.clear_images() # Use new method name
            self.series_list_widget.blockSignals(False)
            print("No series identified, list cleared.")
            return

        new_item_to_select = None
        for series_key, image_paths_in_series in sorted(self.identified_series.items()):
            if not image_paths_in_series:
                continue

            display_text = f"{series_key} ({len(image_paths_in_series)} image{'s' if len(image_paths_in_series) > 1 else ''})"

            item = QListWidgetItem()
            item.setText(display_text)
            item.setData(Qt.UserRole, image_paths_in_series)
            self.series_list_widget.addItem(item)

            if current_selection_data and image_paths_in_series == current_selection_data:
                new_item_to_select = item

        self.series_list_widget.blockSignals(False)

        if new_item_to_select:
            self.series_list_widget.setCurrentItem(new_item_to_select) # This will trigger _on_series_selection_changed
        elif self.series_list_widget.count() > 0:
            self.series_list_widget.setCurrentRow(0) # Triggers _on_series_selection_changed

        # If list is empty after update (e.g. all images became invalid or were removed)
        if self.series_list_widget.count() == 0:
             self.image_display_widget.clear_images() # Use new method name
             self.status_bar.showMessage("No image series found.", 3000)


    def _on_series_selection_changed(self, current_item, previous_item):
        """
        Handles selection changes in the series list widget.
        Displays the first image of the selected series.
        """
        _ = previous_item # Mark as unused

        if current_item:
            image_paths_in_series = current_item.data(Qt.UserRole)

            if not isinstance(image_paths_in_series, list) or \
               not all(isinstance(p, str) for p in image_paths_in_series):
                print(f"Warning: Invalid data for series '{current_item.text()}'. Expected list of strings, got {type(image_paths_in_series)}.")
                self.image_display_widget.clear_images()
                self.status_bar.showMessage("Error: Invalid data for selected series.", 5000)
                return

            if image_paths_in_series:
                # Collect QPixmap objects for the selected series
                pixmaps_for_series = []
                for path in image_paths_in_series:
                    pixmap = self.loaded_pixmaps.get(path)
                    if pixmap:
                        pixmaps_for_series.append(pixmap)
                    else:
                        print(f"Warning: Pixmap for path {path} not found in loaded_pixmaps for series {current_item.text()}")

                if not pixmaps_for_series:
                    print(f"No valid pixmaps found for series: {current_item.text()}")
                    self.image_display_widget.clear_images()
                    self.status_bar.showMessage(f"No valid pixmaps for series: {current_item.text()}", 5000)
                    return

                # Call appropriate display method based on current mode
                if self.current_display_mode == "Side-by-Side":
                    self.image_display_widget.set_pixmaps(pixmaps_for_series)
                    self.status_bar.showMessage(f"Displaying {len(pixmaps_for_series)} images side-by-side for: {current_item.text()}", 5000)
                elif self.image_display_widget.display_mode == "Overlay": # Check ImageWidget's mode
                    # For Overlay, set_pixmaps would have been called already.
                    # ImageWidget handles showing the current_overlay_index.
                    # Update status bar based on current overlay index.
                    num_images_in_series = len(pixmaps_for_series)
                    current_idx_display = self.image_display_widget.current_overlay_index + 1
                    self.status_bar.showMessage(f"Overlay: Image {current_idx_display}/{num_images_in_series} for: {current_item.text()}", 5000)
                else:
                    self.image_display_widget.clear_images() # Should not happen
                    print(f"Unknown display mode in _on_series_selection_changed: {self.image_display_widget.display_mode}")
            else:
                self.image_display_widget.clear_images()
                print(f"Warning: Selected series '{current_item.text()}' has an empty image list.")
                self.status_bar.showMessage("Selected series contains no images.", 5000)
        else:
            self.image_display_widget.clear_images()
            print("No series selected.")
            self.status_bar.showMessage("No series selected.", 2000)

    def _trigger_series_display_update(self):
        """
        Helper method to re-apply the display logic for the currently selected series.
        Useful after display mode changes.
        """
        current_selected_item = self.series_list_widget.currentItem()
        if current_selected_item:
            self._on_series_selection_changed(current_selected_item, None)
        else:
            self.image_display_widget.clear_images()


if __name__ == '__main__':
    # This allows testing the window directly if run as a script
    import sys
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())

    def keyPressEvent(self, event: QKeyEvent):
        """
        Handles key presses for navigation, primarily for overlay mode.
        """
        accepted = False
        if self.image_display_widget.display_mode == "Overlay":
            if event.key() == Qt.Key_Right or event.key() == Qt.Key_PageDown:
                self.image_display_widget.next_image_overlay()
                accepted = True
            elif event.key() == Qt.Key_Left or event.key() == Qt.Key_PageUp:
                self.image_display_widget.prev_image_overlay()
                accepted = True

            if accepted:
                # Update status bar after navigation
                current_series_item = self.series_list_widget.currentItem()
                if current_series_item:
                    paths_in_series = current_series_item.data(Qt.UserRole)
                    if paths_in_series and isinstance(paths_in_series, list):
                        num_images = len(paths_in_series)
                        if num_images > 0:
                            current_idx_display = self.image_display_widget.current_overlay_index + 1
                            self.status_bar.showMessage(f"Overlay: Image {current_idx_display}/{num_images}", 3000)

        if accepted:
            event.accept()
        else:
            # Important to call superclass method for unhandled events
            super().keyPressEvent(event)
