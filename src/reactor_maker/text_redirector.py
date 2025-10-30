from ttkbootstrap.constants import END

class TextRedirector:
    def __init__(self, widget):
        self._widget = widget
    
    def write(self, text):
        self._widget.insert(END, text)
        self._widget.see(END)

    def flush(self):
        pass
