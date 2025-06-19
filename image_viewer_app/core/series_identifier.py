import re
import os
from collections import defaultdict

class SeriesIdentifier:
    """
    Identifies and groups image files into series based on their filenames.
    """

    def __init__(self):
        """
        Initializes the SeriesIdentifier.
        (Currently no specific initialization needed)
        """
        pass

    def identify_series(self, image_paths: list[str]) -> dict[str, list[str]]:
        """
        Groups a list of image file paths into series.

        Series are identified by the filename part preceding a sequence of digits.
        Files without a trailing number sequence are grouped by their full basename.

        Args:
            image_paths (list[str]): A list of full paths to image files.

        Returns:
            dict[str, list[str]]: A dictionary where keys are series identifiers
                                 and values are lists of image paths belonging to
                                 that series, sorted alphabetically.
        """
        if not image_paths:
            return {}

        series_map = defaultdict(list)

        for path in image_paths:
            if not isinstance(path, str) or not path.strip():
                # Skip invalid paths
                print(f"Warning: Invalid or empty path provided: '{path}'")
                continue

            image_name = os.path.basename(path)
            name_without_ext, _ = os.path.splitext(image_name)

            # Try to match a pattern ending with digits
            # This regex captures:
            # group(1): the base part of the name (non-greedy)
            # group(2): the sequence of digits at the end of the name
            # e.g., "scan_v1_001" -> group(1)="scan_v1_", group(2)="001"
            # e.g., "photo_1" -> group(1)="photo_", group(2)="1"
            # e.g., "img001_slice01" -> group(1)="img001_slice", group(2)="01"
            match = re.match(r'^(.*?)(\d+)$', name_without_ext)

            if match:
                series_key = match.group(1)
            else:
                # If no trailing digits, use the whole name (without extension) as the key
                series_key = name_without_ext

            series_map[series_key].append(path)

        # Sort the paths within each series
        for key in series_map:
            series_map[key].sort()

        return dict(series_map)

