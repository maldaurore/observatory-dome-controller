# Project Installation

This document describes how to install the Observatory Dome Controller software.

## Clone the Repository

Open a terminal and clone the project repository:

```bash
git clone https://github.com/maldaurore/observatory-dome-controller.git
```

Enter the project directory:

```bash
cd observatory-dome-controller
```

---

## Install the Alpaca Server

Navigate to the server directory:

```bash
cd alpaca-server
```

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment.

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Deactivate the virtual environment when finished:

```bash
deactivate
```

---

## Install the Graphical User Interface

Return to the project root:

```bash
cd ..
```

Navigate to the GUI directory:

```bash
cd gui
```

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment.

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Deactivate the virtual environment when finished:

```bash
deactivate
```

---

## Next Step

Continue with **05-first-startup.md**.