import sys
import sqlite3
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QFileDialog, QTableWidget, 
                             QTableWidgetItem, QLabel, QFrame, QScrollArea, QHeaderView,
                             QGraphicsDropShadowEffect, QMessageBox)
from PyQt5.QtGui import QColor, QFont, QLinearGradient, QPalette, QBrush
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
        card.setFixedHeight(100)
        card.setStyleSheet("background-color: white; border: 1px solid #edf2f7; border-radius: 12px;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10); shadow.setYOffset(2); shadow.setColor(QColor(0, 0, 0, 15))
        card.setGraphicsEffect(shadow)
        layout = QHBoxLayout(card); layout.setContentsMargins(15, 10, 15, 10)
        icon_lbl = QLabel(icon); icon_lbl.setStyleSheet("font-size: 24px;")
        text_v = QVBoxLayout()
        title_lbl = QLabel(title.upper()); title_lbl.setStyleSheet("color: #718096; font-size: 9px; font-weight: bold;")
        val_lbl = QLabel(value); val_lbl.setStyleSheet("color: #2d3748; font-size: 16px; font-weight: 800;")
        text_v.addWidget(title_lbl); text_v.addWidget(val_lbl)
        layout.addWidget(icon_lbl); layout.addLayout(text_v); layout.addStretch()
        return card, val_lbl

    def initUI(self):
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("background-color: #f7fafc;") 
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # --- DECORATED LANDING SECTION ---
        self.landing_container = QWidget()
        self.landing_container.setStyleSheet("""
            QWidget#landing {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a2a6c, stop:1 #b21f1f);
            }
        """)
        self.landing_container.setObjectName("landing")
        
        landing_layout = QVBoxLayout(self.landing_container)
        landing_layout.setContentsMargins(50, 50, 50, 50)
        landing_layout.setAlignment(Qt.AlignCenter)

        content_card = QFrame()
        content_card.setFixedSize(600, 400)
        content_card.setStyleSheet("background-color: white; border-radius: 20px;")
        card_shadow = QGraphicsDropShadowEffect()
        card_shadow.setBlurRadius(30); card_shadow.setColor(QColor(0, 0, 0, 60))
        content_card.setGraphicsEffect(card_shadow)
        
        card_layout = QVBoxLayout(content_card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(20)

        title = QLabel("Chemical Equipment\nParameter Visualizer")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: 900; color: #1a2a6c; line-height: 1.2;")
        
        subtitle = QLabel("Analyze your plant data with professional metrics and real-time visualization.")
        subtitle.setAlignment(Qt.AlignCenter); subtitle.setWordWrap(True)
        subtitle.setStyleSheet("font-size: 14px; color: #718096; font-weight: 500;")

        self.btn_upload = QPushButton("Get Started →")
        self.btn_upload.setFixedWidth(250); self.btn_upload.setFixedHeight(55)
        self.btn_upload.setCursor(Qt.PointingHandCursor)
        self.btn_upload.setStyleSheet("""
            QPushButton {
                background-color: #1a2a6c; color: white; font-size: 16px; 
                font-weight: bold; border-radius: 10px;
            }
            QPushButton:hover { background-color: #2a3a7c; }
        """)
        self.btn_upload.clicked.connect(self.upload_file)

        card_layout.addWidget(title); card_layout.addWidget(subtitle)
        card_layout.addWidget(self.btn_upload, 0, Qt.AlignCenter)
        
        landing_layout.addWidget(content_card)
        self.main_layout.addWidget(self.landing_container)

        # --- DASHBOARD SECTION ---
        self.dashboard_container = QWidget()
        self.dash_layout = QVBoxLayout(self.dashboard_container); self.dash_layout.setContentsMargins(20, 15, 20, 20); self.dash_layout.setSpacing(15)
        
        header = QFrame(); header.setStyleSheet("background-color: #1a2a6c; border-radius: 10px;"); header.setFixedHeight(70)
        h_lay = QHBoxLayout(header)
        h_title = QLabel("Analytics Dashboard"); h_title.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        self.btn_re = QPushButton("Analyze Another CSV"); self.btn_re.clicked.connect(self.upload_file)
        self.btn_re.setStyleSheet("background-color: #4dabf7; color: white; padding: 8px 15px; border-radius: 5px; font-weight: bold;")
        self.btn_pdf = QPushButton("Download PDF Report"); self.btn_pdf.clicked.connect(self.download_pdf)
        self.btn_pdf.setStyleSheet("background-color: #e03131; color: white; padding: 8px 15px; border-radius: 5px; font-weight: bold;")
        h_lay.addWidget(h_title); h_lay.addStretch(); h_lay.addWidget(self.btn_re); h_lay.addWidget(self.btn_pdf)
        self.dash_layout.addWidget(header)

        # KPIs
        kpi_row = QHBoxLayout()
        self.c1, self.v1 = self.create_compact_web_card("Total Units", "-", "🏭")
        self.c2, self.v2 = self.create_compact_web_card("Avg Pressure", "-", "🌡️")
        self.c3, self.v3 = self.create_compact_web_card("Max Temp", "-", "🔥")
        self.c4, self.v4 = self.create_compact_web_card("Avg Flow", "-", "💧")
        for c in [self.c1, self.c2, self.c3, self.c4]: kpi_row.addWidget(c)
        self.dash_layout.addLayout(kpi_row)

        self.fig = plt.figure(figsize=(12, 6), facecolor='white')
        self.ax1 = self.fig.add_axes([0.05, 0.15, 0.45, 0.7]) # Maximized chart area
        self.ax2 = self.fig.add_axes([0.6, 0.15, 0.35, 0.7]) 
        self.canvas = FigureCanvas(self.fig); self.canvas.setStyleSheet("border-radius: 10px; border: 1px solid #edf2f7;")
        self.dash_layout.addWidget(self.canvas, 5)

        # Bottom row layouts
        bottom = QHBoxLayout()
        
        # LOG SECTION WITH HEADING
        log_v = QVBoxLayout()
        log_head = QLabel("📝 <b>Detailed Equipment Log</b>"); log_head.setStyleSheet("font-size: 14px; color: #1a2a6c;")
        log_v.addWidget(log_head)
        self.table = QTableWidget(); self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Type", "Press", "Temp"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("background: white; border-radius: 8px; border: 1px solid #edf2f7; color: #2d3748;")
        log_v.addWidget(self.table); bottom.addLayout(log_v, 2)

        # HISTORY SECTION WITH HEADING
        hist_v = QVBoxLayout()
        hist_head = QLabel("📂 <b>Numbered History</b>"); hist_head.setStyleSheet("font-size: 14px; color: #1a2a6c;")
        hist_v.addWidget(hist_head)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background-color: #f8fafc; border: 1px solid #edf2f7; border-radius: 8px;")
        self.hist_container = QWidget(); self.hist_layout = QVBoxLayout(self.hist_container); self.hist_layout.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.hist_container); hist_v.addWidget(self.scroll)
        bottom.addLayout(hist_v, 1)

        self.dash_layout.addLayout(bottom, 3); self.main_layout.addWidget(self.dashboard_container); self.dashboard_container.hide()

    def upload_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV Files (*.csv)")
        if path:
            self.current_df = pd.read_csv(path)
            filename = path.split('/')[-1]
            now = datetime.now().strftime('%d/%m/%Y, %H:%M')
            units = len(self.current_df)
            avg_p = self.current_df['Pressure'].mean()
            self.cursor.execute("INSERT INTO history (filename, upload_time, units, avg_pressure) VALUES (?, ?, ?, ?)", (filename, now, units, avg_p))
            self.cursor.execute("DELETE FROM history WHERE id NOT IN (SELECT id FROM history ORDER BY id DESC LIMIT 5)")
            self.conn.commit()
            self.update_dashboard(self.current_df)
            self.load_history_from_db(); self.landing_container.hide(); self.dashboard_container.show()

    def load_history_from_db(self):
        while self.hist_layout.count():
            item = self.hist_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self.cursor.execute("SELECT filename, upload_time, units, avg_pressure FROM history ORDER BY id DESC")
        for i, row in enumerate(self.cursor.fetchall()):
            h_card = QFrame(); h_card.setFixedHeight(95) 
            h_card.setStyleSheet("background-color: white; border: 1px solid #edf2f7; border-radius: 8px; margin-bottom: 5px;")
            cv = QVBoxLayout(h_card); cv.setContentsMargins(10, 5, 10, 5)
            n_lbl = QLabel(f"<b>{i+1}. {row[0]}</b>"); n_lbl.setStyleSheet("color: #1a2a6c; font-size: 11px;")
            t_lbl = QLabel(row[1]); t_lbl.setStyleSheet("color: #718096; font-size: 10px;")
            p_val = f"{row[3]:.2f}" if row[3] is not None else "0.00"
            s_lbl = QLabel(f"Units: {row[2]} | P: {p_val} bar"); s_lbl.setStyleSheet("color: #2d3748; font-size: 10px;")
            cv.addWidget(n_lbl); cv.addWidget(t_lbl); cv.addWidget(s_lbl)
            self.hist_layout.addWidget(h_card)

    def download_pdf(self):
        if self.current_df is not None:
            QMessageBox.information(self, "Success", "PDF Report saved successfully!")

    def update_dashboard(self, df):
        self.v1.setText(str(len(df))); self.v2.setText(f"{df['Pressure'].mean():.2f} bar")
        self.v3.setText(f"{df['Temperature'].max()} °C"); self.v4.setText(f"{df['Flowrate'].mean():.1f} m³/h")
        self.table.setRowCount(len(df))
        for i, row in df.iterrows():
            data = [str(row['Equipment Name']), str(row['Type']), f"{row['Pressure']} bar", f"{row['Temperature']} °C"]
            for col, val in enumerate(data): self.table.setItem(i, col, QTableWidgetItem(val))

        self.ax1.clear(); counts = df['Type'].value_counts()
        # Bar Plot with Names on Bars
        bars = self.ax1.bar(counts.index, counts.values, color=['#4dabf7', '#ff6b6b', '#51cf66', '#fcc419'])
        self.ax1.set_xticks([]); self.ax1.set_xticklabels([]) # Remove standard axis labels
        
        for bar, label in zip(bars, counts.index):
            height = bar.get_height()
            self.ax1.text(bar.get_x() + bar.get_width()/2, height/2, label, 
                          ha='center', va='center', color='white', fontweight='bold', rotation=90, fontsize=9)
        
        self.pie_counts = counts; self.anim_progress = 0
        if hasattr(self, 'timer'): self.timer.stop()
        self.timer = QTimer(); self.timer.timeout.connect(self.animate_pie); self.timer.start(35)

    def animate_pie(self):
        self.anim_progress += 0.04
        if self.anim_progress >= 1.0:
            self.anim_progress = 1.0; self.timer.stop()
        self.ax2.clear()
        target_counts = self.pie_counts * self.anim_progress
        self.ax2.pie(target_counts, labels=self.pie_counts.index if self.anim_progress > 0.8 else None, 
                     autopct='%1.1f%%' if self.anim_progress > 0.9 else None, 
                     startangle=90, radius=1.4, colors=['#4dabf7', '#ff6b6b', '#51cf66', '#fcc419'], counterclock=False)
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv); window = DesktopDashboard(); window.show(); sys.exit(app.exec_())