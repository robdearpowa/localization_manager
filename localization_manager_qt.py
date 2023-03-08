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
        
        self.window: QMainWindow = uic.loadUi("localization_manager.ui")
        self.inp_search: QLineEdit = self.window.findChild(QLineEdit, "inp_search")
        self.act_open_arb: QAction = self.window.findChild(QAction, "act_open_arb")
        self.btn_translate: QPushButton = self.window.findChild(QPushButton, "btn_translate")
        self.lsw_strings: QListWidget = self.window.findChild(QListWidget, "lsw_strings")
        self.inp_string_content: QPlainTextEdit = self.window.findChild(QPlainTextEdit, "inp_string_content")
        pass
    
    def start(self) -> None:
        self.act_open_arb.triggered.connect(self.open_arbfile)
        self.btn_translate.clicked.connect(self.translate)
        self.lsw_strings.currentItemChanged.connect(self.load_current_string)
        self.inp_string_content.textChanged.connect(self.save_current_string)
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

        #self.lbx_strings.update(self.arb_data.keys())
        #self.load_current_string(self.lbx_strings.get())
        rows = self.lsw_strings.count()
        
        for i in range(rows):
            self.lsw_strings.takeItem(0)
        self.lsw_strings.addItems(self.arb_data.keys())
        pass
    
    def load_current_string(self, selected_item: QListWidgetItem) ->None:

        if not self.arb_data:
            return

        string_data = self.arb_data[selected_item.text()]

        if not string_data:
            return

        print(f"loading string {self.arb_data}")
        self.inp_string_content.setPlainText(string_data)
        
    def save_current_string(self) -> None:
        current_string = self.inp_string_content.toPlainText()
        selected_items = self.lsw_strings.selectedItems()

        print(f"text changing {[x.text() for x in selected_items]}")
        if not selected_items or len(selected_items) == 0 or not current_string:
            return

        if not self.arb_data:
            return

        # Prendo solo la prima stringa selezionata
        string_key = selected_items[0].text()

        self.arb_data[string_key] = current_string
        print(f"text changed {self.arb_data}")
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
    
    def translate(self) -> None:
        print("Hello Translate")
        pass
    
if __name__ == "__main__":
    app = App(sys.argv)
    app.start()
    pass