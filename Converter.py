import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import shutil
from datetime import datetime

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

try:
    from pydub import AudioSegment
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False

try:
    import moviepy.editor as mp
    HAS_MOVIEPY = True
except ImportError:
    HAS_MOVIEPY = False

try:
    import zipfile
    HAS_ZIP = True
except ImportError:
    HAS_ZIP = False

class DanrexConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Danrex Converter")
        self.root.configure(bg='#0f0f1a')
        
        self.current_category = "Изображения"
        self.input_paths = []
        self.output_format = tk.StringVar()
        self.conversion_in_progress = False
        self.current_output_dir = ""
        
        self.setup_geometry()
        self.create_widgets()
        self.update_status("Готов к работе")
    
    def setup_geometry(self):
        try:
            self.root.state('zoomed')
        except:
            self.root.geometry("1000x600")
        self.root.minsize(900, 500)
    
    def create_widgets(self):
        main_container = tk.Frame(self.root, bg='#0f0f1a')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        self.create_navigation_panel(main_container)
        self.create_work_area(main_container)
        self.create_status_bar(main_container)
    
    def create_navigation_panel(self, parent):
        nav_frame = tk.Frame(parent, bg='#1a1a2e', width=240)
        nav_frame.pack(side=tk.LEFT, fill=tk.Y)
        nav_frame.pack_propagate(False)
        
        logo_frame = tk.Frame(nav_frame, bg='#1a1a2e')
        logo_frame.pack(fill=tk.X, pady=(30, 20))
        
        logo_label = tk.Label(logo_frame, text="⚡", 
                               font=('Segoe UI', 32),
                               bg='#1a1a2e', fg='#ff6b6b')
        logo_label.pack()
        
        title_label = tk.Label(logo_frame, text="Danrex Converter", 
                               font=('Segoe UI', 12, 'bold'),
                               bg='#1a1a2e', fg='#ffffff')
        title_label.pack(pady=(5, 0))
        
        subtitle_label = tk.Label(logo_frame, text="Конвертация файлов", 
                               font=('Segoe UI', 9),
                               bg='#1a1a2e', fg='#8888aa')
        subtitle_label.pack()
        
        separator = tk.Frame(nav_frame, bg='#2a2a4a', height=1)
        separator.pack(fill=tk.X, pady=20)
        
        categories = [
            ("🖼️", "Изображения", "#ff6b6b"),
            ("🎬", "Видео", "#4ecdc4"),
            ("🎵", "Аудио", "#45b7d1"),
            ("📄", "Документы", "#96ceb4"),
            ("🗜️", "Архивы", "#ffeaa7"),
            ("🧊", "3D Модели", "#dfe6e9"),
            ("🔤", "Шрифты", "#74b9ff"),
            ("📊", "Таблицы", "#a8e6cf"),
            ("💬", "Субтитры", "#ffd3b6"),
            ("🎮", "Игры", "#ffaaa5")
        ]
        
        self.category_buttons = {}
        for icon, cat_name, color in categories:
            btn_frame = tk.Frame(nav_frame, bg='#1a1a2e')
            btn_frame.pack(fill=tk.X, pady=2)
            
            btn = tk.Button(btn_frame, text=f"  {icon}  {cat_name}", 
                           command=lambda c=cat_name: self.switch_category(c),
                           bg='#1a1a2e', fg='#cccccc', bd=0, anchor='w',
                           font=('Segoe UI', 10), padx=20, pady=10,
                           activebackground='#2a2a4e', activeforeground=color,
                           cursor="hand2")
            btn.pack(fill=tk.X)
            self.category_buttons[cat_name] = btn
        
        separator2 = tk.Frame(nav_frame, bg='#2a2a4a', height=1)
        separator2.pack(fill=tk.X, pady=20)
        
        info_frame = tk.Frame(nav_frame, bg='#1a1a2e')
        info_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)
        
        version_label = tk.Label(info_frame, text="Версия 1.0.0", 
                                 bg='#1a1a2e', fg='#666680', font=('Segoe UI', 9))
        version_label.pack()
        
        author_label = tk.Label(info_frame, text="Danrex Studio", 
                                bg='#1a1a2e', fg='#666680', font=('Segoe UI', 8))
        author_label.pack()
    
    def create_work_area(self, parent):
        self.work_frame = tk.Frame(parent, bg='#0f0f1a')
        self.work_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        self.switch_category("Изображения")
    
    def switch_category(self, category):
        self.current_category = category
        for btn in self.category_buttons.values():
            btn.config(bg='#1a1a2e', fg='#cccccc')
        if category in self.category_buttons:
            self.category_buttons[category].config(bg='#2a2a4e', fg='#ff6b6b')
        
        for widget in self.work_frame.winfo_children():
            widget.destroy()
        self.create_category_ui()
    
    def create_category_ui(self):
        header_frame = tk.Frame(self.work_frame, bg='#0f0f1a')
        header_frame.pack(fill=tk.X, pady=(0, 25))
        
        category_colors = {
            "Изображения": "#ff6b6b", "Видео": "#4ecdc4", "Аудио": "#45b7d1",
            "Документы": "#96ceb4", "Архивы": "#ffeaa7", "3D Модели": "#dfe6e9",
            "Шрифты": "#74b9ff", "Таблицы": "#a8e6cf", "Субтитры": "#ffd3b6", "Игры": "#ffaaa5"
        }
        
        color = category_colors.get(self.current_category, "#ffffff")
        
        title_label = tk.Label(header_frame, text=self.current_category, 
                               font=('Segoe UI', 22, 'bold'),
                               bg='#0f0f1a', fg=color)
        title_label.pack(anchor='w')
        
        desc_label = tk.Label(header_frame, text="Выберите файлы для конвертации", 
                              font=('Segoe UI', 10),
                              bg='#0f0f1a', fg='#888888')
        desc_label.pack(anchor='w', pady=(5, 0))
        
        input_frame = tk.Frame(self.work_frame, bg='#1a1a2e', relief=tk.FLAT, bd=0)
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        input_inner = tk.Frame(input_frame, bg='#1a1a2e')
        input_inner.pack(fill=tk.X, padx=20, pady=20)
        
        path_label = tk.Label(input_inner, text="📁 Исходные файлы", 
                              bg='#1a1a2e', fg='#ffffff', font=('Segoe UI', 10, 'bold'))
        path_label.pack(anchor='w', pady=(0, 10))
        
        path_controls = tk.Frame(input_inner, bg='#1a1a2e')
        path_controls.pack(fill=tk.X)
        
        self.path_entry = tk.Entry(path_controls, bg='#0f0f1a', fg='#ffffff',
                                    font=('Segoe UI', 10), relief=tk.FLAT,
                                    insertbackground='#ff6b6b')
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=8)
        
        browse_btn = tk.Button(path_controls, text="Обзор", command=self.browse_files,
                               bg='#ff6b6b', fg='#ffffff', font=('Segoe UI', 10, 'bold'),
                               relief=tk.FLAT, padx=20, cursor="hand2")
        browse_btn.pack(side=tk.RIGHT)
        
        format_frame = tk.Frame(self.work_frame, bg='#1a1a2e', relief=tk.FLAT, bd=0)
        format_frame.pack(fill=tk.X, pady=(0, 20))
        
        format_inner = tk.Frame(format_frame, bg='#1a1a2e')
        format_inner.pack(fill=tk.X, padx=20, pady=20)
        
        format_label = tk.Label(format_inner, text="🎯 Выходной формат", 
                                bg='#1a1a2e', fg='#ffffff', font=('Segoe UI', 10, 'bold'))
        format_label.pack(anchor='w', pady=(0, 10))
        
        self.format_combo = ttk.Combobox(format_inner, textvariable=self.output_format,
                                          values=self.get_output_formats(),
                                          state="readonly", font=('Segoe UI', 11))
        self.format_combo.pack(fill=tk.X, ipady=5)
        if self.get_output_formats():
            self.format_combo.current(0)
        
        self.settings_frame = tk.Frame(self.work_frame, bg='#1a1a2e', relief=tk.FLAT, bd=0)
        self.settings_frame.pack(fill=tk.X, pady=(0, 25))
        
        self.create_settings_ui()
        
        progress_frame = tk.Frame(self.work_frame, bg='#0f0f1a')
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400,
                                             style="Accent.Horizontal.TProgressbar")
        self.progress_bar.pack(fill=tk.X)
        
        self.progress_label = tk.Label(progress_frame, text="", 
                                       bg='#0f0f1a', fg='#ff6b6b', font=('Segoe UI', 9))
        self.progress_label.pack(pady=(8, 0))
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Accent.Horizontal.TProgressbar", background='#ff6b6b',
                       troughcolor='#1a1a2e', bordercolor='#1a1a2e')
        
        convert_btn = tk.Button(self.work_frame, text="▶ НАЧАТЬ КОНВЕРТАЦИЮ", 
                                command=self.start_conversion,
                                bg='#ff6b6b', fg='#ffffff', font=('Segoe UI', 12, 'bold'),
                                relief=tk.FLAT, padx=30, pady=14, cursor="hand2")
        convert_btn.pack()
    
    def create_settings_ui(self):
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        
        settings_inner = tk.Frame(self.settings_frame, bg='#1a1a2e')
        settings_inner.pack(fill=tk.X, padx=20, pady=20)
        
        settings_label = tk.Label(settings_inner, text="⚙️ Настройки", 
                                  bg='#1a1a2e', fg='#ff6b6b', font=('Segoe UI', 10, 'bold'))
        settings_label.pack(anchor='w', pady=(0, 15))
        
        if self.current_category == "Изображения":
            quality_frame = tk.Frame(settings_inner, bg='#1a1a2e')
            quality_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(quality_frame, text="Качество:", bg='#1a1a2e', fg='#cccccc').pack(side=tk.LEFT, padx=(0, 15))
            self.quality_var = tk.IntVar(value=90)
            quality_slider = tk.Scale(quality_frame, from_=1, to=100, orient=tk.HORIZONTAL,
                                       variable=self.quality_var, bg='#1a1a2e', fg='#ff6b6b',
                                       highlightthickness=0, length=250)
            quality_slider.pack(side=tk.LEFT)
        
        elif self.current_category == "Видео":
            quality_frame = tk.Frame(settings_inner, bg='#1a1a2e')
            quality_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(quality_frame, text="Качество:", bg='#1a1a2e', fg='#cccccc').pack(side=tk.LEFT, padx=(0, 15))
            self.crf_var = tk.IntVar(value=23)
            crf_slider = tk.Scale(quality_frame, from_=0, to=51, orient=tk.HORIZONTAL,
                                   variable=self.crf_var, bg='#1a1a2e', fg='#4ecdc4',
                                   highlightthickness=0, length=250)
            crf_slider.pack(side=tk.LEFT)
        
        elif self.current_category == "Аудио":
            bitrate_frame = tk.Frame(settings_inner, bg='#1a1a2e')
            bitrate_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(bitrate_frame, text="Битрейт:", bg='#1a1a2e', fg='#cccccc').pack(side=tk.LEFT, padx=(0, 15))
            self.bitrate_var = tk.StringVar(value="192")
            bitrates = ["128", "192", "256", "320"]
            bitrate_combo = ttk.Combobox(bitrate_frame, textvariable=self.bitrate_var, 
                                          values=bitrates, state="readonly", width=10)
            bitrate_combo.pack(side=tk.LEFT)
            tk.Label(bitrate_frame, text="kbps", bg='#1a1a2e', fg='#cccccc').pack(side=tk.LEFT, padx=(5, 0))
        
        elif self.current_category == "Архивы":
            compress_frame = tk.Frame(settings_inner, bg='#1a1a2e')
            compress_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(compress_frame, text="Сжатие:", bg='#1a1a2e', fg='#cccccc').pack(side=tk.LEFT, padx=(0, 15))
            self.compress_level = ttk.Combobox(compress_frame, values=["Нормальный", "Максимальный"], 
                                                state="readonly", width=12)
            self.compress_level.set("Нормальный")
            self.compress_level.pack(side=tk.LEFT)
    
    def get_output_formats(self):
        formats = {
            "Изображения": ["PNG", "JPG", "WebP", "BMP", "TIFF", "ICO", "GIF"],
            "Видео": ["MP4", "AVI", "MKV", "WebM", "MOV", "GIF"],
            "Аудио": ["MP3", "WAV", "FLAC", "AAC", "OGG", "OPUS", "M4A"],
            "Документы": ["PDF", "TXT", "HTML", "RTF", "MD"],
            "Архивы": ["ZIP", "7Z", "TAR", "GZ"],
            "3D Модели": ["OBJ", "STL", "PLY", "glTF", "GLB"],
            "Шрифты": ["TTF", "OTF", "WOFF", "WOFF2"],
            "Таблицы": ["CSV", "JSON", "XML", "HTML"],
            "Субтитры": ["SRT", "ASS", "VTT", "SBV"],
            "Игры": ["FBX", "OBJ", "PNG", "WAV", "OGG"]
        }
        return formats.get(self.current_category, ["PNG", "JPG"])
    
    def browse_files(self):
        if self.current_category in ["Архивы"]:
            path = filedialog.askdirectory()
            if path:
                self.input_paths = [path]
                self.path_entry.delete(0, tk.END)
                self.path_entry.insert(0, path)
        else:
            paths = filedialog.askopenfilenames()
            if paths:
                self.input_paths = list(paths)
                self.path_entry.delete(0, tk.END)
                if len(paths) == 1:
                    self.path_entry.insert(0, paths[0])
                else:
                    self.path_entry.insert(0, f"Выбрано {len(paths)} файлов")
    
    def update_status(self, message, is_error=False, is_warning=False):
        self.status_label.config(text=message)
        if is_error:
            self.status_emoji.config(text="❌")
            self.status_label.config(fg='#ff6b6b')
        elif is_warning:
            self.status_emoji.config(text="⚠️")
            self.status_label.config(fg='#ffeaa7')
        else:
            self.status_emoji.config(text="✅")
            self.status_label.config(fg='#4ecdc4')
    
    def update_progress(self, current, total, filename):
        percent = (current / total) * 100 if total > 0 else 0
        self.root.after(0, lambda: self._update_progress_ui(percent, filename))
    
    def _update_progress_ui(self, percent, filename):
        self.progress_bar['value'] = percent
        self.progress_label.config(text=f"Конвертация: {percent:.0f}% - {os.path.basename(filename)}")
    
    def start_conversion(self):
        if self.conversion_in_progress:
            messagebox.showwarning("Предупреждение", "Конвертация уже выполняется!")
            return
        
        if not self.input_paths and not self.path_entry.get():
            messagebox.showwarning("Предупреждение", "Выберите файлы для конвертации!")
            return
        
        if not self.output_format.get():
            messagebox.showwarning("Предупреждение", "Выберите выходной формат!")
            return
        
        if not self.input_paths:
            self.input_paths = [self.path_entry.get()]
        
        self.conversion_in_progress = True
        self.update_status("Конвертация в процессе...")
        self.progress_bar['value'] = 0
        
        thread = threading.Thread(target=self.perform_conversion)
        thread.daemon = True
        thread.start()
    
    def perform_conversion(self):
        try:
            self.current_output_dir = os.path.join(os.path.dirname(self.input_paths[0]), "converted")
            os.makedirs(self.current_output_dir, exist_ok=True)
            
            converted = 0
            errors = 0
            total = len(self.input_paths)
            
            for i, file_path in enumerate(self.input_paths):
                self.update_progress(i + 1, total, file_path)
                success = self.convert_file(file_path)
                if success:
                    converted += 1
                else:
                    errors += 1
            
            self.conversion_in_progress = False
            self.update_status(f"Готово. Конвертировано {converted} из {total} файлов.")
            
            if converted > 0:
                messagebox.showinfo("Завершено", 
                                   f"Конвертация завершена!\n\n✅ Успешно: {converted}\n❌ Ошибок: {errors}\n\n📁 Результаты: {self.current_output_dir}")
            
        except Exception as e:
            self.conversion_in_progress = False
            self.update_status(f"Ошибка: {str(e)}", is_error=True)
    
    def convert_file(self, input_path):
        input_ext = os.path.splitext(input_path)[1][1:].upper()
        output_ext = self.output_format.get().upper()
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_name = f"{base_name}.{output_ext.lower()}"
        output_path = os.path.join(self.current_output_dir, output_name)
        
        try:
            if self.current_category == "Изображения" and HAS_PIL:
                img = Image.open(input_path)
                quality = getattr(self, 'quality_var', tk.IntVar(value=90)).get()
                
                if output_ext in ['JPG', 'JPEG']:
                    img.save(output_path, 'JPEG', quality=quality)
                elif output_ext == 'PNG':
                    img.save(output_path, 'PNG', compress_level=9)
                elif output_ext == 'WebP':
                    img.save(output_path, 'WebP', quality=quality)
                elif output_ext == 'ICO':
                    img.save(output_path, 'ICO', sizes=[(256, 256)])
                elif output_ext == 'GIF':
                    img.save(output_path, 'GIF', save_all=True)
                else:
                    img.save(output_path)
                return True
            
            elif self.current_category == "Видео" and HAS_MOVIEPY:
                video = mp.VideoFileClip(input_path)
                codec = 'libx264' if output_ext in ['MP4', 'MKV'] else 'libvpx-vp9'
                video.write_videofile(output_path, codec=codec, logger=None, verbose=False)
                video.close()
                return True
            
            elif self.current_category == "Аудио" and HAS_PYDUB:
                audio = AudioSegment.from_file(input_path)
                bitrate = getattr(self, 'bitrate_var', tk.StringVar(value="192")).get()
                audio.export(output_path, format=output_ext.lower(), bitrate=f"{bitrate}k")
                return True
            
            elif self.current_category == "Документы" and output_ext == "PDF":
                from reportlab.pdfgen import canvas as pdf_canvas
                from reportlab.lib.pagesizes import A4
                c = pdf_canvas.Canvas(output_path, pagesize=A4)
                c.drawString(100, 750, f"Конвертировано из: {os.path.basename(input_path)}")
                c.drawString(100, 730, f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                c.save()
                return True
            
            elif self.current_category == "Архивы" and output_ext == "ZIP":
                import zipfile
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    if os.path.isfile(input_path):
                        zipf.write(input_path, os.path.basename(input_path))
                    else:
                        for root, dirs, files in os.walk(input_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, input_path)
                                zipf.write(file_path, arcname)
                return True
            
            else:
                shutil.copy2(input_path, output_path)
                return True
                
        except Exception as e:
            return False
    
    def create_status_bar(self, parent):
        status_bar = tk.Frame(parent, bg='#1a1a2e', height=40)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_emoji = tk.Label(status_bar, text="✅", bg='#1a1a2e', fg='#4ecdc4', font=('Segoe UI', 12))
        self.status_emoji.pack(side=tk.LEFT, padx=(20, 10))
        
        self.status_label = tk.Label(status_bar, text="Готов к работе", 
                                     bg='#1a1a2e', fg='#cccccc', font=('Segoe UI', 10))
        self.status_label.pack(side=tk.LEFT)

def main():
    root = tk.Tk()
    app = DanrexConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
