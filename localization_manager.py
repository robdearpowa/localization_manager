import os
import json
import PySimpleGUI as gui

from typing import Union


class App:
    def __init__(self) -> None:
        self.running: bool = False
        self.arb_data: Union[dict, None] = None

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

        self.layout: list[list] = [
            [gui.Text("Seleziona il file di lingue")],
            [gui.Input(key="-INPARBFILE-", 
                       expand_x=True, 
                       readonly=True, 
                       disabled_readonly_background_color=input_background, 
                       enable_events=True),
             gui.FileBrowse(target="-INPARBFILE-",
                            enable_events=True,
                            file_types=(("File di localizzazione", "*.arb"),)),],
            [gui.Listbox([], key="-LBXSTRINGS-", expand_y=True, expand_x=False, enable_events=True, size=(30, None), horizontal_scroll=True), 
             gui.Multiline(key="-MTLCURRENTSTRING-", expand_x=True, expand_y=True, enable_events=True)]
        ]

        self.window: gui.Window = gui.Window(
            "Gestore Localizzazione",
            layout=self.layout,
            resizable=True,
        )

        self.window.finalize()

        w, h = self.window.size

        self.window.set_min_size((w, 300))

        # Valorizzazione componenti

        
        self.inp_arbfile: gui.Input = self.window["-INPARBFILE-"] # type: ignore
        self.lbx_strings: gui.Listbox = self.window["-LBXSTRINGS-"] #type: ignore
        self.inp_current_string: gui.Multiline = self.window["-MTLCURRENTSTRING-"] #type: ignore
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

                if event == self.inp_arbfile.key:
                    self.load_arbfile()

                if event == self.lbx_strings.key:
                    self.load_current_string(values[event])

                if event == self.inp_current_string.key:
                    self.save_current_string(values[self.lbx_strings.key], values[event])
        pass

    def get_arbfile_path(self) -> Union[str, None]:
        file_path: str = self.inp_arbfile.get()
        return file_path

    def get_arbfile(self) -> Union[dict, None]:
        file_path = self.get_arbfile_path()

        if not file_path:
            return None

        file_exist = os.path.isfile(file_path)

        if not file_exist:
            return None

        with open(file_path) as arbfile:
            arbfile_content: dict = json.load(arbfile)
            return arbfile_content

    def load_arbfile(self) -> None:
        self.arb_data = self.get_arbfile()

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


if __name__ == "__main__":
    app = App()
    app.start()
