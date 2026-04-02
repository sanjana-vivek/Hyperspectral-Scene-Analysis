"""
HYPERSPECTRAL CUBE: INITIAL SCIENTIFIC CHARACTERIZATION
Dataset: HySpecNet-11k (EnMAP-based, 224-band)
This version prints interpretations and reliability for every computation.
"""

import rasterio
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# ================================================================
# 1. LOAD HYPERSPECTRAL CUBE
# ================================================================
tif_path = "/Users/sanjana/Documents/Sanjana/college-VIT/ Capstone/dims_op_oc_oc-en_703007042_1/ENMAP.HSI.L1B/ENMAP01-____L1B-DT0000159169_20251020T104259Z_023_V010505_20251204T142809Z/ENMAP01-____L1B-DT0000159169_20251020T104259Z_023_V010505_20251204T142809Z-SPECTRAL_IMAGE_SWIR.TIF"
xls_path = "/Users/sanjana/Downloads/enmap_band_metadata.xlsx"

print("\n================= BASIC RASTER METADATA =================\n")

with rasterio.open(tif_path) as src:
    print("Driver:      ", src.driver)
    print("Width:       ", src.width)
    print("Height:      ", src.height)
    print("Bands:       ", src.count)
    print("Data type:   ", src.dtypes[0])
    print("CRS:         ", src.crs)
    print("Transform:   ", src.transform)

    file_size = os.path.getsize(tif_path) / (1024 * 1024)
    print(f"File size:   {file_size:.2f} MB")


# ================================================================
# 2. BAND VALUE RANGES
# ================================================================
print("\n================= BAND VALUE RANGES =================\n")

with rasterio.open(tif_path) as src:
    for b in [1, 30, 50, 100, 120, 130, 133]:
        band = src.read(b)
        print(f"Band {b}: min={band.min()} max={band.max()}")


# ================================================================
# 3. VISUALIZE A SINGLE BAND
# ================================================================
with rasterio.open(tif_path) as src:
    band_num = 100
    band = src.read(band_num)

plt.figure(figsize=(6, 6))
plt.imshow(band, cmap='gray')
plt.title(f"Band {band_num}")
plt.axis('off')
plt.show()


# ================================================================
# 4. APPROXIMATE RGB COMPOSITE
# ================================================================
with rasterio.open(tif_path) as src:
    r = src.read(43).astype(float)
    g = src.read(28).astype(float)
    b = src.read(10).astype(float)

def norm(x):
    return (x - x.min()) / (x.max() - x.min())

rgb = np.dstack([norm(r), norm(g), norm(b)])

plt.figure(figsize=(7,7))
plt.imshow(rgb)
plt.title("Approximate RGB Composite")
plt.axis("off")
plt.show()


# ================================================================
# 5. METADATA PRESENCE
# ================================================================
with rasterio.open(tif_path) as src:
    meta = src.tags()
    band_meta = src.tags(50)

print("\n================= RASTER METADATA KEYS =================\n")
print("Main metadata keys:", meta.keys())
print("Band 50 metadata:", band_meta)

print("""
INTERPRETATION:
- HySpecNet strips spectral metadata → no wavelengths stored in TIFF.
- Must use external metadata (Excel).
RELIABILITY: HIGH (metadata is intentionally removed).
""")

# ================================================================
# 6. LOAD WAVELENGTH + FWHM FROM EXCEL
# ================================================================
print("\n================= LOADING EXCEL METADATA =================\n")

df = pd.read_excel(xls_path)
print(df.head())
print(df.columns)

cw   = df["CW (nm)"].to_numpy()
fwhm = df["FWHM (nm)"].to_numpy()
bands = df["BAND #"].to_numpy()

print("""
INTERPRETATION:
- CW = center wavelength → physical location of band.
- FWHM = bandwidth → spectral resolution.
RELIABILITY: HIGH (official EnMAP metadata).
""")

# ================================================================
# 7. SPECTRAL RESOLUTION
# ================================================================
def spectral_resolution(fwhm):
    return np.mean(fwhm), np.min(fwhm), np.max(fwhm)

mean_res, min_res, max_res = spectral_resolution(fwhm)

print("\n================= SPECTRAL RESOLUTION =================\n")
print("Mean spectral resolution (nm):", mean_res)
print("Range:", min_res, "to", max_res)

print("""
INTERPRETATION:
- Narrow FWHM → ability to detect fine absorption features.
- Wider FWHM → higher signal-to-noise ratio.
RELIABILITY: HIGH.
""")

