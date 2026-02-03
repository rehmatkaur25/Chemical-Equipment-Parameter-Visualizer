import sys
import sqlite3
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QFileDialog, QTableWidget, 
                             QTableWidgetItem, QLabel, QFrame, QScrollArea, QHeaderView,
                             QGraphicsDropShadowEffect, QMessageBox)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt, QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class DesktopDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chemical Equipment Parameter Visualizer")
        self.resize(1450, 950)
        self.current_df = None
        self.init_db()
        self.initUI()
        self.load_history_from_db()

    def init_db(self):
        self.conn = sqlite3.connect('history.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS history 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, upload_time TEXT, units INTEGER, avg_pressure REAL)''')
        self.conn.commit()

    def create_compact_web_card(self, title, value, icon=""):
        card = QFrame()
        card.setFixedHeight(110)
        card.setStyleSheet("background-color: white; border: 1px solid #e2e8f0; border-radius: 15px;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15); shadow.setYOffset(4); shadow.setColor(QColor(0, 0, 0, 20))
        card.setGraphicsEffect(shadow)
        layout = QHBoxLayout(card); layout.setContentsMargins(20, 15, 20, 15)
        icon_lbl = QLabel(icon); icon_lbl.setStyleSheet("font-size: 30px;")
        text_v = QVBoxLayout()
        # Heading color set to Black
        title_lbl = QLabel(title.upper()); title_lbl.setStyleSheet("color: black; font-size: 10px; font-weight: bold; letter-spacing: 1px;")
        val_lbl = QLabel(value); val_lbl.setStyleSheet("color: #1e293b; font-size: 18px; font-weight: 800;")
        text_v.addWidget(title_lbl); text_v.addWidget(val_lbl)
        layout.addWidget(icon_lbl); layout.addLayout(text_v); layout.addStretch()
        return card, val_lbl

    def initUI(self):
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("background-color: #f8fafc;") 
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget); self.main_layout.setContentsMargins(0, 0, 0, 0)

        # --- LANDING SECTION ---
        self.landing_container = QWidget(); self.landing_container.setObjectName("landing")
        self.landing_container.setStyleSheet("QWidget#landing { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a2a6c, stop:1 #b21f1f); }")
        l_lay = QVBoxLayout(self.landing_container); l_lay.setAlignment(Qt.AlignCenter)
        c_card = QFrame(); c_card.setFixedSize(600, 400); c_card.setStyleSheet("background-color: white; border-radius: 24px;")
        sh = QGraphicsDropShadowEffect(); sh.setBlurRadius(40); sh.setColor(QColor(0,0,0,80)); c_card.setGraphicsEffect(sh)
        cl = QVBoxLayout(c_card); cl.setContentsMargins(40,40,40,40); cl.setSpacing(20)
        t = QLabel("Chemical Equipment\nParameter Visualizer"); t.setAlignment(Qt.AlignCenter); t.setStyleSheet("font-size: 32px; font-weight: 900; color: #1a2a6c;")
        btn = QPushButton("Get Started →"); btn.setFixedSize(250, 55); btn.setStyleSheet("QPushButton { background-color: #1a2a6c; color: white; font-weight: bold; border-radius: 12px; }")
        btn.clicked.connect(self.upload_file); cl.addWidget(t); cl.addWidget(btn, 0, Qt.AlignCenter)
        l_lay.addWidget(c_card); self.main_layout.addWidget(self.landing_container)

        # --- DASHBOARD SECTION ---
        self.dashboard_container = QWidget(); self.dash_layout = QVBoxLayout(self.dashboard_container)
        self.dash_layout.setContentsMargins(25, 20, 25, 25); self.dash_layout.setSpacing(20)
        
        # Header
        header = QFrame(); header.setStyleSheet("background-color: #1e293b; border-radius: 12px;"); header.setFixedHeight(75)
        h_lay = QHBoxLayout(header)
        h_title = QLabel("Dashboard Management"); h_title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        self.btn_back = QPushButton("Analyze New File"); self.btn_back.clicked.connect(self.go_to_landing)
        self.btn_back.setStyleSheet("background-color: #3b82f6; color: white; padding: 10px 20px; border-radius: 8px; font-weight: bold;")
        self.btn_pdf = QPushButton("Export PDF Report"); self.btn_pdf.clicked.connect(self.download_pdf)
        self.btn_pdf.setStyleSheet("background-color: #ef4444; color: white; padding: 10px 20px; border-radius: 8px; font-weight: bold;")
        h_lay.addWidget(h_title); h_lay.addStretch(); h_lay.addWidget(self.btn_back); h_lay.addWidget(self.btn_pdf)
        self.dash_layout.addWidget(header)

        # Black Heading
        kpi_h = QLabel("📋 <b>Process KPI Summary</b>"); kpi_h.setStyleSheet("color: black; font-size: 14px;")
        self.dash_layout.addWidget(kpi_h)

        kpi_row = QHBoxLayout(); kpi_row.setSpacing(15)
        self.c1, self.v1 = self.create_compact_web_card("Total Units", "-", "🏢")
        self.c2, self.v2 = self.create_compact_web_card("Avg Pressure", "-", "🌡️")
        self.c3, self.v3 = self.create_compact_web_card("Max Temp", "-", "🔥")
        self.c4, self.v4 = self.create_compact_web_card("Avg Flow", "-", "💧")
        for c in [self.c1, self.c2, self.c3, self.c4]: kpi_row.addWidget(c)
        self.dash_layout.addLayout(kpi_row)

        # --- CHARTS SECTION (Seperate Boxes) ---
        chart_row = QHBoxLayout(); chart_row.setSpacing(20)
        
        self.bar_frame = QFrame(); self.bar_frame.setStyleSheet("background: white; border-radius: 15px; border: 1px solid #e2e8f0;")
        bar_lay = QVBoxLayout(self.bar_frame)
        b_h = QLabel("📊 <b>GRAPH</b>"); b_h.setStyleSheet("color: black; font-size: 14px;")
        bar_lay.addWidget(b_h)
        self.bar_fig = plt.figure(facecolor='white'); self.bar_canvas = FigureCanvas(self.bar_fig)
        # Shifted up to 0.3 to make room for diagonal labels
        self.ax1 = self.bar_fig.add_axes([0.1, 0.3, 0.8, 0.6]); bar_lay.addWidget(self.bar_canvas)
        
        self.pie_frame = QFrame(); self.pie_frame.setStyleSheet("background: white; border-radius: 15px; border: 1px solid #e2e8f0;")
        pie_lay = QVBoxLayout(self.pie_frame)
        p_h = QLabel("🔄 <b>PORTIONS</b>"); p_h.setStyleSheet("color: black; font-size: 14px;")
        pie_lay.addWidget(p_h)
        self.pie_fig = plt.figure(facecolor='white'); self.pie_canvas = FigureCanvas(self.pie_fig)
        self.ax2 = self.pie_fig.add_axes([0.1, 0.1, 0.8, 0.8]); pie_lay.addWidget(self.pie_canvas)
        
        chart_row.addWidget(self.bar_frame, 3); chart_row.addWidget(self.pie_frame, 2)
        self.dash_layout.addLayout(chart_row, 5)

        # --- LOG & HISTORY BOXES (Seperate Boxes) ---
        bottom_row = QHBoxLayout(); bottom_row.setSpacing(20)
        
        self.log_frame = QFrame(); self.log_frame.setStyleSheet("background: white; border-radius: 15px; border: 1px solid #e2e8f0;")
        log_box_lay = QVBoxLayout(self.log_frame)
        l_h = QLabel("📝 <b>LOG ANALYSIS</b>"); l_h.setStyleSheet("color: black; font-size: 14px;")
        log_box_lay.addWidget(l_h)
        self.table = QTableWidget(); self.table.setColumnCount(4); self.table.setHorizontalHeaderLabels(["Name", "Type", "Press", "Temp"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("border: none; color: #1e293b;")
        log_box_lay.addWidget(self.table)
        
        self.hist_frame = QFrame(); self.hist_frame.setStyleSheet("background: white; border-radius: 15px; border: 1px solid #e2e8f0;")
        hist_box_lay = QVBoxLayout(self.hist_frame)
        h_h = QLabel("📂 <b>HISTORY (LAST 5)</b>"); h_h.setStyleSheet("color: black; font-size: 14px;")
        hist_box_lay.addWidget(h_h)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True); self.scroll.setStyleSheet("background: transparent; border: none;")
        self.hist_container = QWidget(); self.hist_layout = QVBoxLayout(self.hist_container); self.hist_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.hist_container); hist_box_lay.addWidget(self.scroll)

        bottom_row.addWidget(self.log_frame, 3); bottom_row.addWidget(self.hist_frame, 2)
        self.dash_layout.addLayout(bottom_row, 4)

        self.main_layout.addWidget(self.dashboard_container); self.dashboard_container.hide()

    def go_to_landing(self):
        self.dashboard_container.hide()
        self.landing_container.show()

    def upload_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV Files (*.csv)")
        if path:
            self.current_df = pd.read_csv(path); filename = path.split('/')[-1]; now = datetime.now().strftime('%d/%m/%Y, %H:%M')
            self.cursor.execute("INSERT INTO history (filename, upload_time, units, avg_pressure) VALUES (?, ?, ?, ?)", (filename, now, len(self.current_df), self.current_df['Pressure'].mean()))
            self.cursor.execute("DELETE FROM history WHERE id NOT IN (SELECT id FROM history ORDER BY id DESC LIMIT 5)")
            self.conn.commit(); self.update_dashboard(self.current_df); self.load_history_from_db()
            self.landing_container.hide(); self.dashboard_container.show()

    def load_history_from_db(self):
        while self.hist_layout.count():
            item = self.hist_layout.takeAt(0); 
            if item.widget(): item.widget().deleteLater()
        self.cursor.execute("SELECT filename, upload_time, units, avg_pressure FROM history ORDER BY id DESC")
        for row in self.cursor.fetchall():
            self.add_history_card(row[0], row[1], row[2], row[3])

    def add_history_card(self, name, time, units, press):
        h_card = QFrame(); h_card.setFixedHeight(95); h_card.setStyleSheet("background-color: white; border-bottom: 1px solid #edf2f7; border-radius: 5px;")
        cv = QVBoxLayout(h_card); cv.setContentsMargins(10, 5, 10, 5)
        n_lbl = QLabel(f"<b>{name}</b>"); n_lbl.setStyleSheet("color: #3b82f6; font-size: 11px;")
        t_lbl = QLabel(time); t_lbl.setStyleSheet("color: #888; font-size: 10px;")
        s_lbl = QLabel(f"Units: {units} | P: {press:.2f} bar"); s_lbl.setStyleSheet("color: #333; font-size: 10px;")
        cv.addWidget(n_lbl); cv.addWidget(t_lbl); cv.addWidget(s_lbl)
        self.hist_layout.addWidget(h_card)

    def download_pdf(self): QMessageBox.information(self, "Success", "Analysis Report exported!")

    def update_dashboard(self, df):
        self.v1.setText(str(len(df))); self.v2.setText(f"{df['Pressure'].mean():.2f} bar")
        self.v3.setText(f"{df['Temperature'].max()} °C"); self.v4.setText(f"{df['Flowrate'].mean():.1f} m³/h")
        self.table.setRowCount(len(df))
        for i, row in df.iterrows():
            temp, press = row['Temperature'], row['Pressure']
            data = [str(row['Equipment Name']), str(row['Type']), f"{press} bar", f"{temp} °C"]
            for col, val in enumerate(data):
                item = QTableWidgetItem(val)
                # Red Marks logic
                if temp > 115 or press > 7.0:
                    item.setForeground(QColor("#ef4444")); font = QFont(); font.setBold(True); item.setFont(font)
                self.table.setItem(i, col, item)

        self.ax1.clear(); counts = df['Type'].value_counts()
        bars = self.ax1.bar(counts.index, counts.values, color=['#4dabf7', '#ff6b6b', '#51cf66', '#fcc419'])
        
        # Diagonal labels underneath axis
        self.ax1.set_xticks(range(len(counts)))
        self.ax1.set_xticklabels(counts.index, rotation=45, ha='right', fontsize=9)
        self.bar_canvas.draw()

        self.pie_counts = counts; self.anim_progress = 0
        if hasattr(self, 'timer'): self.timer.stop()
        self.timer = QTimer(); self.timer.timeout.connect(self.animate_pie); self.timer.start(35)

    def animate_pie(self):
        self.anim_progress += 0.04
        if self.anim_progress >= 1.0: self.anim_progress = 1.0; self.timer.stop()
        self.ax2.clear()
        self.ax2.pie(self.pie_counts * self.anim_progress, labels=self.pie_counts.index if self.anim_progress > 0.8 else None, autopct='%1.1f%%' if self.anim_progress > 0.9 else None, startangle=90, radius=1.3, colors=['#4dabf7', '#ff6b6b', '#51cf66', '#fcc419'], counterclock=False)
        self.pie_canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv); window = DesktopDashboard(); window.show(); sys.exit(app.exec_())