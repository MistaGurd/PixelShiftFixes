import os
#import locale

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, NumericProperty
from kivy.core.window import Window
from kivy.clock import Clock

from pathlib import Path

import tkinter as tk
from tkinter import filedialog

from PIL import Image
import pillow_avif
from pdf2docx import Converter
from docx2pdf import convert as d2pdfc # as d2pdfc for ikke at programmet ikke forveksler pdf2docx og docx2pdf
from txt2docx import txt2docx
from docx import Document

class FileConvertHandle(Screen):
    Start_nummer = NumericProperty()  # Lader Kivy automatisk opdaterer,
    convert_root = ObjectProperty()

class FileConvert(Screen):
    format_file_list_container = ObjectProperty()
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
        formater = (".pdf",".jpg",".jpeg",".png",".webp",".avif",".docx",".txt")
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
            title="Vælg mellem billeder, PDF, Docx, & txt",
            filetypes=[("Formater", "*.png;*.jpg;*.jpeg;*.webp;*.avif;*.pdf;*.docx;*.txt;*")]
        )
        if filepaths:
            self.selected_files.extend(filepaths)
            self.update_file_list()

    def folder_select(self):
        formater = (".pdf",".jpg",".jpeg",".png",".webp",".avif",".docx",".txt")
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
        self.format_file_list_container.clear_widgets()
        for i, path in enumerate(self.selected_files):
            entry = FileConvertHandle()
            entry.entry_index = i
            entry.convert_root = self
            entry.ids.file_label.text = f"{os.path.basename(path)} - {os.path.getsize(path)/1000000:.2f} MB"
            self.format_file_list_container.add_widget(entry)

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


    def start_converting(self):
        self.ids.status_label.color = (1, 0, 0, 1)
        if len(self.selected_files) < 1:  # Sørger for, at der mindst er valgt én fil
            self.ids.status_label.text = "Fejl: Vælg mindst én fil!"  # Hvis ikke, gives denne meddelelse
            return
        self.ids.status_label.color = (0.5, 0.95, 0.4, 1)
        self.ids.status_label.text = "Begynder behandling, vent venligst!"
        Clock.schedule_once(lambda dt: self.convert(), 0.1)

    def convert(self):
        try:
            self.converted_files = []
            self.output_folder = self.ask_output_folder()
            for path in self.selected_files:
                if path.lower().endswith((".jpg",".jpeg",".webp",".avif")):
                    try:
                        Open_img = Image.open(path)
                        file_name_index = "Konverteret - " + Path(path).stem + ".png" # https://stackoverflow.com/questions/678236/how-do-i-get-the-filename-without-the-extension-from-a-path-in-python#47496703
                        file_name_index_output = os.path.join(self.output_folder, file_name_index)
                        Open_img.save(file_name_index_output)
                        self.converted_files.append(file_name_index_output)
                    except Exception as e:
                        self.ids.status_label.text = f"Error: {str(e)}"

                elif path.lower().endswith((".png")):
                    try:
                        Open_img = Image.open(path)
                        png_file_name_index = "Konverteret - " + Path(path).stem + ".jpg" # https://stackoverflow.com/questions/678236/how-do-i-get-the-filename-without-the-extension-from-a-path-in-python#47496703
                        png_file_name_index_output = os.path.join(self.output_folder, png_file_name_index)
                        Open_img.save(png_file_name_index_output)
                        self.converted_files.append(png_file_name_index_output)
                    except Exception as e:
                        self.ids.status_label.text = f"Error: {str(e)}"


                elif path.lower().endswith((".pdf")):
                    try:
                        pdf = Converter(path) # https://pdf2docx.readthedocs.io/en/latest/quickstart.convert.html
                        pdf_file_name_index = "Konverteret - " + Path(path).stem + ".docx"  # https://stackoverflow.com/questions/678236/how-do-i-get-the-filename-without-the-extension-from-a-path-in-python#47496703
                        pdf_file_name_index_output = os.path.join(self.output_folder, pdf_file_name_index)
                        pdf.convert(pdf_file_name_index_output)
                        self.converted_files.append(pdf_file_name_index_output)
                    except Exception as e:
                        self.ids.status_label.text = f"Error: {str(e)}"

                elif path.lower().endswith((".docx")):
                    try:
                        docx_file_name_index = "Konverteret - " + Path(path).stem + ".pdf"  # https://stackoverflow.com/questions/678236/how-do-i-get-the-filename-without-the-extension-from-a-path-in-python#47496703
                        docx_file_name_index_output = os.path.join(self.output_folder, docx_file_name_index)
                        d2pdfc(path, docx_file_name_index_output) # https://pypi.org/project/docx2pdf/
                        self.converted_files.append(docx_file_name_index_output)
                    except Exception as e:
                        self.ids.status_label.text = f"Error: {str(e)}"

                elif path.lower().endswith((".txt")):
                    try:
                        txt_file_name_index = "Konverteret - " + Path(path).stem + ".docx"  # https://stackoverflow.com/questions/678236/how-do-i-get-the-filename-without-the-extension-from-a-path-in-python#47496703
                        txt_file_name_index_output = os.path.join(self.output_folder, txt_file_name_index)

                        txt2docx.txt2docx(path,txt_file_name_index_output)

                        self.converted_files.append(txt_file_name_index_output)

                    except Exception as e:
                        self.ids.status_label.color = (1, 0, 0, 1)
                        self.ids.status_label.text = f"Error: {str(e)}"

                self.ids.status_label.color = (0.5, 0.95, 0.4, 1)
                self.ids.status_label.text = f"Succes: Alle filer konverteret!"
                self.selected_files = []
                self.update_file_list()


        except Exception as e:
            self.ids.status_label.text = f"Error: {str(e)}"

    def clear_list(self):
        self.selected_files = []
        self.update_file_list()
        self.ids.status_label.text = f""
        # Rydder listen