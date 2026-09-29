import tkinter as tk
from tkinter import ttk, messagebox

from alpaca.dome import Dome
from alpaca.exceptions import InvalidOperationException, ValueNotSetException


ALPACA_IP = "localhost:5000"
DEVICE_NUM = 0


shutterStateLabels = {
    0: "Abierta",
    1: "Cerrada",
    2: "Abriendo",
    3: "Cerrando",
    4: "Error"
}

flapStatusLabels = {
    0: "Arriba",
    1: "Abajo",
    3: "Error"
}


class DomeGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Control de Domo")
        self.root.geometry("600x300")
        self.root.minsize(600, 300)

        self.dome = Dome(ALPACA_IP, DEVICE_NUM)
        self.connected = False

        self.create_widgets()
        self.update_status()

    # ============================================================
    # INTERFAZ
    # ============================================================

    def create_widgets(self):

        # --------------------------------------------------------
        # BLOQUE 1: CONEXIÓN + ESTADO
        # --------------------------------------------------------

        top_frame = ttk.LabelFrame(
            self.root,
            text="Conexión y estado"
        )

        top_frame.pack(
            fill="x",
            padx=10,
            pady=(10, 5)
        )

        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=1)

        connection_frame = ttk.Frame(top_frame)

        connection_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=10,
            pady=15
        )

        connection_frame.columnconfigure(0, weight=1)

        self.conn_label = ttk.Label(
            connection_frame,
            text="Desconectado"
        )

        self.conn_label.grid(
            row=0,
            column=0,
            pady=(5, 10)
        )

        self.connect_button = ttk.Button(
            connection_frame,
            text="Conectar",
            command=self.toggle_connection
        )

        self.connect_button.grid(
            row=1,
            column=0
        )

        status_frame = ttk.Frame(top_frame)

        status_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=10,
            pady=15
        )

        status_frame.columnconfigure(0, weight=1)
        status_info = ttk.Frame(status_frame)

        status_info.grid(
            row=0,
            column=0
        )

        self.az_label = ttk.Label(
            status_info,
            text="Acimut: ---"
        )

        self.az_label.grid(
            row=0,
            column=0,
            sticky="w",
            pady=2
        )

        self.shutter_label = ttk.Label(
            status_info,
            text="Cortina: ---"
        )

        self.shutter_label.grid(
            row=1,
            column=0,
            sticky="w",
            pady=2
        )

        self.flap_label = ttk.Label(
            status_info,
            text="Gajo: ---"
        )

        self.flap_label.grid(
            row=2,
            column=0,
            sticky="w",
            pady=2
        )

        self.error_label = ttk.Label(
            status_info,
            text="Estado: Sin errores",
            wraplength=260
        )

        self.error_label.grid(
            row=3,
            column=0,
            sticky="w",
            pady=2
        )

        self.clear_error_button = ttk.Button(
            status_frame,
            text="Limpiar error",
            command=self.clear_error
        )

        self.clear_error_button.grid(
            row=1,
            column=0,
            pady=(8, 0)
        )

        # --------------------------------------------------------
        # BLOQUE 2: ACCIONES DE MOVIMIENTO
        # --------------------------------------------------------

        movement_frame = ttk.LabelFrame(
            self.root,
            text="Acciones de movimiento"
        )

        movement_frame.pack(
            fill="x",
            padx=10,
            pady=5
        )

        for column in range(5):
            movement_frame.columnconfigure(
                column,
                weight=1
            )

        # --------------------------------------------------------
        # Ir a acimut
        # --------------------------------------------------------

        az_frame = ttk.Frame(movement_frame)

        az_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=10,
            pady=10
        )

        az_control = ttk.Frame(az_frame)

        az_control.pack(
            expand=True
        )

        self.az_entry = ttk.Entry(
            az_control,
            width=8
        )

        self.az_entry.pack(
            side="left"
        )

        ttk.Button(
            az_control,
            text="Ir",
            command=self.slew_to_az
        ).pack(
            side="left",
            padx=(5, 0)
        )

        
        # --------------------------------------------------------
        # Abortar movimiento
        # --------------------------------------------------------

        abort_frame = ttk.Frame(movement_frame)

        abort_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=10,
            pady=10
        )

        self.abort_canvas = tk.Canvas(
            abort_frame,
            width=46,
            height=46,
            highlightthickness=0
        )

        self.abort_canvas.pack(
            expand=True
        )

        self.abort_canvas.create_oval(
            5,
            5,
            41,
            41,
            fill="#d32f2f",
            outline="#b71c1c",
            width=1,
            tags="abort"
        )

        self.abort_canvas.create_rectangle(
            19,
            19,
            27,
            27,
            fill="white",
            outline="white",
            tags="abort"
        )

        self.abort_canvas.tag_bind(
            "abort",
            "<Button-1>",
            lambda event: self.abort_slew()
        )

        # --------------------------------------------------------
        # Home + Park
        # --------------------------------------------------------

        home_park_frame = ttk.Frame(movement_frame)

        home_park_frame.grid(
            row=0,
            column=2,
            sticky="nsew",
            padx=10,
            pady=10
        )

        home_park_frame.columnconfigure(
            0,
            weight=1
        )

        ttk.Button(
            home_park_frame,
            text="Ir a Home",
            command=self.find_home
        ).pack(
            pady=(0, 4)
        )

        ttk.Button(
            home_park_frame,
            text="Park",
            command=self.park
        ).pack()

        # --------------------------------------------------------
        # Cortina
        # --------------------------------------------------------

        shutter_frame = ttk.Frame(movement_frame)

        shutter_frame.grid(
            row=0,
            column=3,
            sticky="nsew",
            padx=10,
            pady=10
        )

        self.shutter_button = ttk.Button(
            shutter_frame,
            text="Abrir cortina",
            command=self.toggle_shutter
        )

        self.shutter_button.pack(
            expand=True
        )

        # --------------------------------------------------------
        # Abrir sin gajo
        # --------------------------------------------------------

        special_frame = ttk.Frame(movement_frame)

        special_frame.grid(
            row=0,
            column=4,
            sticky="nsew",
            padx=10,
            pady=10
        )

        ttk.Button(
            special_frame,
            text="Abrir sin gajo",
            command=self.open_without_flap
        ).pack(
            expand=True
        )


    # ============================================================
    # CONEXIÓN
    # ============================================================

    def toggle_connection(self):
        if self.connected:
            self.disconnect()
        else:
            self.connect()

    def connect(self):
        try:
            self.dome.Connected = True
            self.connected = True

            self.conn_label.config(
                text="Conectado"
            )

            self.connect_button.config(
                text="Desconectar"
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                str(e)
            )

    def disconnect(self):
        try:
            self.dome.Connected = False
            self.connected = False

            self.conn_label.config(
                text="Desconectado"
            )

            self.connect_button.config(
                text="Conectar"
            )

            # Limpiar valores mostrados
            self.az_label.config(
                text="Acimut: ---"
            )

            self.shutter_label.config(
                text="Cortina: ---"
            )

            self.flap_label.config(
                text="Gajo: ---"
            )

            self.error_label.config(
                text="Estado: Sin errores"
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                str(e)
            )

    # ============================================================
    # FUNCIONES ASCOM
    # ============================================================

    def toggle_shutter(self):
        if not self.connected:
            messagebox.showwarning(
                "Aviso",
                "Domo no conectado"
            )
            return

        try:
            status = self.dome.ShutterStatus

            if status == 1:
                self.dome.OpenShutter()

            elif status == 0:
                self.dome.CloseShutter()

            else:
                messagebox.showwarning(
                    "Aviso",
                    "La cortina está en movimiento o en estado de error."
                )

        except Exception as e:
            self.show_error(str(e))

    def open_shutter(self):
        self.safe_call(
            self.dome.OpenShutter
        )

    def close_shutter(self):
        self.safe_call(
            self.dome.CloseShutter
        )

    def find_home(self):
        self.safe_call(
            self.dome.FindHome
        )

    def park(self):
        self.safe_call(
            self.dome.Park
        )

    def slew_to_az(self):
        try:
            az = float(
                self.az_entry.get()
            )

            if az < 0 or az >= 360:
                messagebox.showerror(
                    "Error",
                    "El acimut debe estar entre 0 y 359.99 grados."
                )
                return

            self.safe_call(
                lambda: self.dome.SlewToAzimuth(az)
            )

        except ValueError:
            messagebox.showerror(
                "Error",
                "Acimut inválido"
            )

    # ============================================================
    # FUNCIONES PERSONALIZADAS
    # ============================================================

    def open_without_flap(self):
        self.safe_call(
            lambda: self.dome.Action(
                "openwithoutflap",
                ""
            )
        )

    def get_flap_status(self):
        try:
            status = self.dome.Action(
                "getflapstatus",
                ""
            )

            self.flap_label.config(
                text=f"Gajo: {flapStatusLabels.get(status, 'Desconocido')}"
            )

        except Exception as e:
            print(
                f"Excepción al consultar estado del gajo: {e}"
            )

    def get_error(self):
        try:
            return self.dome.Action(
                "geterror",
                ""
            )

        except Exception as e:
            print(
                f"Excepción al consultar error: {e}"
            )
            return None

    def clear_error(self):
        if not self.connected:
            messagebox.showwarning(
                "Aviso",
                "Domo no conectado"
            )
            return

        try:
            self.dome.Action(
                "clearerror",
                ""
            )

        except Exception as e:
            self.show_error(
                str(e)
            )

    # ============================================================
    # ERROR
    # ============================================================

    def update_error_status(self):
        result = self.get_error()

        if result is None:
            return

        error = result.get(
            "Error",
            False
        )

        error_number = result.get(
            "ErrorNumber",
            0
        )

        error_message = result.get(
            "ErrorMessage",
            ""
        )

        if error:

            if error_message:
                text = (
                    f"ERROR {error_number}: "
                    f"{error_message}"
                )
            else:
                text = (
                    f"ERROR {error_number}"
                )

            self.error_label.config(
                text=text
            )

        else:
            self.error_label.config(
                text="Estado: Sin errores"
            )

    def show_error(self, message):
        self.error_label.config(
            text=f"ERROR: {message}"
        )

        messagebox.showerror(
            "Error",
            message
        )

    # ============================================================
    # UTILIDADES
    # ============================================================

    def safe_call(self, func):

        if not self.connected:
            messagebox.showwarning(
                "Aviso",
                "Domo no conectado"
            )
            return

        try:
            func()

        except Exception as e:
            self.show_error(
                str(e)
            )

    # ============================================================
    # ACTUALIZACIÓN DE ESTADO
    # ============================================================

    def update_status(self):

        # Volver a ejecutar en 1 segundo
        self.root.after(
            1000,
            self.update_status
        )

        if not self.connected:
            return

        # --------------------------------------------------------
        # Acimut
        # --------------------------------------------------------

        try:
            azimuth = self.dome.Azimuth

            self.az_label.config(
                text=f"Acimut: {azimuth:.2f}°"
            )

        except InvalidOperationException:
            self.az_label.config(
                text="Acimut: Offline"
            )

        except ValueNotSetException:
            self.az_label.config(
                text="Acimut: Offline"
            )

        except Exception as e:
            print(
                f"Excepción al consultar Azimuth: {e}"
            )

            self.az_label.config(
                text="Acimut: Error"
            )

        # --------------------------------------------------------
        # Cortina
        # --------------------------------------------------------

        try:
            shutter_status = self.dome.ShutterStatus

            self.shutter_label.config(
                text=(
                    "Cortina: "
                    f"{shutterStateLabels.get(
                        shutter_status,
                        "Desconocida"
                    )}"
                )
            )

            if shutter_status == 0:
                self.shutter_button.config(
                    text="Cerrar cortina",
                    state="normal"
                )
            elif shutter_status == 1:
                self.shutter_button.config(
                    text="Abrir cortina",
                    state="normal"
                )
            else:
                self.shutter_button.config(
                    state="disabled"
                )

        except InvalidOperationException:
            self.shutter_label.config(
                text="Cortina: Offline"
            )

        except ValueNotSetException:
            self.shutter_label.config(
                text="Cortina: Offline"
            )

        except Exception as e:
            print(
                f"Excepción al consultar ShutterStatus: {e}"
            )

            self.shutter_label.config(
                text="Cortina: Error"
            )

        self.get_flap_status()

        # --------------------------------------------------------
        # Error
        # --------------------------------------------------------

        self.update_error_status()

    # ============================================================
    # ABORTAR MOVIMIENTO
    # ============================================================

    def abort_slew(self):

        if not self.connected:
            messagebox.showwarning(
                "Aviso",
                "Domo no conectado"
            )
            return

        try:
            self.dome.AbortSlew()

        except Exception as e:
            self.show_error(
                str(e)
            )


if __name__ == "__main__":

    root = tk.Tk()

    app = DomeGUI(root)

    root.mainloop()
