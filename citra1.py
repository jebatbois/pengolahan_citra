import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import os

class ImageEnhancementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PCD - Image Enhancement Tool")
        
        # --- PERUBAHAN 1: Jendela Aplikasi Jauh Lebih Besar ---
        # Format: "LebarxTinggi"
        self.root.geometry("1250x750") 
        self.root.config(padx=20, pady=20)

        self.cv_image = None
        self.processed_cv_image = None

        self.setup_ui()

    def setup_ui(self):
        # --- Frame Kontrol (Kiri) ---
        control_frame = tk.Frame(self.root, width=250)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

        tk.Label(control_frame, text="Menu Kontrol", font=("Arial", 14, "bold")).pack(pady=(0, 15))

        tk.Button(control_frame, text="1. Buka Gambar", command=self.load_image, width=25).pack(pady=5)

        tk.Label(control_frame, text="2. Pilih Mode:").pack(pady=(15, 5))
        
        self.mode_var = tk.StringVar()
        self.mode_var.set("Convolution")
        
        mode_frame = tk.Frame(control_frame)
        mode_frame.pack()
        tk.Radiobutton(mode_frame, text="Convolution", variable=self.mode_var, value="Convolution", command=self.update_options).pack(anchor="w")
        tk.Radiobutton(mode_frame, text="Histogram Spec", variable=self.mode_var, value="Histogram", command=self.update_options).pack(anchor="w")

        tk.Label(control_frame, text="3. Pilih Teknik:").pack(pady=(15, 5))
        self.technique_var = tk.StringVar()
        self.technique_dropdown = ttk.Combobox(control_frame, textvariable=self.technique_var, state="readonly", width=22)
        self.technique_dropdown.pack(pady=5)
        
        self.update_options()

        tk.Button(control_frame, text="4. Terapkan", command=self.apply_processing, width=25, bg="#4CAF50", fg="white").pack(pady=20)
        tk.Button(control_frame, text="5. Simpan Hasil", command=self.save_image, width=25).pack(pady=5)

        # --- Frame Tampilan Citra (Kanan) --- PERUBAHAN UTAMA DI SINI ---
        image_container_frame = tk.Frame(self.root)
        image_container_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # Memaksa pembagian ruang menggunakan sistem Grid (50% Kiri, 50% Kanan)
        image_container_frame.columnconfigure(0, weight=1)
        image_container_frame.columnconfigure(1, weight=1)
        image_container_frame.rowconfigure(0, weight=1)

        # Container untuk Citra Asli (Kolom 0)
        orig_frame = tk.Frame(image_container_frame)
        orig_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=10)
        tk.Label(orig_frame, text="Citra Asli", font=("Arial", 12, "bold")).pack(pady=(0, 10))
        self.lbl_original = tk.Label(orig_frame, bg="#e0e0e0") 
        self.lbl_original.pack(expand=True)

        # Container untuk Citra Hasil (Kolom 1)
        proc_frame = tk.Frame(image_container_frame)
        proc_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)
        tk.Label(proc_frame, text="Hasil Pemrosesan", font=("Arial", 12, "bold")).pack(pady=(0, 10))
        self.lbl_processed = tk.Label(proc_frame, bg="#e0e0e0")
        self.lbl_processed.pack(expand=True)

    def update_options(self):
        mode = self.mode_var.get()
        if mode == "Convolution":
            # Menggunakan istilah yang persis ada di PDF materi
            options = ["Box Filter (Smoothing)", "Median Filter", "Laplacian Filter", "High-boost Filter"]
        else:
            options = ["Global Equalization", "CLAHE (Adaptive)"]
        
        self.technique_dropdown['values'] = options
        self.technique_dropdown.current(0)

    def load_image(self):
        # Perbaikan filter file untuk Linux agar case-insensitive
        tipe_file = [
            ("Semua File Gambar", "*.png *.jpg *.jpeg *.bmp *.PNG *.JPG *.JPEG *.BMP"),
            ("PNG Files", "*.png *.PNG"),
            ("JPEG Files", "*.jpg *.jpeg *.JPG *.JPEG"),
            ("Semua File", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(title="Pilih Gambar", filetypes=tipe_file)
        
        if file_path:
            # Menggunakan OS path agar kompatibel dengan Linux
            file_path = os.path.abspath(file_path)
            self.cv_image = cv2.imread(file_path)
            
            if self.cv_image is not None:
                self.display_image(self.cv_image, self.lbl_original)
                self.lbl_processed.config(image='')
                self.processed_cv_image = None
            else:
                messagebox.showerror("Error", "Gagal membaca file gambar. Pastikan format file didukung!")

    def display_image(self, img, label_widget):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        
        # Mengatur batas maksimal gambar agar pas dengan pembagian grid 50:50
        max_preview_size = (450, 450) 
        img_pil.thumbnail(max_preview_size) 
        
        img_tk = ImageTk.PhotoImage(image=img_pil)
        label_widget.config(image=img_tk)
        label_widget.image = img_tk

    def apply_processing(self):
        if self.cv_image is None:
            messagebox.showwarning("Peringatan", "Harap buka gambar terlebih dahulu!")
            return

        mode = self.mode_var.get()
        technique = self.technique_var.get()

        if mode == "Convolution":
            kernel = None
            if technique == "Box Filter (Smoothing)":
                # KITA UBAH KE UKURAN 5x5 (dikalikan 1/25) AGAR BLUR LEBIH TERLIHAT
                kernel = np.ones((5, 5), np.float32) / 25.0
                
            elif technique == "Laplacian Filter":
                kernel = np.array([[ 0, -1,  0], 
                                   [-1,  4, -1], 
                                   [ 0, -1,  0]])
                
            elif technique == "High-boost Filter":
                kernel = np.array([[-1, -1, -1], 
                                   [-1,  8, -1], 
                                   [-1, -1, -1]])
                
            elif technique == "Median Filter":
                # KITA UBAH PARAMETERNYA MENJADI 5 (Matriks 5x5)
                # Syarat angka ini harus ganjil (3, 5, 7, 9, dst)
                self.processed_cv_image = cv2.medianBlur(self.cv_image, 5)

            if kernel is not None:
                self.processed_cv_image = cv2.filter2D(self.cv_image, -1, kernel)

        elif mode == "Histogram":
            # Convert BGR ke YUV untuk memproses channel Y (Luminance) saja
            img_yuv = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2YUV)
            
            if technique == "Global Equalization":
                img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
            elif technique == "CLAHE (Adaptive)":
                # CLAHE untuk meningkatkan kontras lokal tanpa noise berlebih
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                img_yuv[:, :, 0] = clahe.apply(img_yuv[:, :, 0])
                
            # Kembalikan ke BGR untuk ditampilkan
            self.processed_cv_image = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

        self.display_image(self.processed_cv_image, self.lbl_processed)

    def save_image(self):
        if self.processed_cv_image is None:
            messagebox.showwarning("Peringatan", "Tidak ada hasil gambar untuk disimpan!")
            return
            
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg")])
        if file_path:
            cv2.imwrite(file_path, self.processed_cv_image)
            messagebox.showinfo("Sukses", "Gambar berhasil disimpan!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEnhancementApp(root)
    root.mainloop()