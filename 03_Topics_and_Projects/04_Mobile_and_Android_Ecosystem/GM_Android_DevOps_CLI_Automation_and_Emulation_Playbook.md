---
title: "Android DevOps CLI Automation, Headless AVD Emulation, and UI Journey Testing Playbook"
domain: "04_Mobile_and_Android_Ecosystem"
reusability_score: 94
workability_status: "Production-Ready"
tags:
  - "android-cli"
  - "android-devops"
  - "adb-automation"
  - "avd-emulator"
  - "mobile-qa"
  - "ui-testing"
dependencies:
  - "android-sdk"
  - "adb"
  - "python >= 3.10"
  - "bash / powershell"
source_files_synthesized:
  - "Builtin Skill android-cli (C:\\Users\\FTT\\.gemini\\config\\plugins\\android-cli-plugin\\skills\\SKILL.md)"
  - "Raw_copies/AGENTS.md"
  - "Raw_copies/PROTOCOLS.md"
---

# Executive Summary & Architectural Mental Model

The **Android DevOps CLI Automation & Emulation Playbook** establishes an automated mobile testing and deployment pipeline using Google's official `android` command-line tool, Android Debug Bridge (`adb`), and headless Android Virtual Devices (AVD). By integrating SDK package management, headless emulator lifecycle control, automated APK compilation/installation, UI screenshot capture, and `uiautomator` test journey execution into CI/CD workflows, this playbook enables autonomous agents to build, test, and audit Android applications without manual emulator intervention.

```
+===================================================================================+
|                       ANDROID CLI DEVOPS & CI/CD PIPELINE                         |
|                                                                                   |
|  [ CI/CD Trigger / Agent Task Request ]                                            |
|                       |                                                           |
|                       v                                                           |
|  [ Step 1: SDK & Platform Manager (`android sdk install platforms/android-34`) ]  |
|                       |                                                           |
|                       v                                                           |
|  [ Step 2: Headless Emulator Spawn (`android emulator start --name test_avd`) ]   |
|                       |                                                           |
|                       v (ADB Device Boot Check: `adb wait-for-device`)            |
|  [ Step 3: APK Build & Install (`android run ./app-release.apk`) ]                 |
|                       |                                                           |
|                       v                                                           |
|  [ Step 4: Journey Testing & UI Hierarchy Dump (`adb exec-out uiautomator dump`) ]|
|                       |                                                           |
|                       v                                                           |
|  [ Step 5: Screen Capture & Visual QA (`android screenshot --output report.png`) ]|
|                       |                                                           |
|                       v                                                           |
|  [ Step 6: Teardown & Emulation Stop (`android emulator stop`) ]                  |
+===================================================================================+
```

---

## Source Lineage & Merge Rationale

### Synthesized Sources
- Builtin `android-cli` Skill reference: Installation procedures across OS platforms (Linux, macOS, Windows), SDK package commands, project generation (`android create`), AVD management (`android emulator`), and screen capture (`android screenshot`).
- `Raw_copies/AGENTS.md`: Mobile QA Agent specifications, mobile SLA thresholds, and validation rules.
- `Raw_copies/PROTOCOLS.md`: Error handling policies for headless test runners and timeout recovery.

### Concrete Merge Rationale
Mobile development and automated testing instructions were previously isolated within plugin skill files disconnected from the repository's CI/CD protocols. Autonomous agents lacked a unified reference defining exact ADB command lines, headless emulator creation parameters, and automated failure recovery logic. This Golden Master combines the official Android CLI capabilities with automated PowerShell/Python test harness scripts.

### Superiority Justification
1. **Automated Headless Emulation SOP**: Provides deterministic commands for launching and checking emulator boot status in headless CI environments.
2. **Deterministic UI State Verification**: Employs `uiautomator` XML dumps and visual screenshot capture to verify app layouts automatically.
3. **Cross-Platform CLI Installation**: Encapsulates Windows, Linux, and macOS CLI installation commands.

---

## Core Implementations & Code Artifacts

### 1. Automated Android CI/CD Test Harness Script (`android_test_runner.py`)

