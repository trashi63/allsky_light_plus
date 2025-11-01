# AllSky Light Plus

**Enhanced AllSky Light Meter for AllSky cameras**  
by **Helmut Hoerschgl**

This module extends the original *AllSky Light Meter* by adding:

- 🎨 Bortle color classification and hex color output  
- 🧮 SQM (mag/arcsec²) and NELM estimation  
- 🧭 Calibration mode with CSV logging  
- 🧾 Clean ASCII output for overlays  
- ⚙️ Adjustable calibration offset for site tuning  

---

## 🧑‍💻 Original Work

Based on the **AllSky Light Meter** module by  
**Alex Greenland** (AllSky Team)  
→ [https://github.com/allskyteam](https://github.com/allskyteam)

All original logic and metadata foundations remain under the same open license.  
This version was extended and refined by **Helmut Hoerschgl** in 2025.

---

## 📦 Installation

1. Copy this folder (`allsky_light_plus`) into your AllSky module directory:


2. Install dependencies:
```bash
pip3 install -r requirements.txt

python3 - <<'PY'
import allsky_light_plus
allsky_light_plus.calibration_mode(allsky_light_plus.metaData["arguments"], samples=30, delay=60) 
PY

This module follows the same open-source license as the original AllSky modules (MIT).

GitHub Repository: https://github.com/trashi63/allsky_light_plus


---

### ⚖️ **5️⃣ LICENSE**
```text
MIT License

Copyright (c) 2025 Helmut Hoerschgl

Based on original work by Alex Greenland (AllSky Team)
https://github.com/allskyteam

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

