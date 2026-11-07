# MuCpp 🚀

<div align="center">

![MuCpp Logo](assets/icons/app_logo.svg)

### **A Fast, Modern, and Lightweight C/C++ Integrated Development Environment**

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![GUI Framework](https://img.shields.io/badge/GUI-PySide6%20%2F%20Qt-41CD52?logo=qt&logoColor=white)](https://wiki.qt.io/Qt_for_Python)
[![Compiler](https://img.shields.io/badge/Compiler-MinGW--w64%20GCC%2FG%2B%2B-00599C?logo=c%2B%2B&logoColor=white)](https://www.mingw-w64.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

*Combining the simplicity and legendary speed of classic C/C++ IDEs with a sleek, modern vector interface, background compiler threads, and direct error navigation.*

---

</div>

## 🌟 Overview

**MuCpp** is a clean, responsive desktop C/C++ IDE built with **Python** and **PySide6 (Qt)**. It is engineered for students, educators, competitive programmers, and developers who desire the instant startup time and straightforward workflow of tools like Dev-C++, enhanced with modern UI design, crisp vector SVG toolbars, non-blocking compilation workers, and interactive diagnostic navigation.

---

## ✨ Features

- **⚡ Instant Build & Execution**:
  - Non-blocking asynchronous compilation via `QThread` workers (your UI never freezes).
  - Familiar single-key execution pipeline: **F9** (Compile), **F10** (Run), **F11** (Compile & Run), and **F12** (Rebuild All).
  - Support for launching executables directly in an external Windows console window with automatic pause upon exit.

- **🎨 Modern Vector UI & Toolbar**:
  - High-DPI crisp vector icons (SVG) with modern styling.
  - Context menu to switch between **Icons Only**, **Text Beside Icons**, **Text Under Icons**, or **Text Only** on demand.
  - Native Windows / Fusion styling with smooth hover states and tab controls.

- **🔍 Interactive Diagnostics & Issue Tracking**:
  - Automatically parses GCC/G++ output into structured error and warning lists.
  - **Double-click any diagnostic line** to automatically jump directly to the exact file, line, and column in the code editor.

- **📝 High-Performance Code Editor**:
  - Real-time C/C++ syntax highlighting (keywords, types, preprocessors, strings, comments, numbers).
  - Left gutter with line numbers and active line highlighting.
  - Automatic indentation, smart bracket matching, and multi-tab document management.

- **📁 Project Management & Templates**:
  - Support for standalone single-source files (`.cpp`, `.c`) as well as full multi-file projects (`.mcpp`).
  - Pre-built project templates:
    - 📟 **Console Application**
    - 🪟 **Win32 GUI Application**
    - 📦 **Static Library (`.a` / `.lib`)**
    - 🔗 **Dynamic Link Library (DLL)**

- **⚙️ Configurable Toolchain Settings**:
  - Automatic detection of local MinGW64 `g++.exe` and `gcc.exe`.
  - GUI configuration for language standards (`C++11`, `C++14`, `C++17`, `C++20`), optimization levels (`-O0` to `-O3`, `-Ofast`), warning flags (`-Wall`, `-Wextra`), and custom linker flags.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action | Description |
|:---|:---|:---|
| <kbd>F9</kbd> | **Compile** | Compiles current file or active project in background |
| <kbd>F10</kbd> | **Run** | Executes the compiled binary in an interactive console |
| <kbd>F11</kbd> | **Compile & Run** | Builds and immediately launches upon successful compilation |
| <kbd>F12</kbd> | **Rebuild All** | Cleans old binary and triggers a fresh compilation |
| <kbd>Ctrl</kbd> + <kbd>N</kbd> | **New Source File** | Opens a new code editor tab with initial C++ template |
| <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>N</kbd> | **New Project** | Opens project wizard to choose from templates |
| <kbd>Ctrl</kbd> + <kbd>O</kbd> | **Open File** | Opens existing C/C++ source code |
| <kbd>Ctrl</kbd> + <kbd>S</kbd> | **Save** | Saves the active document |
| <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>S</kbd> | **Save All** | Saves all currently open modified tabs |
| <kbd>Ctrl</kbd> + <kbd>W</kbd> | **Close Tab** | Closes active tab (prompts if unsaved changes exist) |
| <kbd>Ctrl</kbd> + <kbd>F</kbd> | **Find / Replace** | Opens search and text replacement dialog |
| <kbd>Ctrl</kbd> + <kbd>G</kbd> | **Go to Line** | Jump directly to a specific line number |

---

## 🚀 Getting Started

### Prerequisites

1. **Python 3.10+**: Download and install from [python.org](https://www.python.org/).
2. **MinGW-w64 GCC/G++**: A working C/C++ compiler toolchain (e.g., via WinLibs, MSYS2, or standalone MinGW64).
   - Ensure `g++.exe` or `gcc.exe` is either on your system `PATH` or located in default paths like `C:\Program Files (x86)\Dev-Cpp\MinGW64\bin\`.
   - You can also configure the custom compiler paths anytime inside the IDE via **Execute ➔ Compiler Options**.

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/MuCpp.git
   cd MuCpp
   ```

2. **Create a virtual environment (optional but recommended)**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch MuCpp**:
   ```bash
   python main.py
   ```

---

## 📂 Project Structure

```text
MuCpp/
├── assets/
│   └── icons/                 # Crisp modern vector SVG icons
│       ├── app_logo.svg       # MuCpp Application Brand Logo
│       ├── compile.svg        # Compile (F9) gear icon
│       ├── run.svg            # Run (F10) emerald play icon
│       ├── compile_run.svg    # Compile & Run (F11) combo icon
│       ├── rebuild.svg        # Rebuild All (F12) cycle icon
│       ├── new_file.svg       # New Source File
│       ├── new_project.svg    # New Project
│       ├── open_file.svg      # Open File
│       ├── save.svg           # Save Current File
│       ├── save_all.svg       # Save All Open Files
│       ├── find.svg           # Search & Replace
│       ├── settings.svg       # Compiler & Toolchain Options
│       └── ...                # Undo, Redo, Cut, Copy, Paste, etc.
├── compiler.py                # GCC/G++ detection, runner, & diagnostic parser
├── dialogs.py                 # New Project, Compiler Options, Find/Replace dialogs
├── editor.py                  # CodeEditor with syntax highlighter & line number gutter
├── icons.py                   # High-DPI icon cache & loader
├── ide.py                     # Main IDE window, menus, toolbars, & worker thread
├── main.py                    # Application entry point & modern theme definitions
├── project.py                 # Project file (.mcpp) model and starter templates
├── requirements.txt           # Python package requirements
└── README.md                  # Project documentation
```

---

## 🛠️ Configuration

Inside MuCpp, navigate to **Execute ➔ Compiler Options** to configure:

- **C++ Compiler (`g++.exe`) & C Compiler (`gcc.exe`)**: Specify custom binary paths if not in `PATH`.
- **Language Standard**: Choose between `C++98`, `C++11`, `C++14`, `C++17`, or `C++20`.
- **Optimization Level**: Select `-O0` (Debug), `-O1`, `-O2` (Recommended), `-O3` (Max speed), `-Os` (Size), or `-Ofast`.
- **Diagnostics & Warnings**: Toggle `-Wall` and `-Wextra`, or add arbitrary custom compiler/linker flags.
- **Execution Mode**: Toggle launching in an external interactive Windows console with auto-pause.

---

## 🤝 Contributing

Contributions, bug reports, and feature requests are very welcome!

1. Fork the Project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the Branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.
