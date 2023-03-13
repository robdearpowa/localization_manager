import sys
import os
import json

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import uic

from typing import Union
from googletrans import Translator
from pathlib import Path
    

class App(QApplication):
    def __init__(self, argv: list[str]) -> None:
        super(App, self).__init__(argv)
        self.current_arbfile_path: Union[str, None] = None
        self.arb_data: Union[dict, None] = None
        self.translator: Translator = Translator()
        self.entry_to_copy: Union[tuple[str, str]] = None
        self.original_arb_data: Union[dict, None] = None
        
        #window
        self.window: QMainWindow = uic.loadUi("localization_manager.ui")
        
        #mnu
        self.mnu_modifica: QMenu = self.window.findChild(QMenu, "mnu_modifica")
        
        #inp
        self.inp_search: QLineEdit = self.window.findChild(QLineEdit, "inp_search")
        self.inp_string_content: QPlainTextEdit = self.window.findChild(QPlainTextEdit, "inp_string_content")
        self.inp_search: QLineEdit = self.window.findChild(QLineEdit, "inp_search")
        
        #cmb
        self.cmb_from: QComboBox = self.window.findChild(QComboBox, "cmb_from")
        self.cmb_to: QComboBox = self.window.findChild(QComboBox, "cmb_to")
        
        #lsw
        self.lsw_strings: QListWidget = self.window.findChild(QListWidget, "lsw_strings")
        
        #act
        self.act_open_arb: QAction = self.window.findChild(QAction, "act_open_arb")
        self.act_save_arb: QAction = self.window.findChild(QAction, "act_save_arb")
        self.act_save_arb_as: QAction = self.window.findChild(QAction, "act_save_arb_as")
        self.act_new_string: QAction = self.window.findChild(QAction, "act_new_string")
        self.act_rename_string: QAction = self.window.findChild(QAction, "act_rename_string")
        self.act_delete_string: QAction = self.window.findChild(QAction, "act_delete_string")
        self.act_copy_string: QAction = self.window.findChild(QAction, "act_copy_string")
        self.act_paste_string: QAction = self.window.findChild(QAction, "act_paste_string")
        
        #btn
        self.btn_translate: QPushButton = self.window.findChild(QPushButton, "btn_translate")
        
        pass
    
    def start(self) -> None:
        
        #window
        self.window.closeEvent = self.check_changes
            
        #inp
        self.inp_string_content.textChanged.connect(self.save_current_string)
        self.inp_search.textChanged.connect(self.search)
        
        #lsw
        self.lsw_strings.currentItemChanged.connect(self.load_current_string)
        self.lsw_strings.addActions(self.mnu_modifica.actions())
        
        #act
        self.act_open_arb.triggered.connect(self.open_arbfile)
        self.act_save_arb.triggered.connect(self.save_arbfile)
        self.act_save_arb_as.triggered.connect(self.save_arbfile_as)
        self.act_new_string.triggered.connect(self.new_string)
        self.act_rename_string.triggered.connect(self.rename_string)
        self.act_delete_string.triggered.connect(self.delete_string)
        self.act_copy_string.triggered.connect(self.copy_string)
        self.act_paste_string.triggered.connect(self.paste_string)
        
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
        if self.arb_data == None:
            print("File non valido")
            return

        print(self.arb_data)
        self.original_arb_data = self.arb_data.copy()

        self.reset_list()
        self.inp_string_content.setPlainText("")
        pass
    
    def save_arbfile(self) -> None:
        if self.arb_data == None:
            self.arb_data = {}

        if not self.current_arbfile_path:
            self.save_arbfile_as()
            return

        #self.txt_result.update("Salvando file... {file_path}")
        with open(self.current_arbfile_path, "w+", encoding="utf-8") as arbfile:
            json.dump(self.arb_data, arbfile, sort_keys=False, indent=2, ensure_ascii=False)
            self.alert_user(f"File salvato: {self.current_arbfile_path}")
            self.original_arb_data = self.arb_data.copy()
            self.update_window_title()
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
    
    def load_current_string(self, selected_item: QListWidgetItem, prev_item: QListWidgetItem) -> None:

        if self.arb_data == None or selected_item == None:
            return

        string_data = self.arb_data[selected_item.text()]

        if string_data == None:
            return

        print(f"loading string {selected_item.text()}")
        self.inp_string_content.setPlainText(string_data)
        
    def save_current_string(self) -> None:
        current_string = self.inp_string_content.toPlainText()
        current_item = self.lsw_strings.currentItem()

        if current_item == None or current_string == None:
            return

        if self.arb_data == None:
            return

        # Prendo solo la prima stringa selezionata
        string_key = current_item.text()

        self.arb_data[string_key] = current_string
        self.update_window_title()
        print(f"saving string {string_key}")
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
        if self.arb_data == None:
            return

        self.set_list(self.arb_data.keys())
        
    def set_list(self, strings: Union[list[str], None]) -> None:
        if strings == None:
            return
        
        self.lsw_strings.setCurrentItem(None)
        
        rows = self.lsw_strings.count()
        
        for i in range(rows):
            self.lsw_strings.takeItem(0)
        self.lsw_strings.addItems(strings)
        self.update_window_title()
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

        if self.arb_data == None:
            return

        result = [(k, v) for k, v in self.arb_data.items()
                  if search_term in k.lower() or search_term in v.lower()]
        filtered_arb = dict(result)
        
        self.set_list(filtered_arb.keys())
        self.inp_string_content.setPlainText("")
        
    def new_string(self) -> None:
        if self.arb_data == None:
            self.arb_data = {}
            
            
        new_string_name = self.text_from_user("Nome stringa nuova")
        
        #L'utente ha annullato l'operazione
        if new_string_name == None:
            return
        
        if not new_string_name:
            self.alert_user("Nome della stringa non valido")
            return
        
        if new_string_name in self.arb_data.keys():
            self.alert_user("Questa stringa già esiste")
            print("This string already exist")
            return
            
        current_item: Union[QListWidgetItem, None] = self.lsw_strings.currentItem()
        current_key: Union[str, None] = current_item.text() if current_item else None
        current_pos: Union[int, None] = list(self.arb_data.keys()).index(current_key) if current_key else None
        
        items = list(self.arb_data.items())
        
        if current_pos != None:
            items.insert(current_pos + 1, (new_string_name, ""))
            self.arb_data = dict(items)
        else:
            self.arb_data[new_string_name] = ""
            
        self.reset_list()
        self.inp_string_content.setPlainText("")
        print("Hello new string")
        pass
    
    def rename_string(self) -> None:
        if self.arb_data == None:
            return
        
        current_item = self.lsw_strings.currentItem()
        
        if not current_item:
            self.alert_user("Nessuna stringa selezionata")
            return
        
        current_string = self.arb_data[current_item.text()]
            
            
        new_string_name = self.text_from_user("Rinomina String", current_item.text())
        
        #L'utente ha annullato l'operazione
        if new_string_name == None:
            return
        
        if not new_string_name:
            self.alert_user("Nome della stringa non valido")
            return
        
        if new_string_name in self.arb_data.keys():
            self.alert_user("Questa stringa già esiste")
            print("This string already exist")
            return
            
        current_key: Union[str, None] = current_item.text() if current_item else None
        current_pos: Union[int, None] = list(self.arb_data.keys()).index(current_key) if current_key else None
        
        items = list(self.arb_data.items())
        
        if current_pos == None:
            self.alert_user("Posizione stringa non valida")
            return
        
        items.pop(current_pos)
        items.insert(current_pos, (new_string_name, current_string))
        self.arb_data = dict(items)
            
        self.reset_list()
        print("Hello rename string")
        pass
    
    def delete_string(self) -> None:
        if self.arb_data == None:
            self.alert_user("Nessuna file di stringe")
            print("No arb data")
            return
        
        current_item: Union[QListWidgetItem, None] = self.lsw_strings.currentItem()
        current_key: Union[str, None] = current_item.text() if current_item else None
        
        if current_key == None:
            self.alert_user("Nessuna stringa selezionata da eliminare")
            print("No key to delete")
            return
        
        self.arb_data.pop(current_key)
        self.reset_list()
        self.inp_string_content.setPlainText("")
        print("Hello delete string")
        pass
    
    def copy_string(self) -> None:
        print("Hello copy")
        current_item = self.lsw_strings.currentItem()
        
        
        if self.arb_data == None or current_item == None:
            return
        
        current_key = current_item.text()
        current_value = self.arb_data[current_key]
        
        self.entry_to_copy = (current_key, current_value)
        pass
    
    def paste_string(self) -> None:
        print("Hello paste")
        
        if self.entry_to_copy == None:
            return
        
        new_string_name, value = self.entry_to_copy
        
        while True:
            if new_string_name not in self.arb_data.keys():
                break
            print("This string already exist")
            new_string_name = f"{new_string_name} copy"
                
        current_item: Union[QListWidgetItem, None] = self.lsw_strings.currentItem()
        current_key: Union[str, None] = current_item.text() if current_item else None
        current_pos: Union[int, None] = list(self.arb_data.keys()).index(current_key) if current_key else None
        
        items = list(self.arb_data.items())
        
        if current_pos != None:
            items.insert(current_pos + 1, (new_string_name, value))
            self.arb_data = dict(items)
        else:
            self.arb_data[new_string_name] = value
            
        self.reset_list()
        self.inp_string_content.setPlainText("")
        pass
    
    def alert_user(self, message: str) -> None:
        message = QMessageBox.information(self.window, self.window.windowTitle(), message)
        pass
    
    def ask_user(self, message: str) -> QMessageBox.StandardButton:
        result = QMessageBox.information(self.window, self.window.windowTitle(), message, QMessageBox.Yes|QMessageBox.No)
        return result
    
    def text_from_user(self, message: str, text: str = "") -> Union[str, None]:
        result, ok = QInputDialog.getText(self.window, self.window.windowTitle(), message, text=text)
        return result.strip() if ok else None
    
    def update_window_title(self) -> None:
        
        file_name = ""
        
        if self.current_arbfile_path != None:
            file_name = Path(self.current_arbfile_path).stem
            
        if self.arb_data != self.original_arb_data:
            self.window.setWindowTitle(f"Gestore Localizzazione {file_name}*")
        else:
            self.window.setWindowTitle(f"Gestore Localizzazione {file_name}")
            
    def check_changes(self, event) -> None:
        print("Hello check changes")
        event.ignore()
        
        result = True
        if self.arb_data != self.original_arb_data:
            result = self.ask_user("Hai delle modifiche non salvate, vuoi salvare?") == QMessageBox.Yes
            
        if result:
            self.save_arbfile()
        
        event.accept()
        pass
    
    def translate(self) -> None:
        lang_from = self.cmb_from.currentText()
        lang_to = self.cmb_to.currentText()
        
        current_string = self.inp_string_content.toPlainText()
        
        
        if not lang_to:
            self.alert_user("Nessuna traduzione selezionata")
            return

        current_string = current_string.strip() if current_string else ""

        if len(current_string) == 0:
            self.alert_user("Impossibile tradurre una stringa vuota")
            return

        try:
            response = self.translator.translate(
                text=current_string,
                src=lang_from if lang_from and len(
                    lang_from.strip()) > 0 else "auto",
                dest=lang_to,
            )

            if not response:
                return
            
            self.inp_string_content.setPlainText(response.text)
        finally:
            pass

if __name__ == "__main__":
    app = App(sys.argv)
    app.start()
    pass