import sys
import os
import json

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import uic

from typing import Union
    

class App(QApplication):
    def __init__(self, argv: list[str]) -> None:
        super(App, self).__init__(argv)
        self.current_arbfile_path: Union[str, None] = None
        self.arb_data: Union[dict, None] = None
        
        #window
        self.window: QMainWindow = uic.loadUi("localization_manager.ui")
        
        #inp
        self.inp_search: QLineEdit = self.window.findChild(QLineEdit, "inp_search")
        self.inp_string_content: QPlainTextEdit = self.window.findChild(QPlainTextEdit, "inp_string_content")
        self.inp_search: QLineEdit = self.window.findChild(QLineEdit, "inp_search")
        
        #lsw
        self.lsw_strings: QListWidget = self.window.findChild(QListWidget, "lsw_strings")
        
        #act
        self.act_open_arb: QAction = self.window.findChild(QAction, "act_open_arb")
        self.act_save_arb: QAction = self.window.findChild(QAction, "act_save_arb")
        self.act_save_arb_as: QAction = self.window.findChild(QAction, "act_save_arb_as")
        
        #btn
        self.btn_translate: QPushButton = self.window.findChild(QPushButton, "btn_translate")
        
        pass
    
    def start(self) -> None:
            
        #inp
        self.inp_string_content.textChanged.connect(self.save_current_string)
        self.inp_search.textChanged.connect(self.search)
        
        #lsw
        self.lsw_strings.itemClicked.connect(self.load_current_string)
        
        #act
        self.act_open_arb.triggered.connect(self.open_arbfile)
        self.act_save_arb.triggered.connect(self.save_arbfile)
        self.act_save_arb_as.triggered.connect(self.save_arbfile_as)
        
        #btn
        self.btn_translate.clicked.connect(self.translate)
        
        self.window.show()
        sys.exit(self.exec_())
        pass
    
    def open_arbfile(self) -> None:
        print("Hello open arb")
        dialog = QFileDialog()
        
        file_data = QFileDialog.getOpenFileName(dialog, "Apri File ARB", "", "File ARB (*.arb)")
        
        file_path, _ = file_data
        print(file_data)
        
        if not file_path:
            return

        self.current_arbfile_path = file_path
        #self.txt_result.update("Aprendo file... {self.current_arbfile_path}")
        self.load_arbfile()
        pass
    
    def load_arbfile(self) -> None:
        self.arb_data = self.get_arbfile()
        if not self.arb_data:
            print("File non valido")
            return

        print(self.arb_data)

        self.set_list(self.arb_data.keys())
        pass
    
    def save_arbfile(self) -> None:
        if not self.arb_data:
            self.arb_data = {}

        if not self.current_arbfile_path:
            self.save_arbfile_as()
            return

        #self.txt_result.update("Salvando file... {file_path}")
        with open(self.current_arbfile_path, "w+", encoding="utf-8") as arbfile:
            json.dump(self.arb_data, arbfile)
            #self.txt_result.update(f"Salvato file: {file_path}")
        pass

    def save_arbfile_as(self) -> None:
        dialog = QFileDialog()
        
        file_data = QFileDialog.getSaveFileName(dialog, "Salva File ARB", "", "File ARB (*.arb)")
        
        file_path, _ = file_data

        if not file_path:
            return

        self.current_arbfile_path = file_path
        self.save_arbfile()
        pass
    
    def load_current_string(self, selected_item: QListWidgetItem) ->None:

        if not self.arb_data:
            return

        string_data = self.arb_data[selected_item.text()]

        if not string_data:
            return

        print(f"loading string {selected_item.text()}")
        self.inp_string_content.setPlainText(string_data)
        
    def save_current_string(self) -> None:
        current_string = self.inp_string_content.toPlainText()
        selected_items = self.lsw_strings.selectedItems()

        if not selected_items or len(selected_items) == 0 or not current_string:
            return

        if not self.arb_data:
            return

        # Prendo solo la prima stringa selezionata
        string_key = selected_items[0].text()

        self.arb_data[string_key] = current_string
        pass

    
    def get_arbfile(self) -> Union[dict, None]:
        if not self.current_arbfile_path:
            return None

        file_exist = os.path.isfile(self.current_arbfile_path)

        if not file_exist:
            return None

        with open(self.current_arbfile_path, encoding="utf-8") as arbfile:
            arbfile_content: dict = json.load(arbfile)
            return arbfile_content
        
    def reset_list(self) -> None:
        if not self.arb_data:
            return

        self.set_list(self.arb_data.keys())
        
    def set_list(self, strings: Union[list[str], None]) -> None:
        if not strings:
            return
        
        rows = self.lsw_strings.count()
        
        for i in range(rows):
            self.lsw_strings.takeItem(0)
        self.lsw_strings.addItems(strings)
        pass
        
    def search(self) -> None:
        search_term = self.inp_search.text()
        
        if not search_term:
            self.reset_list()
            return

        search_term = search_term.rstrip().lower()

        if len(search_term) == 0:
            self.reset_list()
            return

        if not self.arb_data:
            return

        result = [(k, v) for k, v in self.arb_data.items()
                  if search_term in k.lower() or search_term in v.lower()]
        filtered_arb = dict(result)
        
        self.set_list(filtered_arb.keys())
        self.inp_string_content.setPlainText("")
    
    def translate(self) -> None:
        print("Hello Translate")
        pass
    
if __name__ == "__main__":
    app = App(sys.argv)
    app.start()
    pass