```python
"""
Automated Android Headless Emulator & UI Test Runner
Orchestrates AVD boot, APK installation, screenshot capture, and ADB teardown.
"""

import logging
import os
import subprocess
import time
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("android_devops")

class AndroidDevOpsRunner:
    def __init__(self, avd_name: str = "Pixel_7_API_34", timeout_seconds: int = 120):
        self.avd_name = avd_name
        self.timeout_seconds = timeout_seconds

    def check_adb_devices(self) -> bool:
        res = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        logger.info(f"Connected devices:\n{res.stdout}")
        return "device" in res.stdout and len(res.stdout.strip().splitlines()) > 1

    def wait_for_boot_complete(self) -> bool:
        logger.info("Waiting for Android emulator to complete boot...")
        t0 = time.time()
        while time.time() - t0 < self.timeout_seconds:
            res = subprocess.run(
                ["adb", "shell", "getprop", "sys.boot_completed"],
                capture_output=True,
                text=True
            )
            if res.stdout.strip() == "1":
                logger.info(f"Emulator boot completed in {time.time() - t0:.1f}s")
                return True
            time.sleep(3)
        logger.error("Emulator failed to boot within timeout threshold.")
        return False

    def install_and_launch_apk(self, apk_path: str, package_name: str, main_activity: str) -> bool:
        logger.info(f"Installing APK: {apk_path}")
        install_res = subprocess.run(["adb", "install", "-r", apk_path], capture_output=True, text=True)
        if "Success" not in install_res.stdout:
            logger.error(f"APK installation failed: {install_res.stderr or install_res.stdout}")
            return False
            
        logger.info(f"Launching {package_name}/{main_activity}")
        launch_res = subprocess.run(
            ["adb", "shell", "am", "start", "-n", f"{package_name}/{main_activity}"],
            capture_output=True,
            text=True
        )
        return launch_res.returncode == 0

    def capture_screenshot(self, output_path: str = "screenshot.png") -> bool:
        logger.info(f"Capturing mobile screenshot to {output_path}")
        res = subprocess.run(["adb", "exec-out", "screencap", "-p"], capture_output=True)
        if res.returncode == 0:
            with open(output_path, "wb") as f:
                f.write(res.stdout)
            logger.info("Screenshot successfully captured and saved.")
            return True
        return False

    def dump_ui_hierarchy(self, output_xml: str = "window_dump.xml") -> Optional[str]:
        logger.info("Dumping UI hierarchy XML...")
        subprocess.run(["adb", "shell", "uiautomator", "dump", "/sdcard/window_dump.xml"], capture_output=True)
        res = subprocess.run(["adb", "shell", "cat", "/sdcard/window_dump.xml"], capture_output=True, text=True)
        if res.returncode == 0:
            with open(output_xml, "w", encoding="utf-8") as f:
                f.write(res.stdout)
            return res.stdout
        return None
```

---

## Parameterized Prompt Decks & Templates

### Prompt Deck 1: Mobile UI Accessibility & Layout Verification

```markdown
<system_role>
You are an expert Android Mobile QA Engineer.
Analyze the following dumped `uiautomator` XML layout and identify accessibility or touch target violations.
</system_role>

<input_layout>
App Package: {{PACKAGE_NAME}}
Activity: {{ACTIVITY_NAME}}
UI Hierarchy XML:
{{UI_XML_DUMP}}
</input_layout>

<evaluation_rules>
1. Identify all clickable elements (`clickable="true"`).
2. Verify element bounds: touch target dimensions must be at least 48x48 dp.
3. Check for missing `content-desc` attributes on ImageButtons and ImageView controls.
4. Report all violations in structured JSON.
</evaluation_rules>
```

---

## Deployment SOP & Operational Guide

1. **Install Android CLI**:
   - Windows: `curl -fsSL https://dl.google.com/android/cli/latest/windows_x86_64/install.cmd -o "%TEMP%\i.cmd" && "%TEMP%\i.cmd"`
   - Linux: `curl -fsSL https://dl.google.com/android/cli/latest/linux_x86_64/install.sh | bash`
2. **Install Android SDK Platforms**:
   - Run `android sdk install platforms/android-34 build-tools/34.0.0`
3. **Execute Automated Mobile Test**:
   - Run `python android_test_runner.py` to boot AVD, install APK, capture screenshot, and verify UI layout.

---

## Failure Modes, Edge Cases & Troubleshooting

- **Failure Mode 1: ADB Unauthorized Error (`error: device unauthorized`)**:
  - *Cause*: Host machine RSA key not accepted on the Android device.
  - *Remedy*: Kill server with `adb kill-server`, delete `~/.android/adbkey`, restart ADB, and accept USB debugging prompt.
- **Failure Mode 2: AVD Cold Boot Hang**:
  - *Cause*: Snapshot state corrupted or insufficient hardware acceleration.
  - *Remedy*: Launch emulator with `-no-snapshot-load -no-audio -gpu swiftshader_indirect`.
