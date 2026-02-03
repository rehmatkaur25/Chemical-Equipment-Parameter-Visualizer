# Chemical Equipment Parameter Visualizer(Hybrid Web + Destop App)

A robust monitoring solution featuring a **PyQt5 Desktop Application**, **Django REST API**, and a **React Web Dashboard**. This system provides real-time analytics and safety monitoring for industrial chemical equipment.

### 🌟 Key Features

* **Hybrid Architecture**: Seamless data interaction across Desktop, Web, and Backend platforms.
* **Persistent Desktop History**: Uses **SQLite** to store and display the last 5 uploaded datasets locally.
* **Safety Threshold Alerts**: Automatic red-highl Desktop App)ighting and bold alerts for equipment exceeding **115°C** (e.g., Reactor-1 at 140°C).
* **Dynamic Visualizations**: High-fidelity **Matplotlib** charts (Distribution and Proportions) with a professional pure black theme.
* **Report Generation**: Integrated feature to generate summarized text/PDF reports of equipment analysis.

---

### 🛠️ Tech Stack

* **Desktop**: Python, PyQt5, Pandas, Matplotlib
* **Backend**: Django, SQLite3, REST Framework
* **Frontend**: React.js, Tailwind CSS

---

## ⚙️ Setup & Installation

### 1. Backend (Django)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```



###  2. Desktop Application (PyQt5)

```bash

 cd desktop-app
 pip install pyqt5 pandas matplotlib
 python3 main.py
```


 ### 3. Web Frontend (React)
 
```bash 
  cd web-frontend
  npm install
  npm start
```

---

### 📋 Usage Instructions

* **Centered Landing Page**: Launch the desktop application to find the "Chemical Analytics Dashboard" title and "Choose CSV" button perfectly centered on your screen.

* **Analyze Equipment Data**: Click **"Choose CSV and Analyze Data"** to upload your chemical dataset and trigger the automated visualization suite.

* **Real-Time Safety Monitoring**: Review the **Detailed Equipment Log**; hazardous temperatures exceeding **115°C** (e.g., Reactor-1 at 140°C) are automatically highlighted in bold red.

* **Persistent History Tracking**: The sidebar manages the **last 5 datasets** using a local **SQLite** database, allowing you to switch between recent reports instantly.

* **Export Summary Reports**: Use the **"Generate PDF Report"** button to export a summarized text analysis of your current findings.

---

### 🎓 Academic Context

* **Developer**: Rehmat Kaur

* **Institution**: VIT Bhopal University

* **Project Purpose**: Technical Portfolio for FOSSEE Internship Application.