# ================================================================
# 8. GAUSSIAN BANDPASS CURVES
# ================================================================
def bandpass_gaussian(cw, fwhm, num_points=1000):
    lambda_min = cw.min() - 20
    lambda_max = cw.max() + 20
    wavelengths = np.linspace(lambda_min, lambda_max, num_points)

    responses = []
    for c, w in zip(cw, fwhm):
        sigma = w / (2*np.sqrt(2*np.log(2)))
        resp = np.exp(-0.5 * ((wavelengths - c) / sigma)**2)
        responses.append(resp)

    return wavelengths, np.array(responses)

wavelengths, response_curves = bandpass_gaussian(cw, fwhm)

print("\n================= GAUSSIAN BANDPASS MODEL =================\n")
print(f"Generated {len(response_curves)} spectral response curves.")

print("""
INTERPRETATION:
- Approximates bandwidth and sensitivity of each VNIR band.
- Shows band overlap → spectral redundancy.
RELIABILITY: MEDIUM (Gaussian approximation).
""")

# ================================================================
# 9. MATERIAL SEPARABILITY INDEX
# ================================================================
def material_separability(cw):
    diffs = np.diff(cw)
    return diffs.mean(), diffs.min(), diffs.max()

ms_mean, ms_min, ms_max = material_separability(cw)

print("\n================= MATERIAL SEPARABILITY INDEX =================\n")
print("Mean band spacing (nm):", ms_mean)
print("Band spacing range:", ms_min, "–", ms_max)

print("""
INTERPRETATION:
- Defines how finely wavelengths are sampled.
- Smaller spacing → ability to distinguish vegetation pigments, minerals.
RELIABILITY: HIGH.
""")

# ================================================================
# 10. SPECTRAL INFORMATION REDUNDANCY
# ================================================================
def spectral_redundancy(cw):
    diffs = np.diff(cw)
    return np.std(diffs) / np.mean(diffs)

sir = spectral_redundancy(cw)

print("\n================= SPECTRAL INFORMATION REDUNDANCY =================\n")
print("Redundancy index:", sir)

print("""
INTERPRETATION:
- Hyperspectral sensors intentionally oversample the spectrum.
- Low redundancy = more unique information.
RELIABILITY: HIGH.
""")

# ================================================================
# 11. DIAGNOSTIC BAND FINDER
# ================================================================
def find_band(cw, target):
    return np.argmin(np.abs(cw - target)) + 1

red_band = find_band(cw, 660)
nir_band = find_band(cw, 850)
water_band = find_band(cw, 970)
chlorophyll_band = find_band(cw, 705)

print("\n================= DIAGNOSTIC BANDS =================\n")
print("Nearest RED band (~660 nm):", red_band)
print("Nearest NIR band (~850 nm):", nir_band)
print("Nearest Water Absorption (~970 nm):", water_band)
print("Nearest Red-edge (~705 nm):", chlorophyll_band)

print("""
INTERPRETATION:
- 660 nm → chlorophyll absorption
- 705 nm → red-edge (plant stress)
- 850 nm → vegetation scattering plateau
- 970 nm → water absorption
RELIABILITY: HIGH (center wavelengths accurate).
""")

# ================================================================
# 12. THEORETICAL SNR ESTIMATION
# ================================================================
def theoretical_snr(fwhm):
    return fwhm / fwhm.mean()

snr_curve = theoretical_snr(fwhm)

print("\n================= THEORETICAL SNR =================\n")
print("Relative SNR (first 10 bands):", snr_curve[:10])

print("""
INTERPRETATION:
- Wider bands capture more photons → higher SNR.
- Narrow bands → more noise but better absorption detection.
RELIABILITY: MEDIUM (relative SNR, not absolute).
""")

# ================================================================
# 13. HIGH-VALUE BANDS
# ================================================================
def high_value_bands(cw, fwhm):
    score = 1/(fwhm + np.abs(np.diff(cw, append=cw[-1])))
    idx = np.argsort(score)[-10:]
    return idx + 1

important = high_value_bands(cw, fwhm)

print("\n================= HIGH-VALUE BANDS =================\n")
print("Top 10 informative bands:", important)

print("""
INTERPRETATION:
- These bands balance narrow FWHM with unique spacing.
- Useful for classification, anomaly detection, feature selection.
RELIABILITY: MEDIUM (heuristic but meaningful).
""")
