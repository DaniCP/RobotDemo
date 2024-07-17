import FreeSimpleGUI as sg
import threading
import queue

class Calculator:
    BUTTONS = '1234567890+-*/C='

    def __init__(self):
        self._expression = ''
        self.gui_running = False
        self.gui_end_cmd = False
        self.event_queue = queue.Queue()

        # Layout for the calculator
        self.layout = [
            [sg.Text('', size=(20, 1), key='-DISPLAY-', justification='right')],
            [sg.Button('1'), sg.Button('2'), sg.Button('3'), sg.Button('+')],
            [sg.Button('4'), sg.Button('5'), sg.Button('6'), sg.Button('-')],
            [sg.Button('7'), sg.Button('8'), sg.Button('9'), sg.Button('*')],
            [sg.Button('0'), sg.Button('C'), sg.Button('/'), sg.Button('=')],
        ]

    def _run_gui_backend(self):
        # Create the window
        self.window = sg.Window('Calculadora', self.layout)

        # Event loop to process "events" and get the "values" of the inputs
        while not self.gui_end_cmd:
            event, values = self.window.read(timeout=100)
            if event == sg.WIN_CLOSED:
                break

            # If event is from GUI, put it in the queue
            if event in self.BUTTONS:
                self.event_queue.put(event)

            # Process events from the queue
            while not self.event_queue.empty():
                event = self.event_queue.get()
                try:
                    display = self._process_event(event)
                    self.window['-DISPLAY-'].update(display)
                except CalculationError as e:
                    self.window['-DISPLAY-'].update(str(e))
                    self._expression = ''  # Reset expression after an error

        self.window.close()

    def show_gui(self):
        # Start the GUI in a separate thread
        self.gui_thread = threading.Thread(target=self._run_gui_backend)
        self.gui_thread.start()
        self.gui_end_cmd = False
        self.gui_running = True


    def push(self, button):
        if button not in self.BUTTONS:
            raise CalculationError("Invalid button '%s'." % button)
        # Put the event in the queue for the GUI to process
        self.event_queue.put(button)
        # If no gui process the queued event here
        if not self.gui_running:
            event = self.event_queue.get()
            display = self._process_event(event)
        while not self.event_queue.empty():
            pass
        return self._expression

    def _process_event(self, button):
        if button == '=':
            self._expression = self._calculate(self._expression)
        elif button == 'C':
            self._expression = ''
        elif button == '/':
            self._expression += '//'
        else:
            self._expression += button
        return self._expression

    def _calculate(self, expression):
        try:
            return str(eval(expression))
        except SyntaxError:
            raise CalculationError('Invalid expression.')
        except ZeroDivisionError:
            raise CalculationError('Division by zero.')

class CalculationError(Exception):
    pass

if __name__ == "__main__":
    # Create an instance of the Calculator class
    calc = Calculator()

    # Show the GUI
    calc.show_gui()

    # Example of pushing buttons from the model
    import time
    time.sleep(2)
    calc.push('1')
    time.sleep(1)
    calc.push('+')
    time.sleep(1)
    calc.push('2')
    time.sleep(1)
    calc.push('=')

    calc.gui_end_cmd = True