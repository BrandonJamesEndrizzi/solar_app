import pytest

cv2 = pytest.importorskip("cv2")
np = pytest.importorskip("numpy")
pytest.importorskip("dotenv")

import analyze_image

DISC_VALUE = 200


def draw_disc(size=1024, radius=500):
    """Return a synthetic SDO-like frame: bright disc on a black background."""
    image = np.zeros((size, size, 3), dtype=np.uint8)
    center = (size // 2, size // 2)
    cv2.circle(image, center, radius, (DISC_VALUE,) * 3, thickness=-1)
    return image


def save(tmp_path, image, name="sun.png"):
    path = tmp_path / name
    cv2.imwrite(str(path), image)
    return path


def test_counts_large_spots_and_ignores_noise_and_limb(tmp_path):
    image = draw_disc()

    # Two real sunspots, comfortably above MIN_CONTOUR_AREA.
    cv2.circle(image, (400, 400), 40, (0, 0, 0), thickness=-1)
    cv2.circle(image, (600, 550), 40, (0, 0, 0), thickness=-1)
    # Too small to count: below the noise floor.
    cv2.circle(image, (300, 600), 15, (0, 0, 0), thickness=-1)
    # Large enough, but in the right-limb exclusion zone (x > 90% of width).
    cv2.circle(image, (960, 512), 35, (0, 0, 0), thickness=-1)

    count, annotated = analyze_image.process_sun_image(save(tmp_path, image))

    assert count == 2
    assert annotated is not None


def test_clean_disc_has_no_spots(tmp_path):
    count, annotated = analyze_image.process_sun_image(save(tmp_path, draw_disc()))
    assert count == 0
    assert annotated is not None


def test_missing_file_returns_zero():
    count, annotated = analyze_image.process_sun_image("/nonexistent/sun.png")
    assert (count, annotated) == (0, None)


def test_saturated_image_returns_zero(tmp_path):
    white = np.full((256, 256, 3), 255, dtype=np.uint8)
    count, annotated = analyze_image.process_sun_image(save(tmp_path, white))
    assert (count, annotated) == (0, None)


def test_surface_area_of_disc(tmp_path):
    image = np.zeros((512, 512, 3), dtype=np.uint8)
    cv2.circle(image, (256, 256), 100, (DISC_VALUE,) * 3, thickness=-1)

    area = analyze_image.calculate_sun_surface_area(save(tmp_path, image))

    expected = np.pi * 100**2
    assert area == pytest.approx(expected, rel=0.02)


def test_surface_area_missing_file_returns_none():
    assert analyze_image.calculate_sun_surface_area("/nonexistent/sun.png") is None
