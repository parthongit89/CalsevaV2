# CalSEVA V2 🛠️📐

CalSEVA (Calibration Assistant & Asset Management Utility) is a secure, local-first web and mobile application designed to streamline industrial calibration scheduling, asset tracking, and compliance reporting. Version 2 builds upon the core architecture with enhanced UI components, faster localized processing, and optimized asset lifecycle tracking.

---

## 🚀 Key Features

* **Local-First Architecture:** Maximizes user data privacy and performance by storing all machinery records, scheduling parameters, and calibration history strictly in local device storage.
* **Automated Scheduling & Reminders:** Helps operators stay ahead of audit cycles with configurable calibration intervals, early-warning triggers, and drift thresholds.
* **QR Code Ecosystem:** Instantly generates unique asset identification tags for equipment lookup, verification, and swift on-site data logging via a built-in scanning utility.
* **Compliance-Ready PDF Reports:** Compiles raw "As-Found" and "As-Left" input data into professional, signed, and tamper-resistant calibration certificates on the fly.
* **Premium Dark Mode UI:** Features a modern, scannable Midnight Black interface with crisp, glassmorphic layout elements for clarity in industrial shop-floor environments.

---

## 🛠️ Tech Stack & Architecture

* **Frontend:** Built with responsive design principles using modern web and mobile frameworks supporting desktop, tablet, and mobile displays.
* **Styling:** Premium dark aesthetics with soft accent palettes optimized for high-contrast visibility.
* **Storage Engine:** 100% Client-Side Local Storage (No external cloud database dependencies, ensuring total local data ownership).
* **Integrations:** On-device engines for dynamic PDF compilation, QR generation/scanning, and localized date utilities.

---

## 📋 Standard Operating Guidelines

To maintain data integrity and compliance across your testing environment:
1. **Regular Data Exports:** Because all data remains strictly on your device, users should manually export generated PDFs and backup database objects regularly to avoid data loss from cleared caches or device hardware failures.
2. **Standardized Asset Naming:** Follow a consistent organizational schema (e.g., `DEPT-TYPE-NUMBER`) when registering machinery for flawless search optimization.
3. **Hardware Deployment:** Print generated QR tags on high-durability, industrial-grade thermal or laminated labels to withstand temperature variations, friction, and chemicals.

---

## 🔒 Privacy & Terms Summary

* **Data Ownership:** CalSEVA does not transmit, collect, or mirror industrial asset details to any third-party remote servers. Your configuration is strictly your own.
* **Liability Disclaimer:** CalSEVA acts as a localized data management assistant. Accuracy of entered formulas, error tolerances (MPE), and compliance with industrial standards (such as ISO/IEC 17025) remains the sole responsibility of the certified technician operating the app.

---

## 🏗️ Setup & Installation

*(Modify these steps based on your specific framework environment)*

1. Clone the repository:
   ```bash
   git clone https://github.com/parthongit89/CalsevaV2.git
   cd CalsevaV2
   ```
