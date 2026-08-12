"""Count sunspots in an SDO image using OpenCV.

The disc is isolated by thresholding and a morphological close, the background is
removed with a flood fill, and the remaining dark regions are counted as sunspots
once small blobs and limb artifacts are filtered out.
"""

import cv2
import numpy as np

from settings import data_path

# Ignore blobs smaller than this many pixels; below it, noise dominates.
MIN_CONTOUR_AREA = 2000
# Ignore contours near the right limb, where the disc edge produces false positives.
LIMB_CUTOFF = 0.90


def calculate_sun_surface_area(image_path):
    """Return the sun's area in pixels, or None if the image cannot be read."""
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        print(f"Error: could not load image at {image_path}")
        return None

    _, binary_image = cv2.threshold(image, 1, 255, cv2.THRESH_BINARY)
    return int(np.sum(binary_image == 255))


def process_sun_image(image_path, save_debug_images=False):
    """Return (sunspot_count, annotated_image_path) for an SDO image."""
    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        print(f"Error: could not load image at {image_path}")
        return 0, None

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Isolate the bright disc, then close small holes inside it.
    _, binary_image = cv2.threshold(gray_image, 60, 255, cv2.THRESH_BINARY)
    kernel = np.ones((5, 5), np.uint8)
    binary_image = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)

    # Flood fill from the first background pixel; the mask must be 2px larger.
    height, width = binary_image.shape[:2]
    mask = np.zeros((height + 2, width + 2), np.uint8)
    background_pixels = np.argwhere(binary_image == 0)
    if background_pixels.size == 0:
        print("Error: no background found; the image may be fully saturated.")
        return 0, None
    flood_start = tuple(int(value) for value in background_pixels[0][::-1])
    cv2.floodFill(binary_image, mask, flood_start, 255)

    # Invert to select the sunspots, then blank the border so the frame edge
    # is not detected as a contour.
    mask = cv2.bitwise_not(mask)
    mask[:, 0] = 0
    mask[:, width + 1] = 0
    mask[0, :] = 0
    mask[height + 1, :] = 0

    sunspots = cv2.bitwise_and(
        binary_image, binary_image, mask=mask[1 : height + 1, 1 : width + 1]
    )
    sunspots = cv2.bitwise_not(sunspots)

    contours, _ = cv2.findContours(
        sunspots, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    filtered_contours = [
        contour
        for contour in contours
        if cv2.contourArea(contour) > MIN_CONTOUR_AREA
        and cv2.boundingRect(contour)[0] < image.shape[1] * LIMB_CUTOFF
    ]

    cv2.drawContours(image, filtered_contours, -1, (0, 255, 0), 2)

    if save_debug_images:
        cv2.imwrite(str(data_path("gray_image.jpg")), gray_image)
        cv2.imwrite(str(data_path("binary_image.jpg")), binary_image)
        cv2.imwrite(str(data_path("mask.jpg")), mask)
        cv2.imwrite(str(data_path("sunspots.jpg")), sunspots)

    annotated_path = data_path("image_with_contours.jpg")
    cv2.imwrite(str(annotated_path), image)

    return len(filtered_contours), annotated_path


if __name__ == "__main__":
    count, annotated = process_sun_image(
        data_path("latest_4096_0193.jpg"), save_debug_images=True
    )
    print(f"Sunspots detected: {count}")
    print(f"Annotated image: {annotated}")
