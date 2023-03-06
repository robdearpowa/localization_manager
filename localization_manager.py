import os
import json
import PySimpleGUI as gui
import tkinter as tk

from typing import Union


ARB_FILETYPE = (("File di localizzazione", "*.arb"),)

def repack(widget, fill, expand, before=None):
    pack_info = widget.pack_info()
    pack_info.update({'fill':fill, 'expand':expand, 'before':before})
    widget.pack(**pack_info)


class App:
    def __init__(self) -> None:
        self.running: bool = False
        self.arb_data: Union[dict, None] = None
        self.current_arbfile_path: Union[str, None] = None

        gui.LOOK_AND_FEEL_TABLE["Marketwall"] = {
            "BACKGROUND": "#424242",
            "TEXT": "#FFFFFF",
            "INPUT": "#656565",
            "TEXT_INPUT": "#FFFFFF",
            "SCROLL": "#212121",
            "BUTTON": ("#FFFFFF", "#4595F7"),
            "PROGRESS": ("#656565", "#4595F7"),
            "BORDER": 1, "SLIDER_DEPTH": 0,
            "PROGRESS_DEPTH": 0,
        }

        gui.theme('Marketwall')

        input_background = gui.theme_input_background_color()

        modify_menu = ["&Rinomina stringa  (Crtl+R)::-MENURENAMESTRING-",
                                "&Aggiungi stringa   (Crtl+A)::-MENUADDSTRING-",
                                "&Inserisci stringa   (Crtl+I)::-MENUINSERTSTRING-",
                                "&Duplica stringa    (Crtl+D)::-MENUDUPESTRING-",
                                "&Rimuovi stringa::-MENUREMOVESTRING-",]

        menu_layout = [
            ["&File", ['&Apri File ARB (Crtl+O)::-MENUOPEN-',
                       '&Salva             (Ctrl+S)::-MENUSAVE-',
                       'Salva come...::-MENUSAVEAS-']],
            ["&Modifica", modify_menu]
        ]
        
        lbx_right_click_menu = ["&Right", modify_menu]

        self.layout: list[list] = [
            [gui.Menu(menu_layout)],
            [gui.Text("Cerca")],
            [gui.Input(key="-INPSEARCH-", enable_events=True, expand_x=True)],
            [gui.Listbox([], key="-LBXSTRINGS-",
                         expand_y=True,
                         expand_x=False,
                         enable_events=True,
                         horizontal_scroll=True,
                         size=(40, None),
                         right_click_menu=lbx_right_click_menu), 
             gui.Multiline(key="-MTLCURRENTSTRING-", expand_x=True, expand_y=True, enable_events=True,)],
            [gui.Text("Seleziona il file di lingue", key="-TXTRESULT-")],
        ]

        self.window: gui.Window = gui.Window(
            "Gestore Localizzazione",
            layout=self.layout,
            resizable=True,
        )

        self.window.finalize()
        #Shortcut menu file
        self.window.bind("<Control_L><o>", "-MENUOPEN-")
        self.window.bind("<Control_L><s>", "-MENUSAVE-")
        
        #Shortcut menu modifica
        self.window.bind("<Control_L><r>", "-MENURENAMESTRING-")
        self.window.bind("<Control_L><a>", "-MENUADDSTRING-")
        self.window.bind("<Control_L><i>", "-MENUINSERTSTRING-")
        self.window.bind("<Control_L><d>", "-MENUDUPESTRING-")


        w, h = self.window.size

        self.window.set_min_size((w, 400))

        # Valorizzazione componenti

        self.lbx_strings: gui.Listbox = self.window["-LBXSTRINGS-"] #type: ignore
        self.inp_current_string: gui.Multiline = self.window["-MTLCURRENTSTRING-"] #type: ignore
        self.inp_search: gui.Input = self.window["-INPSEARCH-"] #type: ignore
        self.txt_result: gui.Text = self.window["-TXTRESULT-"] #type: ignore

        lbx_strings_widget: Union[tk.Widget, None] = self.lbx_strings.Widget #type: ignore
        inp_current_string_widget: Union[tk.Widget, None] = self.inp_current_string.Widget #type: ignore
        
        if lbx_strings_widget and inp_current_string_widget:
            repack(lbx_strings_widget,        'y', 0)
            repack(lbx_strings_widget.master, 'y', 0, inp_current_string_widget.master)
        pass

    def start(self) -> None:
        self.running = True
        print("Running")

        while self.running:
            data = self.window.read()
            if data:
                event, values = data
                
                if event == gui.WIN_CLOSED or event == "Cancel":
                    self.running = False
                    continue

                if event.endswith("-MENUOPEN-"):
                    self.open_arbfile()
                    
                if event.endswith("-MENUSAVE-"):
                    self.save_arbfile(self.current_arbfile_path)
                    
                if event.endswith("-MENUSAVEAS-"):
                    self.save_arbfile_as()
                    
                if event.endswith("-MENURENAMESTRING-"):
                    self.rename_string()
                    
                if event.endswith("-MENUADDSTRING-"):
                    self.add_string()
                    
                if event.endswith("-MENURENAMESTRING-"):
                    self.rename_string()

                if event == self.lbx_strings.key:
                    self.load_current_string(values[event])

                if event == self.inp_current_string.key:
                    self.save_current_string(values[self.lbx_strings.key], values[event])

                if event == self.inp_search.key:
                    self.search(values[event])
        pass

    def open_arbfile(self) -> None:
        file_path = gui.popup_get_file("Apri un File Localizzazione ARB",
                                       file_types=ARB_FILETYPE,
                                       default_path=self.current_arbfile_path if self.current_arbfile_path else "",
                                       keep_on_top=True)
        
        if not file_path:
            return
        
        self.current_arbfile_path = file_path
        self.txt_result.update("Aprendo file... {self.current_arbfile_path}")
        self.load_arbfile(self.current_arbfile_path)
        
        self.txt_result.update(f"Aperto file: {self.current_arbfile_path}")

        pass
    
    def save_arbfile(self, file_path: Union[str, None]) -> None:
        if not self.arb_data:
            self.arb_data = {}
        
        if not file_path:
            self.save_arbfile_as()
            return
        
        self.txt_result.update("Salvando file... {file_path}")
        with open(file_path, "w+", encoding="utf-8") as arbfile:
            json.dump(self.arb_data, arbfile)
            self.txt_result.update(f"Salvato file: {file_path}")
        pass
            
    def save_arbfile_as(self) -> None:
        file_path = gui.popup_get_file("Salva il File di Localizzazione",
                                       file_types=ARB_FILETYPE,
                                       default_path=self.current_arbfile_path if self.current_arbfile_path else "",
                                       save_as=True,
                                       keep_on_top=True)
        
        if not file_path:
            return
        
        self.current_arbfile_path = file_path
        self.save_arbfile(self.current_arbfile_path)
        pass

    def get_arbfile(self, file_path: Union[str, None]) -> Union[dict, None]:
        if not file_path:
            return None

        file_exist = os.path.isfile(file_path)

        if not file_exist:
            return None

        with open(file_path, encoding="utf-8") as arbfile:
            arbfile_content: dict = json.load(arbfile)
            return arbfile_content

    def load_arbfile(self, file_path: Union[str, None]) -> None:
        self.arb_data = self.get_arbfile(file_path)

        if not self.arb_data:
            print("File non valido")
            return

        print(self.arb_data)

        self.lbx_strings.update(self.arb_data.keys())
        self.load_current_string(self.lbx_strings.get())
        pass

    def load_current_string(self, selected_strings: Union[list, None]) -> None:
        
        if not selected_strings or len(selected_strings) == 0 or not self.arb_data:
            self.inp_current_string.update("")
            return

        #Prendo solo la prima stringa selezionata
        string_key = selected_strings[0]

        string_data = self.arb_data[string_key]

        if not string_data:
            self.inp_current_string.update("")
            return
        
        self.inp_current_string.update(string_data)

    def save_current_string(self, selected_strings: Union[list, None], current_string: Union[str, None]) -> None:
        if not selected_strings or len(selected_strings) == 0 or not current_string:
            return
        
        if not self.arb_data:
            return
        
        #Prendo solo la prima stringa selezionata
        string_key = selected_strings[0]

        self.arb_data[string_key] = current_string
        pass

    def search(self, search_term: Union[str, None]) -> None:
        if not search_term:
            self.reset_list()
            return

        search_term = search_term.rstrip().lower()

        if len(search_term) == 0:
            self.reset_list()
            return

        if not self.arb_data:
            return

        result = [(k, v) for k, v in self.arb_data.items() if search_term in k.lower() or search_term in v.lower()]
        filtered_arb = dict(result)

        self.lbx_strings.update(filtered_arb.keys())
        self.load_current_string(self.lbx_strings.get())
        
    def reset_list(self) -> None:
        if not self.arb_data:
            return

        self.lbx_strings.update(self.arb_data.keys())
        self.load_current_string(self.lbx_strings.get())
        
    def add_string(self, rename_string: Union[str, None]=None) -> None:
        string_key = gui.popup_get_text("Rinomina una nuova stringa" if rename_string else "Aggiungi una nuova stringa",
                                        default_text=rename_string if rename_string else "")
        
        if not self.arb_data:
            self.arb_data = {}
            
        if string_key in self.arb_data.keys():
            self.txt_result.update("Impossibile creare la stringa: Stringa già esistente")
            return
        
        if not string_key:
            self.txt_result.update("Impossibile creare la stringa: Operazione annullata")
            return
        
        data = ""
        if rename_string:
            data = self.arb_data.pop(rename_string)
            
        self.arb_data[string_key] = data
        
        self.reset_list()
            
        
        pass
    
    def rename_string(self) -> None:
        selected_strings = self.lbx_strings.get()
        
        if not selected_strings or len(selected_strings) == 0:
            self.txt_result.update("Impossibile rinominare la stringa: Nessuna stringa selezionata")
            return
        
        self.add_string(selected_strings[0])

if __name__ == "__main__":
    app = App()
    app.start()
