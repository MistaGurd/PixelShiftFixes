from kivy.uix.screenmanager import Screen # Til screen manager i Main
from kivy.properties import ObjectProperty, NumericProperty
from kivy.core.window import Window
from kivy.clock import Clock

import tkinter as tk
from tkinter import filedialog # Windows dialog vindue
import os
import threading

from pypdf import PdfWriter


class PDFNummer(Screen):
    Start_nummer = NumericProperty() # Lader Kivy automatisk opdaterer,
    merger_root = ObjectProperty()

class PDF_Merging(Screen):
    pdf_list_container = ObjectProperty()
    status_label = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.root_tk = tk.Tk()
        self.root_tk.withdraw()

        self.selected_pdfs = []

        Window.bind(on_dropfile=self.on_drop)

    def on_drop(self, window, file_path):
        path = file_path.decode("utf-8")  # Når man drag and dropper vil Kivy gerne have
                                          # et input i bytes, derfor decoder vi med utf-8 fra str til bytes

        Clock.schedule_once(lambda dt: setattr(self.ids.status_label, "text", ""))
        if os.path.isdir(path):  # Hvis det er en mappe (dir for directory/mappe)
            pdf_in_dir = [
                os.path.join(path,f)
                for f in os.listdir(path)
                if f.lower().endswith(".pdf")
            ]
            self.selected_pdfs.extend(pdf_in_dir)

        elif path.lower().endswith((".pdf")): # Hvis det er en enkel fil i følgende format
            self.selected_pdfs.append(path)

        self.update_pdf_list()
    def add_pdfs(self):
        filepaths = filedialog.askopenfilenames(
            title="Vælg PDF filer",
            filetypes=[("PDF Fil", "*.pdf")]
        )
        if filepaths:
            self.selected_pdfs.extend(filepaths)
            self.update_pdf_list()

    def update_pdf_list(self):
        self.pdf_list_container.clear_widgets()
        for i, path in enumerate(self.selected_pdfs):
            print(i, path)
            entry = PDFNummer()
            entry.entry_index = i
            entry.merger_root = self
            entry.ids.file_label.text = os.path.basename(path)
            self.pdf_list_container.add_widget(entry)

    def move_up(self, index):
        if index > 0:
            self.selected_pdfs[index], self.selected_pdfs[index-1] = self.selected_pdfs[index-1], self.selected_pdfs[index]
            self.update_pdf_list()


    def move_down(self, index):
        if index < len(self.selected_pdfs) - 1:
            self.selected_pdfs[index], self.selected_pdfs[index+1] = self.selected_pdfs[index+1], self.selected_pdfs[index]
            self.update_pdf_list()

    def start_merging(self):
        if len(self.selected_pdfs) < 2: # Sørger for, at der mindst er valgt to PDF filer
            self.ids.status_label.color = (1, 0, 0, 1)
            self.status_label.text = "Fejl: Vælg mindst to PDF filer!" # Hvis ikke, gives denne meddelelse
            return

        for pdf_path in self.selected_pdfs:
            if not os.path.exists(pdf_path):
                self.ids.status_label.color = (1, 0, 0, 1)
                Clock.schedule_once(lambda dt: setattr(self.ids.status_label, 'text', f"Fejl, filen {os.path.basename(pdf_path)} findes ikke! \n Er den blevet flyttet, eller slettet?"))
                return

        if len(self.selected_pdfs) >= 2:
            output_path = filedialog.asksaveasfilename(
                title="Vælg destinationssti og navn til merged PDF",
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")]
            )
            # Vha. tkinter kan destinationsstien vælges, inklusiv navn.
            # Sørger selv for, at formattet bliver PDF
            if not output_path:
                return

            if output_path:
                self.ids.status_label.color = (0.5, 0.95, 0.4, 1)
                Clock.schedule_once(lambda dt: setattr(self.ids.status_label, "text", "Begynder behandling, vent venligst!"),-1)
                Clock.schedule_once(lambda dt: threading.Thread(target=self.merge_pdfs(output_path), args=(self.selected_pdfs,), daemon=True).start(),1)
            #threading.Thread(target=self.merge_pdfs(output_path), args=(self.selected_pdfs,), daemon=True).start()

    def merge_pdfs(self, output_path):
        try:
            merger = PdfWriter() # Variabel af PyPDF
            for pdf in self.selected_pdfs:
                merger.append(pdf) # Appender de valgter PDF'er
            merger.write(output_path) # Gemmer den nye merged fil med write fra PyPDF4
            merger.close() # Rydder chachen

            # Sørger automatisk for at ryde listen når PDFer er blevet merged
            # Klar til brug igen, med det samme!
        except Exception as e:
            self.status_label.color: (1,0,0,1)
            self.status_label.text = f"Fejl: {str(e)}" # Hvis fejl skulle opstå, kan brugeren her se, hvad der gik galt

        if os.path.exists(output_path):
            self.status_label.color = (0.5, 0.95,0.4,1)
            Clock.schedule_once(lambda dt: setattr(self.ids.status_label, "text", f"Succes: Merged PDF gemt som {os.path.basename(output_path)}"))
            self.status_label.text = f"Succes: Merged PDF gemt som {os.path.basename(output_path)}"
            self.selected_pdfs = []
            self.update_pdf_list()

        if not os.path.exists(output_path):
            self.clear_list()
            return

    def clear_list(self):
        self.selected_pdfs = []
        self.update_pdf_list()
        self.ids.status_label.text = f""
        # Rydder listen