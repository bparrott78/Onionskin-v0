import os
from PyQt5.QtCore import QObject, pyqtSignal, QFileSystemWatcher
from PyQt5.QtWidgets import QApplication # For testing purposes

class FolderWatcher(QObject):
    """
    Watches a specified folder for new image files.
    """
    new_images_detected = pyqtSignal(list)

    def __init__(self, parent=None):
        """
        Initializes the FolderWatcher.
        """
        super().__init__(parent)
        self._watcher = QFileSystemWatcher()
        self._watched_folder = ""
        self._processed_files = set()

        self._watcher.directoryChanged.connect(self._on_directory_changed)

    def set_folder(self, folder_path):
        """
        Sets the directory to watch for new images.

        Args:
            folder_path (str): The path to the folder to watch.
        """
        if not os.path.isdir(folder_path):
            print(f"Error: Folder not found at {folder_path}") # Or raise an error
            return

        if self._watched_folder and self._watched_folder in self._watcher.directories():
            self._watcher.removePath(self._watched_folder)

        self._watcher.addPath(folder_path)
        self._watched_folder = folder_path
        self._processed_files.clear() # Clear processed files when folder changes
        print(f"Now watching: {self._watched_folder}")
        # Initial scan for existing images
        self._scan_folder_for_images()

    def _on_directory_changed(self, path):
        """
        Slot called when the watched directory's content changes.

        Args:
            path (str): The path of the directory that changed.
        """
        if path == self._watched_folder:
            print(f"Directory changed: {path}")
            self._scan_folder_for_images()

    def _scan_folder_for_images(self):
        """
        Scans the watched folder for new image files and emits a signal.
        """
        if not self._watched_folder:
            return

        try:
            all_files = [os.path.join(self._watched_folder, f) for f in os.listdir(self._watched_folder)
                         if os.path.isfile(os.path.join(self._watched_folder, f))]
        except FileNotFoundError:
            print(f"Error: Watched folder {self._watched_folder} not found during scan.")
            return # Or handle more gracefully

        image_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".gif"}
        new_image_files = []

        for file_path in all_files:
            _, ext = os.path.splitext(file_path)
            if ext.lower() in image_extensions and file_path not in self._processed_files:
                new_image_files.append(file_path)

        if new_image_files:
            self._processed_files.update(new_image_files)
            self.new_images_detected.emit(new_image_files)
            print(f"Detected new images: {new_image_files}")

if __name__ == '__main__':
    # Example Usage (for testing)
    import sys
    from PyQt5.QtCore import QTimer

    app = QApplication(sys.argv)

    # Create a dummy folder for testing
    test_folder = "test_image_folder"
    if not os.path.exists(test_folder):
        os.makedirs(test_folder)

    # Create some dummy image files
    with open(os.path.join(test_folder, "img1.png"), "w") as f: f.write("")
    with open(os.path.join(test_folder, "img2.jpg"), "w") as f: f.write("")

    watcher = FolderWatcher()
    watcher.set_folder(test_folder)

    def on_new_images(images):
        print(f"Signal received for new images: {images}")

    watcher.new_images_detected.connect(on_new_images)

    # Simulate adding a new file after a delay
    def add_new_file():
        print("Adding a new test file...")
        with open(os.path.join(test_folder, f"img{len(os.listdir(test_folder)) + 1}.jpeg"), "w") as f:
            f.write("dummy content")
        # QFileSystemWatcher might need a moment, or might trigger on its own.
        # Forcing a manual scan can be done for more immediate testing if needed,
        # but ideally the watcher picks it up.
        # watcher._scan_folder_for_images() # Not ideal for real use, watcher should trigger

    QTimer.singleShot(2000, add_new_file) # Add after 2 seconds
    QTimer.singleShot(4000, lambda: QApplication.instance().quit()) # Quit after 4 seconds

    print("Starting test event loop...")
    sys.exit(app.exec_())
