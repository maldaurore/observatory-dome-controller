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
        self.root.geometry("420x700")

        self.dome = Dome(ALPACA_IP, DEVICE_NUM)
        self.connected = False

        self.create_widgets()
        self.update_status()

    def create_widgets(self):

        # Conexión
        conn_frame = ttk.LabelFrame(
            self.root,
            text="Conexión"
        )
        conn_frame.pack(
            fill="x",
            padx=10,
            pady=5
        )

        self.conn_label = ttk.Label(
            conn_frame,
            text="Desconectado"
        )
        self.conn_label.pack(pady=5)

        ttk.Button(
            conn_frame,
            text="Conectar",
            command=self.connect
        ).pack(pady=2)

        ttk.Button(
            conn_frame,
            text="Desconectar",
            command=self.disconnect
        ).pack(pady=2)

        # Estado
        status_frame = ttk.LabelFrame(
            self.root,
            text="Estado"
        )
        status_frame.pack(
            fill="x",
            padx=10,
            pady=5
        )

        self.az_label = ttk.Label(
            status_frame,
            text="Azimut: ---"
        )
        self.az_label.pack()

        self.shutter_label = ttk.Label(
            status_frame,
            text="Cortina: ---"
        )
        self.shutter_label.pack()

        self.flap_label = ttk.Label(
            status_frame,
            text="Gajo: ---"
        )
        self.flap_label.pack()

        self.slave_label = ttk.Label(
            status_frame,
            text="Slaved: ---"
        )
        self.slave_label.pack()

        self.error_label = ttk.Label(
            status_frame,
            text="Estado: Sin errores",
            wraplength=380
        )
        self.error_label.pack(pady=5)

        ttk.Button(
            status_frame,
            text="Limpiar error",
            command=self.clear_error
        ).pack(pady=3)

        # Control de azimut
        az_frame = ttk.LabelFrame(
            self.root,
            text="Control de Azimut"
        )
        az_frame.pack(
            fill="x",
            padx=10,
            pady=5
        )

        self.az_entry = ttk.Entry(az_frame)
        self.az_entry.pack(pady=5)

        ttk.Button(
            az_frame,
            text="Girar a azimut",
            command=self.slew_to_az
        ).pack(pady=5)

        # Acciones principales
        main_frame = ttk.LabelFrame(
            self.root,
            text="Acciones principales"
        )
        main_frame.pack(
            fill="x",
            padx=10,
            pady=5
        )

        ttk.Button(
            main_frame,
            text="Find Home",
            command=self.find_home
        ).pack(
            fill="x",
            pady=2
        )

        ttk.Button(
            main_frame,
            text="Park",
            command=self.park
        ).pack(
            fill="x",
            pady=2
        )

        # Shutter
        shutter_frame = ttk.LabelFrame(
            self.root,
            text="Control de Shutter"
        )
        shutter_frame.pack(
            fill="x",
            padx=10,
            pady=5
        )

        ttk.Button(
            shutter_frame,
            text="Abrir",
            command=self.open_shutter
        ).pack(
            fill="x",
            pady=2
        )

        ttk.Button(
            shutter_frame,
            text="Cerrar",
            command=self.close_shutter
        ).pack(
            fill="x",
            pady=2
        )

        # Funciones especiales
        special_frame = ttk.LabelFrame(
            self.root,
            text="Funciones especiales"
        )
        special_frame.pack(
            fill="x",
            padx=10,
            pady=5
        )

        ttk.Button(
            special_frame,
            text="Abrir sin gajo",
            command=self.open_without_flap
        ).pack(
            fill="x",
            pady=2
        )

        ttk.Button(
            special_frame,
            text="Obtener estado del gajo",
            command=self.get_flap_status
        ).pack(
            fill="x",
            pady=2
        )

        # Modo Slaved
        slave_frame = ttk.LabelFrame(
            self.root,
            text="Modo Slaved"
        )
        slave_frame.pack(
            fill="x",
            padx=10,
            pady=5
        )

        self.slave_var = tk.BooleanVar()

        ttk.Checkbutton(
            slave_frame,
            text="Slaved",
            variable=self.slave_var,
            command=self.toggle_slave
        ).pack()

        # Abortar movimiento
        abort_frame = ttk.LabelFrame(
            self.root,
            text="Abortar movimiento"
        )
        abort_frame.pack(
            fill="x",
            padx=10,
            pady=5
        )

        ttk.Button(
            abort_frame,
            text="Abortar movimiento",
            command=self.abort_slew
        ).pack()

    # Conexión

    def connect(self):
        try:
            self.dome.Connected = True
            self.connected = True
            self.conn_label.config(text="Conectado")

        except Exception as e:
            messagebox.showerror(
                "Error",
                str(e)
            )

    def disconnect(self):
        try:
            self.dome.Connected = False
            self.connected = False
            self.conn_label.config(text="Desconectado")

        except Exception as e:
            messagebox.showerror(
                "Error",
                str(e)
            )

    # Funciones ASCOM

    def open_shutter(self):
        self.safe_call(self.dome.OpenShutter)

    def close_shutter(self):
        self.safe_call(self.dome.CloseShutter)

    def find_home(self):
        self.safe_call(self.dome.FindHome)

    def park(self):
        self.safe_call(self.dome.Park)

    def slew_to_az(self):
        try:
            az = float(self.az_entry.get())

            self.safe_call(
                lambda: self.dome.SlewToAzimuth(az)
            )

        except ValueError:
            messagebox.showerror(
                "Error",
                "Azimut inválido"
            )

    def toggle_slave(self):
        self.safe_call(
            lambda: setattr(
                self.dome,
                "Slaved",
                self.slave_var.get()
            )
        )

    # Funciones personalizadas

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
                text=f"Gajo: {flapStatusLabels[status]}"
            )

        except Exception as e:
            self.show_error(str(e))

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
            self.show_error(str(e))

    # Error

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
                text = f"ERROR {error_number}"

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

    # Utilidades

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
            self.show_error(str(e))

    # Actualización de estado

    def update_status(self):

        self.root.after(
            1000,
            self.update_status
        )

        if not self.connected:
            return

        properties = [
            (
                "Azimuth",
                self.az_label,
                "Azimut: {:.2f}",
                "Azimut"
            ),
            (
                "ShutterStatus",
                self.shutter_label,
                "Cortina: {}",
                "Cortina"
            ),
            (
                "Slaved",
                self.slave_label,
                "Slaved: {}",
                "Slaved"
            )
        ]

        for attr, label, fmt, name in properties:

            try:

                value = getattr(
                    self.dome,
                    attr
                )

                if attr == "ShutterStatus":

                    label.config(
                        text=fmt.format(
                            shutterStateLabels[value]
                        )
                    )

                else:

                    label.config(
                        text=fmt.format(value)
                    )

            except InvalidOperationException:

                label.config(
                    text=f"{name}: Offline"
                )

            except ValueNotSetException:

                label.config(
                    text=f"{name}: Offline"
                )

            except Exception as e:

                print(
                    f"Excepción al consultar "
                    f"{attr}: {e}"
                )

                label.config(
                    text=f"{attr}: Error"
                )

        self.update_error_status()

    def abort_slew(self):

        if self.connected:

            try:
                self.dome.AbortSlew()

            except Exception as e:
                self.show_error(str(e))


if __name__ == "__main__":

    root = tk.Tk()

    app = DomeGUI(root)

    root.mainloop()

