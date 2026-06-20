# PySmith-LMBA

> **Pre-design GUI for Load Modulated Balanced Amplifiers (LMBA)**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## Overview

PySmith-LMBA is a desktop application for rapid pre-design and visualization of **Load Modulated Balanced Amplifier (LMBA)** architectures. It calculates the required control-amplifier impedance from user-defined load and target impedances, renders the result on a **Smith chart**, and exports the design session to CSV.

## Features

- **Interactive Smith Chart** — real-time impedance visualization powered by `scikit-rf` and Matplotlib
- **Design Parameter Inputs** — Z_opt (real/imaginary), Z_target, power limits, coupler loss
- **Status Indicator** — LED-style widget shows pass / fail / warning states
- **CSV Export** — saves every evaluated design point to `lmba_tasarim_sonuclari.csv`
- **Clean GUI** — built with Tkinter/ttk; no external UI framework required

## Requirements

```
numpy
matplotlib
scikit-rf
tkinter  # included with standard Python on Windows
```

Install dependencies:

```bash
pip install numpy matplotlib scikit-rf
```

## Usage

```bash
python lmba_smith.chart.py
```

1. Enter the impedance parameters in the left panel.
2. Click **Evaluate and Save** to compute and plot.
3. Review the Smith chart on the right and check the status LED.
4. Results are automatically appended to `lmba_tasarim_sonuclari.csv`.

## Parameters

| Parameter | Description | Default |
|---|---|---|
| Z_opt Real | Optimal load resistance (Ω) | 15 |
| Z_opt Imaginary | Optimal load reactance (jΩ) | 30 |
| Z_target Real | Target impedance resistance (Ω) | 45 |
| Z_target Imaginary | Target impedance reactance (jΩ) | 10 |
| Power Limit (CA) | Control amplifier max output (dBm) | 37 |
| Main DUT Power | Main amplifier output power (dBm) | 40 |
| Coupler Loss | 90° hybrid coupler insertion loss (dB) | 0.7 |

## Author

**Engin Can Cicek**
