# -*- coding: utf-8 -*-
"""
Created on Mon Jan 19 14:51:00 2026

@author: engcicek
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
import skrf as rf
import csv
import os

class LMBA_Pro_App:
    def __init__(self, root):
        self.root = root
        self.root.title("Pre-design Center of Load Modulated Balanced Amplifier")
        self.root.geometry("1200x800")
        
        # --- Ayarlar ---
        self.Z0 = 50
        self.csv_file = "lmba_tasarim_sonuclari.csv"
        large_font = ('Verdana', 12, 'bold') 
        entry_font = ('Verdana', 11)

        # --- Layout ---
        self.stil = ttk.Style()
        self.stil.configure("TLabelframe.Label", font=("Verdana", 12, "bold"))
        self.main_frame = ttk.Frame(self.root, padding=10, style="TLabelframe.Label")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        

        # --- Sol Panel ---
        input_frame = ttk.LabelFrame(self.main_frame, text="Parametreler", padding=10)
        input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        self.entries = {}
        fields = [
            ("Zopt_R", 15.0, "Z_opt Real (Ω)"),
            ("Zopt_I", 30.0, "Z_opt İmaginary (jΩ)"),
            ("Ztarget_R", 45.0, "Z_target Real (Ω)"),
            ("Ztarget_I", 10.0, "Z_target İmaginary (jΩ)"),
            ("P_CA", 37.0, "Power Limit of Control Amp (dBm)"),
            ("P_DUT", 40.0, "Main DUT Power (dBm)"),
            ("C_Loss", 0.7, "Coupler Loss (dB)")
        ]
        
        for key, val, label in fields:
            ttk.Label(input_frame, text=label, font=large_font).pack(anchor=tk.W)
            ent = ttk.Entry(input_frame,font=entry_font)
            ent.insert(0, str(val))
            ent.pack(fill=tk.X, pady=2)
            self.entries[key] = ent

        style = ttk.Style()
        style.configure('ttk.TButton', font=('Verdana', 14, 'bold'))
        ttk.Button(input_frame, text="Evaluate and Save" , command=self.process, style='ttk.TButton').pack(pady=15,ipady=5, fill=tk.X)

        # LED ve Durum
        self.status_canvas = tk.Canvas(input_frame, width=200, height=80, bg="#f0f0f0")
        self.status_canvas.pack(pady=5)
        self.led = self.status_canvas.create_oval(85, 5, 115, 35, fill="gray")
        self.status_text = self.status_canvas.create_text(100, 55, text="Waiting", font=("Verdana", 12, "bold"))

        self.res_label = ttk.Label(input_frame, text="", font=("Verdana", 12))
        self.res_label.pack(pady=10, fill=tk.BOTH)

        # --- Sağ Panel (Grafik) ---
        self.fig, self.ax = plt.subplots(figsize=(7, 7),dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.process() # İlk açılış çizimi
        # --- İmza Bölümü ---
        self.imza_label = tk.Label(
            input_frame, 
            text="Developed by Engin Can Cicek", 
            font=('Segoe UI', 12, 'italic'), 
            fg="#555555",
            bg="white" # Resmin üzerine gelirse okunması için
        )
        self.imza_label.place(relx=1, rely=1, anchor="se", x=-10, y=-10)

    def save_data(self, data):
        file_exists = os.path.isfile(self.csv_file)
        with open(self.csv_file, mode='a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)

    def process(self):
        try:
            # Verileri Çek
            zo = complex(float(self.entries["Zopt_R"].get()), float(self.entries["Zopt_I"].get()))
            zt = complex(float(self.entries["Ztarget_R"].get()), float(self.entries["Ztarget_I"].get()))
            pdut = float(self.entries["P_DUT"].get())
            loss = float(self.entries["C_Loss"].get())
            pmax_ca = float(self.entries["P_CA"].get()) 

            # Hesapla
            inj = (zo / zt) - 1
            beta = np.abs(inj)
            theta = np.angle(inj, deg=True)
            p_ca = 10 * np.log10(max(10**(pdut/10) * (beta**2), 1e-10)) + loss +3  # dBm
            safe = p_ca <= pmax_ca

            # LED Güncelle
            color = "lime" if safe else "red"
            msg = "SAFE" if safe else "DANGER"
            self.status_canvas.itemconfig(self.led, fill=color)
            self.status_canvas.itemconfig(self.status_text, text=msg, fill="red" if not safe else "green")

            # CSV Kaydet
            self.save_data({
                "Z_opt": zo, "Z_target": zt, "Beta": round(beta,3), 
                "Phase": round(theta,2), "CA_dBm": round(p_ca,2), "Status": msg
            })

            # Metin ve Grafik
            self.res_label.config(text=f"Beta_Injection_Ratio: {beta:.3f}\nPhase : {theta:.2f}°\nCA_Power  : {p_ca:.1f} dBm")
            

            self.ax.clear()

            # 1. TEMEL SMITH CHART ÇİZİMİ
            # draw_labels=True otomatik olarak ana değerleri (0.2, 0.5, 1.0 vb.) yazar.
            rf.plotting.smith(ax=self.ax, chart_type='z', draw_labels=True)

            # 2. DENSE GRID: R ve X ARALIKLARINI DOLDURMA
            # Yoğunluk miktarını buradan ayarlayabilirsin (0.1 adımlarla)
            dense_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.5, 2.0, 3.0, 5.0]

            for v in dense_values:
                # --- SABİT DİRENÇ HALKALARI (R) ---
                theta2 = np.linspace(0, 2*np.pi, 100)
                r_center = v / (v + 1)
                r_radius = 1 / (v + 1)
                xr = r_center + r_radius * np.cos(theta2)
                yr = r_radius * np.sin(theta2)
                self.ax.plot(xr, yr, color='black', linestyle='-', linewidth=1, alpha=0.3)

                # --- SABİT REAKTANS YAYLARI (X) ---
                # Üst (+) ve Alt (-) reaktans yayları
                phi = np.linspace(0, 2*np.pi, 100) # Yayın açısı
                x_center = 1.0
                x_y_center = 1.0 / v
                x_radius = 1.0 / v
                
                # Pozitif Reaktans (Endüktif - Üst Yarım)
                xx_p = x_center + x_radius * np.cos(phi)
                yy_p = x_y_center + x_radius * np.sin(phi)
                # Sadece Smith Chart dairesi içinde kalanları çiz
                mask = xx_p**2 + yy_p**2 <= 5
                self.ax.plot(xx_p[mask], yy_p[mask], color='gray', linestyle=':', linewidth=1, alpha=0.5)
                
                # Negatif Reaktans (Kapasitif - Alt Yarım)
                yy_n = -x_y_center + x_radius * np.sin(phi)
                mask_n = xx_p**2 + yy_n**2 <= 5
                self.ax.plot(xx_p[mask_n], yy_n[mask_n], color='gray', linestyle=':', linewidth=1, alpha=0.5)

            # ... (Yörünge ve nokta plotlama kısımları aynı) ...

            betas = np.linspace(0, beta, 100)
            gamma_traj = (zt*(1+betas*np.exp(1j*np.deg2rad(theta))) - self.Z0) / (zt*(1+betas*np.exp(1j*np.deg2rad(theta))) + self.Z0)
            self.ax.plot(np.real(gamma_traj), np.imag(gamma_traj), 'b-', lw=2, label="Trajectory")
            
            # Zopt ve Ztarget noktaları
            g_opt = (zo - self.Z0)/(zo + self.Z0)
            g_target = (zt - self.Z0)/(zt + self.Z0)
            self.ax.plot(np.real(g_opt), np.imag(g_opt), 'go', label="Z_opt")
            self.ax.plot(np.real(g_target), np.imag(g_target), 'rx', ms=10, label="Z_target")
            
            self.ax.legend()
            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Hata", f"Değerleri kontrol edin: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LMBA_Pro_App(root)
    root.mainloop()
