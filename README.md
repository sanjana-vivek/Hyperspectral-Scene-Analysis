# Hyperspectral Cube Characterisation

A Python-based pipeline for exploratory analysis and characterisation of EnMAP hyperspectral imaging (HSI) data cubes.

> ⚠️ **Work in progress** — initial commit. Structure and documentation will evolve.

---

## Overview

This project provides a set of diagnostic tools to inspect, validate, and characterise EnMAP hyperspectral cubes before any scientific processing. It covers everything from basic raster metadata checks to spectral band analysis and quality assessment.

---

## What It Does

| Step | Description |
|------|-------------|
| Raster metadata | Validates spatial/spectral dimensions, CRS, data type, and memory footprint |
| Band value ranges | Computes per-band min/max DN values as an early quality check |
| Band visualisation | Plots individual bands as monochromatic images |
| RGB composite | Simulates a pseudo-RGB view by mapping nearest bands to R, G, B |
| Wavelength + FWHM loading | Imports center wavelength (CW) and bandwidth from external Excel metadata |
| Spectral resolution | Computes mean/min/max FWHM across all bands |
| Gaussian bandpass curves | Models each band's spectral response function (SRF) as a Gaussian |
| Band spacing analysis | Measures spacing between adjacent center wavelengths |
| Spectral redundancy index | Quantifies uniformity of spectral sampling (SIR) |
| Diagnostic band finder | Locates bands closest to known absorption features (e.g. chlorophyll at 660 nm) |
| SNR estimation | Derives a relative SNR curve from FWHM values |
| High-value band ranking | Scores and ranks bands by spectral informativeness |

---

## Why External Metadata?

HySpecNet-11k strips all spectral metadata from TIFF files to reduce size for ML research. Wavelength and FWHM values must be loaded from an accompanying Excel file. Without this, the cube is effectively 224 unlabelled grayscale images.

---

## Data

This pipeline is designed for **EnMAP Level-2A** products (atmospherically corrected surface reflectance). Using L1B or L1C data means you are working with radiance, not reflectance — keep this in mind when interpreting results.

---

## Requirements

- Python 3.x
- `rasterio`
- `numpy`
- `matplotlib`
- `pandas`

---

## Status

- [x] Metadata inspection
- [x] Band diagnostics
- [x] Spectral characterisation
- [ ] Cloud/shadow masking
- [ ] Atmospheric correction integration
- [ ] ML feature selection pipeline

---

## References

- [EnMAP mission](https://www.enmap.org/)
- [HySpecNet-11k dataset](https://hyspecnet.rsim.berlin/)
