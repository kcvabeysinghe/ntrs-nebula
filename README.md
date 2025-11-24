# NTRS Nebula: Zero-Point Optical Encryption Protocol
[![PyPI version](https://badge.fury.io/py/ntrs-nebula.svg)](https://badge.fury.io/py/ntrs-nebula)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Downloads](https://static.pepy.tech/badge/ntrs-nebula)](https://pepy.tech/project/ntrs-nebula)

**Created by CHETHANA ABEYSINGHE**

> **NTRS (Nano-Topographic Radial Steganography)** is a revolutionary optical encryption protocol. Unlike traditional steganography that hides data in pixel values (LSB), NTRS wipes the value and stores data as a **Coordinate Map** (Zero-Point Dots) in the Alpha Channel.

The result is an encryption layer that is mathematically indistinguishable from random CCD sensor noise.

---

## 🚀 Features

* **🌌 Zero-Point Logic:** Discards binary values and stores data as *coordinates* (sparse index mapping).
* **🔒 Nebula Hash:** Uses a custom non-linear chaos stream cipher for coordinate shuffling (No AES).
* **👻 Matrix Stealth:** 100% Invisible Alpha-Channel encoding (Quantum Limit 1px).
* **🛡️ Parity Check:** Integrated Reed-Solomon error correction (Survives ~20% image corruption).

---

## 📦 Installation

### Option A: For Normal Users (Windows App)
If you just want to use the tool without coding:
1.  Download **NTRS_Nebula.exe** from the [**Releases Page**](../../releases).
2.  Open your Command Prompt (cmd) or PowerShell.
3.  Run the commands in the Usage Guide below.

### Option B: For Developers (Python Library)
If you want to use the protocol inside your own Python scripts:
```bash
pip install ntrs-nebula
```

---

## 💻 Usage Guide

### 1. Using the Windows App (CLI)

**To Encrypt (Hide a Message):**
This command takes your text and hides it inside `image.png`.
```bash
NTRS_Nebula.exe encrypt --text "This is a secret message" --image image.png --password "MyStrongPass123"
```

**To Decrypt (Read a Message):**
This command reads the invisible dots from `image.png` and reveals the text.
```bash
NTRS_Nebula.exe decrypt --image image.png --password "MyStrongPass123"
```

### 2. Using the Python Library
You can import NTRS into your own projects to build secure communication tools.

**Initialization:**
```python
from ntrs.core import NTRS

# Initialize the engine with a seed password
engine = NTRS("MySecurePassword")
```

**Encryption (Encode):**
```python
secret_text = "Launch Code: 8841-9921"
target_image = "database_backup.png"

# This will modify the image in-place
engine.encode(secret_text, target_image)
print(f"Data successfully hidden in {target_image}")
```

**Decryption (Decode):**
```python
target_image = "database_backup.png"

try:
    # Attempt to recover the data
    decrypted_text = engine.decode(target_image)
    print(f"Recovered Message: {decrypted_text}")
except Exception as e:
    print("Decryption failed. Image might be corrupted or password incorrect.")
```

---

## ⚔️ The Security Challenge
I am releasing the core logic as open source to verify the strength of the **Zero-Point Logic**.

I challenge the cybersecurity community to:
1.  Analyze the `_nebula_hash` function in `src/ntrs/core.py`.
2.  Attempt to distinguish an NTRS Dot from random sensor noise.
3.  Try to reverse the coordinate map without the seed.

## ⚙️ Technical Specs
* **Encryption:** NTRS Nebula Hash (Custom Chaos Stream)
* **Error Correction:** Reed-Solomon (RSCodec-10)
* **Signal Separation:** Alpha-Channel Dithering (Δ1 value difference)
* **Coordinate System:** Radial Sparse Indexing

## 📄 License
This project is protected under the **GNU General Public License v3.0 (GPLv3)**.
Commercial use, modification, or distribution requires explicit attribution to the original author, **CHETHANA ABEYSINGHE**.
