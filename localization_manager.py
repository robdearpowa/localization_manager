import os
import json
import PySimpleGUI as gui

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

        menu_layout = [
            ["&File", ['&Apri File ARB::-MENUOPEN-', '&Salva::-MENUSAVE-', 'Salva come...::-MENUSAVEAS-']]
        ]

        self.layout: list[list] = [
            [gui.Menu(menu_layout)],
            [gui.Text("Cerca")],
            [gui.Input(key="-INPSEARCH-", enable_events=True, expand_x=True)],
            [gui.Listbox([], key="-LBXSTRINGS-", expand_y=True, expand_x=False, enable_events=True, horizontal_scroll=True, size=(40, None)), 
             gui.Multiline(key="-MTLCURRENTSTRING-", expand_x=True, expand_y=True, enable_events=True,)],
            [gui.Text("Seleziona il file di lingue", key="-TXTRESULT-")],
        ]

        self.window: gui.Window = gui.Window(
            "Gestore Localizzazione",
            layout=self.layout,
            resizable=True,
        )

        self.window.finalize()

        w, h = self.window.size

        self.window.set_min_size((w, 400))

        # Valorizzazione componenti

        self.lbx_strings: gui.Listbox = self.window["-LBXSTRINGS-"] #type: ignore
        self.inp_current_string: gui.Multiline = self.window["-MTLCURRENTSTRING-"] #type: ignore
        self.inp_search: gui.Input = self.window["-INPSEARCH-"] #type: ignore
        self.txt_result: gui.Text = self.window["-TXTRESULT-"]

        repack(self.lbx_strings.Widget,        'y', 0)
        repack(self.lbx_strings.Widget.master, 'y', 0, self.inp_current_string.Widget.master)
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
                                       default_path=self.current_arbfile_path,
                                       keep_on_top=True)
        
        if not file_path:
            return
        
        self.current_arbfile_path = file_path
        self.txt_result.update("Aprendo file... {self.current_arbfile_path}")
        self.load_arbfile(self.current_arbfile_path)
        
        self.txt_result.update(f"Aperto file: {self.current_arbfile_path}")

        pass
    
    def save_arbfile(self, file_path: Union[str, None]) -> None:
        if not file_path or not self.arb_data:
            return
        
        self.txt_result.update("Salvando file... {file_path}")
        with open(file_path, "w+") as arbfile:
            json.dump(self.arb_data, arbfile)
            self.txt_result.update(f"Salvato file: {file_path}")
        pass
            
    def save_arbfile_as(self) -> None:
        file_path = gui.popup_get_file("Salva il File di Localizzazione",
                                       file_types=ARB_FILETYPE,
                                       default_path=self.current_arbfile_path,
                                       save_as=True,
                                       keep_on_top=True)
        
        if not file_path:
            return
        
        self.current_arbfile_path = file_path
        self.save_arbfile(self.current_arbfile_path)
        pass
        

    def get_arbfile_path(self) -> Union[str, None]:
        file_path: str = self.inp_arbfile.get()
        return file_path

    def get_arbfile(self, file_path: Union[str, None]) -> Union[dict, None]:
        if not file_path:
            return None

        file_exist = os.path.isfile(file_path)

        if not file_exist:
            return None

        with open(file_path) as arbfile:
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

if __name__ == "__main__":
    app = App()
    app.start()
