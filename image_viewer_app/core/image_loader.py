from PyQt5.QtGui import QImage, QPixmap

def load_qimage(file_path: str) -> QImage | None:
    """
    Loads an image file into a QImage object.

    Args:
        file_path (str): The path to the image file.

    Returns:
        QImage | None: The loaded QImage object, or None if loading fails.
    """
    if not file_path:
        print("Error: No file path provided to load_qimage.")
        return None

    image = QImage(file_path)

    if image.isNull():
        print(f"Error: Failed to load image or image is null: {file_path}")
        return None

    return image

def load_qpixmap(file_path: str) -> QPixmap | None:
    """
    Loads an image file into a QPixmap object.

    Args:
        file_path (str): The path to the image file.

    Returns:
        QPixmap | None: The loaded QPixmap object, or None if loading fails.
    """
    if not file_path:
        print("Error: No file path provided to load_qpixmap.")
        return None

    pixmap = QPixmap(file_path)

    if pixmap.isNull():
        print(f"Error: Failed to load pixmap or pixmap is null: {file_path}")
        return None

    return pixmap

if __name__ == '__main__':
    # This part is for basic testing.
    # You would need a Qt application context to fully test QPixmap/QImage loading in some environments.
    # And actual image files.

    # Create dummy files for testing (if you have image files, replace these paths)
    import os
    from PyQt5.QtWidgets import QApplication
    import sys

    # It's good practice to have a QApplication instance for Qt GUI modules
    app = QApplication(sys.argv)

    test_image_dir = "test_images"
    if not os.path.exists(test_image_dir):
        os.makedirs(test_image_dir)

    # Note: These are empty files and won't load as valid images.
    # Replace with actual small image files for real testing.
    dummy_image_path_png = os.path.join(test_image_dir, "dummy.png")
    dummy_image_path_jpg = os.path.join(test_image_dir, "dummy.jpg")
    invalid_image_path = os.path.join(test_image_dir, "invalid.txt")

    with open(dummy_image_path_png, 'w') as f: f.write('') # Empty file, QImage/QPixmap will be null
    with open(dummy_image_path_jpg, 'w') as f: f.write('') # Empty file
    with open(invalid_image_path, 'w') as f: f.write('this is not an image')

    print("--- Testing load_qimage ---")
    img_png = load_qimage(dummy_image_path_png)
    if img_png:
        print(f"Successfully loaded {dummy_image_path_png} as QImage. Size: {img_png.size()}")
    else:
        print(f"Failed to load {dummy_image_path_png} as QImage.")

    img_invalid = load_qimage(invalid_image_path)
    if img_invalid:
        print(f"Successfully loaded {invalid_image_path} as QImage. Size: {img_invalid.size()}")
    else:
        print(f"Failed to load {invalid_image_path} as QImage.")

    img_none = load_qimage("")
    if img_none:
        print(f"Successfully loaded empty path as QImage. Size: {img_none.size()}")
    else:
        print(f"Failed to load empty path as QImage.")


    print("\n--- Testing load_qpixmap ---")
    pix_jpg = load_qpixmap(dummy_image_path_jpg)
    if pix_jpg:
        print(f"Successfully loaded {dummy_image_path_jpg} as QPixmap. Size: {pix_jpg.size()}")
    else:
        print(f"Failed to load {dummy_image_path_jpg} as QPixmap.")

    pix_invalid = load_qpixmap(invalid_image_path)
    if pix_invalid:
        print(f"Successfully loaded {invalid_image_path} as QPixmap. Size: {pix_invalid.size()}")
    else:
        print(f"Failed to load {invalid_image_path} as QPixmap.")

    pix_none = load_qpixmap("")
    if pix_none:
        print(f"Successfully loaded empty path as QPixmap. Size: {pix_none.size()}")
    else:
        print(f"Failed to load empty path as QPixmap.")

    # Clean up dummy files
    # os.remove(dummy_image_path_png)
    # os.remove(dummy_image_path_jpg)
    # os.remove(invalid_image_path)
    # os.rmdir(test_image_dir)

    # No app.exec_() needed if not displaying GUI, but QApplication is good for resource initialization.
    # If you were creating widgets that use these images, then app.exec_() would be necessary.
    print("\nTest complete. Note: Loading empty files will result in null QImage/QPixmap.")

    # For a more thorough test, you'd use actual valid image files.
    # Example with a hypothetical valid image (replace with a real path if you have one):
    # valid_image_path = "path/to/your/actual/image.png"
    # if os.path.exists(valid_image_path):
    #     print(f"\n--- Testing with a valid image: {valid_image_path} ---")
    #     valid_qimg = load_qimage(valid_image_path)
    #     if valid_qimg:
    #         print(f"Loaded QImage: {valid_qimg.width()}x{valid_qimg.height()}")
    #     valid_qpix = load_qpixmap(valid_image_path)
    #     if valid_qpix:
    #         print(f"Loaded QPixmap: {valid_qpix.width()}x{valid_qpix.height()}")
    # else:
    #     print(f"\nSkipping valid image test: {valid_image_path} not found.")

```
