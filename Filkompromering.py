import os
import locale

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, NumericProperty
from kivy.core.window import Window
from kivy.clock import Clock


import tkinter as tk
from tkinter import filedialog

from PIL import Image
import pillow_avif
import ghostscript

class FileCompressHandle(Screen):
    Start_nummer = NumericProperty()  # Lader Kivy automatisk opdaterer,
    compress_root = ObjectProperty()

class FilKomprimering(Screen):
    compress_file_list_container = ObjectProperty()
    status_label = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.root_tk = tk.Tk()
        self.root_tk.withdraw()

        self.selected_files = []

        self.default_output_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        self.output_folder = None

        Window.bind(on_dropfile=self.on_drop)

    def on_drop(self, window, file_path):
        formater = (".pdf",".jpg",".jpeg",".png",".webp",".avif")
        path = file_path.decode("utf-8")  # Når man drag and dropper vil Kivy gerne have
        # et input i bytes, derfor decoder vi med utf-8 fra str til bytes

        if os.path.isdir(path):  # Hvis det er en mappe (dir for directory/mappe)
            files_in_dir = [
                os.path.join(path, f)
                for f in os.listdir(path)
                if f.lower().endswith(formater)
            ]
            self.selected_files.extend(files_in_dir)

        elif path.lower().endswith(formater):  # Hvis det er en enkel fil i følgende format
            self.selected_files.append(path)

        self.update_file_list()

    def file_select(self):
        filepaths = filedialog.askopenfilenames(
            title="Vælg billeder og PDF filer",
            filetypes=[("Formater", "*.png;*.jpg;*.jpeg;*.webp;*.avif;*.pdf*")]
        )
        if filepaths:
            self.selected_files.extend(filepaths)
            self.update_file_list()

    def folder_select(self):
        formater = (".pdf",".jpg",".jpeg",".png",".webp",".avif")
        filepaths = filedialog.askdirectory()

        if os.path.isdir(filepaths):  # Hvis det er en mappe (dir for directory/mappe)
            files_in_dir = [
                os.path.join(filepaths, f)
                for f in os.listdir(filepaths)
                if f.lower().endswith(formater)
            ]
            self.selected_files.extend(files_in_dir)

        self.update_file_list()


    def update_file_list(self):
        self.compress_file_list_container.clear_widgets()
        for i, path in enumerate(self.selected_files):
            entry = FileCompressHandle()
            entry.entry_index = i
            entry.compress_root = self
            entry.ids.file_label.text = f"{os.path.basename(path)} - {os.path.getsize(path)/1000000:.2f} MB"
            self.compress_file_list_container.add_widget(entry)

    def ask_output_folder(self):
        folder = filedialog.askdirectory(title="Vælg mappesti")
        return folder if folder else self.create_unique_output_folder(self.default_output_folder)

    def create_unique_output_folder(self, base_folder):
        output_folder = os.path.join(base_folder, "PixelShifted") # Laver en mappe, hvis brugeren ikke vælger en
        counter = 1  # Programmet navngiver filer, og starter med billede 1
        while os.path.exists(output_folder):
            output_folder = os.path.join(base_folder, f"PixelShifted_{counter}") # her navngives de
            counter += 1 # og tæller op for hvert billede
        os.makedirs(output_folder) # Opretter mappen
        return output_folder

    def start_compressing(self):
        self.ids.status_label.color = (1, 0, 0, 1)
        if len(self.selected_files) < 1:  # Sørger for, at der mindst er valgt én fil
            self.ids.status_label.text = "Fejl: Vælg mindst én fil!"  # Hvis ikke, gives denne meddelelse
            return
        self.ids.status_label.color = (0.5, 0.95, 0.4, 1)
        self.ids.status_label.text = "Begynder behandling, vent venligst!"
        Clock.schedule_once(lambda dt: self.compress(), 0.1)

    def compress(self):
        try:
            self.compressed_files = []
            raw_size = sum(os.path.getsize(path) for path in self.selected_files) / 1000000
            self.output_folder = self.ask_output_folder()
            formater = (".jpg", ".jpeg", ".png", ".webp",".avif")
            for path in self.selected_files:
                if path.lower().endswith(formater):
                    try:
                        Open_img = Image.open(path)
                        self.ids.status_label.text = f"Behandler {os.path.basename(path)}."
                        width, height = Open_img.size
                        new_width = int(width*0.75)
                        new_height = int(height*0.75)
                        resized_img = Open_img.resize((new_width,new_height))

                        file_name_index = "Compressed - " + os.path.basename(path)
                        print(os.path.basename(path))
                        file_name_index_output = os.path.join(self.output_folder, file_name_index)

                        resized_img.save(file_name_index_output)
                        self.compressed_files.append(file_name_index_output)

                    except Exception as e:
                        self.ids.status_label.text = f"Error: {str(e)}"

                elif path.lower().endswith((".pdf")):
                    self.ids.status_label.text = f"Behandler {os.path.basename(path)}."
                    try:
                        output_name = f"Compressed - {os.path.basename(path)}"
                        output_path = os.path.join(self.output_folder, output_name)
                        args = [
                            "gs",
                            "-sDEVICE=pdfwrite",
                            "-dCompatibilityLevel=1.4",
                            "-dPDFSETTINGS=/prepress",
                            "-dNOPAUSE",
                            "-dQUIET",
                            "-dBATCH",
                            f"-sOutputFile={output_path}",
                            path
                        ]
                        ghostscript.Ghostscript(*args)
                        self.compressed_files.append(output_path)
                    except Exception as e:
                        self.ids.status_label.text = f"Error: {str(e)}"

        except Exception as e:
            self.ids.status_label.text = f"Error: {str(e)}"

        try:
            compressed_size = sum(os.path.getsize(path) for path in self.compressed_files)/1000000
            size_diff = raw_size-compressed_size
            self.ids.status_label.color = (0.5, 0.95,0.4,1)
            self.ids.status_label.text = f"Succes: Fil/filer reduceret med {size_diff:.2f} MB."
            self.selected_files = []
            self.update_file_list()


        except Exception as e:
            self.ids.status_label.text = f"Error: {str(e)}"

    def clear_list(self):
        self.selected_files = []
        self.update_file_list()
        self.ids.status_label.text = f""
        # Rydder listen