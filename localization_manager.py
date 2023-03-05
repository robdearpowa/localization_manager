import PySimpleGUI as gui


class App:
    def __init__(self):
        self.running: bool = False

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
            [gui.Input(key="-ARBFILE-", expand_x=True, readonly=True, disabled_readonly_background_color=input_background), gui.FileBrowse(target="-ARBFILE-", file_types=(("File di localizzazione", "*.arb"),))],
        ]

        self.window: gui.Window = gui.Window(
            "Gestore Localizzazione",
            layout=self.layout,
            resizable=True,
            finalize=True,
        )

        current_size = self.window.size

        self.window.set_min_size(current_size)

        pass

    def start(self):
        self.running = True
        print("Running")

        while self.running:
            data = self.window.read()
            if data:
                event, values = data

                if event == gui.WIN_CLOSED or event == "Cancel":
                    self.running = False

        pass


if __name__ == "__main__":
    app = App()
    app.start()
