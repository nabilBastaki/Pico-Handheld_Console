# 🎮 Raspberry Pi Pico 2W Handheld Console

Welcome to the Pico 2W Handheld Console project! This repository contains all the hardware files, software firmware, and step-by-step instructions needed to build your own portable gaming device.

---

## 📂 Project Structure

* **/Hardware**: Contains KiCad PCB design files, schematics, and the Bill of Materials (BOM).
* **/Software**: Contains the MicroPython firmware (`main.py`, `diagnostics.py`, `ili9341.py`, `boot.py`).
* **/Guidelines**: **Start here!** These are your step-by-step assembly and user manuals in PDF format.

---

## 🚀 Getting Started (The Build Process)

Please follow the documentation in the **/Guidelines** folder in this specific order:

1.  **01: Soldering & Assembly (PDF)**: Learn the "Golden Rule" of assembly and how to handle the ESOP-8 charger and SOT-23-6 MOSFET.
2.  **02: Initial Power-On Check (PDF)**: Perform critical "Cold Checks" with a multi-meter to ensure your board is safe.
3.  **03: Software Installation (PDF)**: Upload the firmware files to your Pico 2W using Thonny—no coding required!
4.  **04: Console User Manual (PDF)**: Learn how to charge your device, use the "Hold-to-Setup" menu, and handle the LiPo battery safely.
5.  **05: Hardware Troubleshooting (PDF)**: If your screen is white or the buzzer won't stop, use this table to find the fix.
6.  **06: Sign_Off_Sheet (PDF)**: Checklist that includes milestones for each team to keep track of progress and ensure correct procedures.

---

## ⚠️ Important Safety Note

**This project uses a Lithium-Polymer (LiPo) battery.** You must read Section 2 of the User Manual before connecting the battery to your PCB to avoid damage or safety hazards.