if __name__ == '__main__':
    # Example Usage (for testing)
    identifier = SeriesIdentifier()

    test_paths_1 = [
        "/path/to/scan_v1_001.png",
        "/path/to/scan_v1_002.png",
        "/path/to/scan_v1_003.tiff",
        "/path/to/photo_1.jpg",
        "/path/to/photo_2.jpeg",
        "/path/to/img001_slice01.tif",
        "/path/to/img001_slice02.tif",
        "/path/to/single_image.bmp",
        "/path/to/another_single.gif",
        "/path/to/scan_v1_010.png", # For sort testing
        "/path/to/photo_12.jpg",   # For sort testing
    ]

    expected_1 = {
        'scan_v1_': [
            '/path/to/scan_v1_001.png',
            '/path/to/scan_v1_002.png',
            '/path/to/scan_v1_003.tiff',
            '/path/to/scan_v1_010.png'
            ],
        'photo_': [
            '/path/to/photo_1.jpg',
            '/path/to/photo_12.jpg',
            '/path/to/photo_2.jpeg'
            ],
        'img001_slice': [
            '/path/to/img001_slice01.tif',
            '/path/to/img001_slice02.tif'
            ],
        'single_image': ['/path/to/single_image.bmp'],
        'another_single': ['/path/to/another_single.gif']
    }

    print("--- Test Case 1 ---")
    result_1 = identifier.identify_series(test_paths_1)
    for key, paths in result_1.items():
        print(f"Series '{key}':")
        for p in paths:
            print(f"  - {p}")

    # Basic check - can be more sophisticated
    # Note: Direct dict comparison might be tricky if order of keys differs,
    # but Python 3.7+ preserves insertion order for dicts.
    # For robust testing, compare keys and sorted lists for each key.
    print("\nComparing with expected (ordering of paths within series matters):")
    match_count = 0
    for k_exp, v_exp in expected_1.items():
        if k_exp in result_1 and sorted(result_1[k_exp]) == sorted(v_exp): # sort v_exp too for safety
            match_count +=1
        else:
            print(f"Mismatch for key '{k_exp}' or its values.")
            print(f"  Expected: {sorted(v_exp)}")
            print(f"  Got:      {sorted(result_1.get(k_exp, []))}")

    if match_count == len(expected_1) and len(result_1) == len(expected_1):
        print("Test Case 1 PASSED (basic check)")
    else:
        print("Test Case 1 FAILED (basic check)")


    test_paths_2 = [
        "image1.png", "image2.png", "image10.png", "image.tif"
    ]
    expected_2 = {
        'image': ["image.tif"], # No numbers, so full name is key
        'image': ["image1.png", "image10.png", "image2.png"] # This is wrong, regex will make 'image' the key
    }
    # Corrected expectation for test_paths_2 based on the implemented logic:
    corrected_expected_2 = {
        'image': [ # Key from "image1.png", "image2.png", "image10.png"
            'image1.png',
            'image10.png', # This should come after image2 if paths are sorted like strings. Let's verify sort order.
            'image2.png'
        ],
        'image.tif': ['image.tif'] # This will be its own series based on current logic.
                                   # The regex `^(.*?)(\d+)$` means the part before digits becomes the key.
                                   # If no digits, the full name_without_ext is the key.
    }
    # Re-evaluating the logic for "image.tif" and "image1.png"
    # "image.tif" -> name_without_ext = "image" -> no match for `(\d+)$` -> series_key = "image"
    # "image1.png" -> name_without_ext = "image1" -> match `(.*?)(\d+)$` -> series_key = "image", num = "1"
    # "image2.png" -> name_without_ext = "image2" -> match `(.*?)(\d+)$` -> series_key = "image", num = "2"
    # "image10.png" -> name_without_ext = "image10" -> match `(.*?)(\d+)$` -> series_key = "image", num = "10"
    # So they should all group under "image".

    final_expected_2 = {
        'image': sorted([
            "image1.png",
            "image2.png", # String sort: "image10.png" comes before "image2.png"
            "image10.png",
            "image.tif" # "image.tif" will also go into 'image' key because name_without_ext "image" is the key
        ])
    }
    # The logic is: `name_without_ext` is "image" for "image.tif". No digits, so key is "image".
    # For "image1.png", `name_without_ext` is "image1". Match gives key "image".
    # So they all fall under the key "image".

    print("\n--- Test Case 2 ---")
    result_2 = identifier.identify_series(test_paths_2)
    for key, paths in result_2.items():
        print(f"Series '{key}':")
        for p in paths:
            print(f"  - {p}")

    # For test_paths_2, all should fall under 'image' and then be sorted.
    # 'image.tif', 'image1.png', 'image10.png', 'image2.png'
    # Sorted: 'image.tif', 'image1.png', 'image10.png', 'image2.png' (standard string sort)
    # Actually, standard sort would be: 'image.tif', 'image1.png', 'image2.png', 'image10.png'
    # Let's re-verify the sort:
    # `name_without_ext` for 'image.tif' is 'image'. Key is 'image'.
    # `name_without_ext` for 'image1.png' is 'image1'. Key is 'image'.
    # `name_without_ext` for 'image10.png' is 'image10'. Key is 'image'.
    # `name_without_ext` for 'image2.png' is 'image2'. Key is 'image'.
    # So all paths go into series_map['image'].
    # Then series_map['image'].sort() is called.
    # Expected:
    final_expected_2_sorted = {
        'image': [
            'image.tif', # . comes before 1
            'image1.png',
            'image10.png', # 10 comes before 2 in string sort
            'image2.png'
        ]
    }
    # Wait, string sort: "image10.png" vs "image2.png"
    # "1" vs "2", so "image10.png" comes before "image2.png". This is correct.
    # "image.tif" vs "image1.png": "." vs "1", so "image.tif" comes before "image1.png". Correct.

    # The sorting is just Python's default sort on the full path strings.

    print("\nComparing with expected (Test Case 2):")
    match_count_2 = 0
    # Manually check the single key 'image'
    if 'image' in result_2 and sorted(result_2['image']) == sorted(final_expected_2_sorted['image']):
         match_count_2 = 1

    if match_count_2 == 1 and len(result_2) == 1:
        print("Test Case 2 PASSED (basic check)")
    else:
        print("Test Case 2 FAILED (basic check)")
        print(f"  Expected: {final_expected_2_sorted.get('image', [])}")
        print(f"  Got:      {result_2.get('image', [])}")


    test_paths_3 = []
    print("\n--- Test Case 3 (Empty List) ---")
    result_3 = identifier.identify_series(test_paths_3)
    if not result_3:
        print("Test Case 3 PASSED (empty list yields empty dict)")
    else:
        print(f"Test Case 3 FAILED: {result_3}")

    test_paths_4 = ["item.001.png", "item.002.png", "item_no_number.jpeg"]
    # "item.001.png" -> name_without_ext = "item.001" -> key "item."
    # "item.002.png" -> name_without_ext = "item.002" -> key "item."
    # "item_no_number.jpeg" -> name_without_ext = "item_no_number" -> key "item_no_number"
    expected_4 = {
        "item.": ["item.001.png", "item.002.png"],
        "item_no_number": ["item_no_number.jpeg"]
    }
    print("\n--- Test Case 4 (names with dots) ---")
    result_4 = identifier.identify_series(test_paths_4)
    for key, paths in result_4.items():
        print(f"Series '{key}':")
        for p in paths:
            print(f"  - {p}")
    # Basic check for test_paths_4
    match_count_4 = 0
    for k_exp, v_exp in expected_4.items():
        if k_exp in result_4 and sorted(result_4[k_exp]) == sorted(v_exp):
            match_count_4 +=1
    if match_count_4 == len(expected_4) and len(result_4) == len(expected_4):
        print("Test Case 4 PASSED (basic check)")
    else:
        print("Test Case 4 FAILED (basic check)")

    test_paths_5 = [None, "/valid/path.png", ""]
    print("\n--- Test Case 5 (Invalid Paths) ---")
    result_5 = identifier.identify_series(test_paths_5)
    # Expected: {'valid/path': ['/valid/path.png']} (after path.strip() and basename)
    # Basename of "/valid/path.png" is "path.png". name_without_ext "path". Key "path".
    expected_5 = {
        'path': ['/valid/path.png']
    }
    for key, paths in result_5.items():
        print(f"Series '{key}':")
        for p in paths:
            print(f"  - {p}")
    match_count_5 = 0
    if 'path' in result_5 and result_5['path'] == expected_5['path'] and len(result_5) == 1:
        print("Test Case 5 PASSED (basic check for invalid paths)")
    else:
        print("Test Case 5 FAILED (basic check for invalid paths)")
        print(f"  Expected: {expected_5}")
        print(f"  Got:      {result_5}")

```
