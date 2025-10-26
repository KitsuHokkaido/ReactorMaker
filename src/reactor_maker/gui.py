import tkinter as tk
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showinfo

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from .core import ReactorMaker
from .vector.vector import vector2, vector3


class Application:
    def __init__(self):
        self._window = tk.Tk()
        self._window.title("Reactor Maker")
        self._window.geometry("1000x600")
        self._style = ttk.Style("solar")

        self._generate_menu()

        self._lframe = ttk.Frame(self._window, padding=10)
        self._lframe.pack(side=LEFT, fill=Y, padx=10, pady=10)

        self._rframe = ttk.Frame(self._window, padding=10)
        self._rframe.pack(side=RIGHT, fill=BOTH, expand=True, padx=10, pady=10)

        self._generate_parameters_widget()

        button_frame = ttk.Frame(self._lframe)
        button_frame.pack(side=BOTTOM, fill=X, pady=5)

        self._reset_button = ttk.Button(
            button_frame, text="Reset", bootstyle="secondary", command=self._on_reset
        )
        self._generate_button = ttk.Button(
            button_frame,
            text="Generate",
            bootstyle="success",
            command=self._on_generate,
        )

        self._generate_button.pack(side=RIGHT, padx=5)
        self._reset_button.pack(side=RIGHT, padx=5)

        self._generate_output_widget()

        self._mesh = None

    def _generate_menu(self):
        self._menu = ttk.Menu(self._window)
        self._window.config(menu=self._menu)

        self._file_menu = ttk.Menu(self._menu)
        self._menu.add_cascade(label="File", menu=self._file_menu)
        self._file_menu.add_command(label="New", command=self._on_reset)
        self._file_menu.add_command(label="Save As", command=self._on_save_as)
        self._file_menu.add_separator()
        self._file_menu.add_command(label="Exit", command=self._window.quit)

        self._mesh_menu = ttk.Menu(self._menu)
        self._menu.add_cascade(label="Mesh", menu=self._mesh_menu)
        self._mesh_menu.add_command(label="Generate", command=self._on_generate)

        self._about_menu = ttk.Menu(self._menu)
        self._menu.add_cascade(label="About", menu=self._about_menu)
        self._about_menu.add_command(label="About", command=self._on_about)

    def _generate_parameters_widget(self):
        # ---------------------- Geometry Frame -----------------------
        geometry_frame = ttk.LabelFrame(self._lframe, text="Geometry")
        geometry_frame.pack(side=TOP, fill=X)

        ttk.Label(
            geometry_frame, text="Reactor dimensions", font=("Helvetica", 10, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky=W, padx=5, pady=5)
        ttk.Label(geometry_frame, text="Center position").grid(
            row=1, column=0, padx=5, pady=5, sticky=W
        )
        self._center_entry = ttk.Entry(geometry_frame)
        self._center_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(geometry_frame, text="Radius").grid(
            row=2, column=0, padx=5, pady=5, sticky=W
        )
        self._reactor_radius_entry = ttk.Entry(geometry_frame)
        self._reactor_radius_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(geometry_frame, text="Height").grid(
            row=3, column=0, padx=5, pady=5, sticky=W
        )
        self._reactor_height_entry = ttk.Entry(geometry_frame)
        self._reactor_height_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(geometry_frame, text="Square mesh size").grid(
            row=4, column=0, padx=5, pady=5, sticky=W
        )
        self._per_squarre_entry = ttk.Entry(geometry_frame)
        self._per_squarre_entry.grid(row=4, column=1, padx=5, pady=5)

        ttk.Separator(geometry_frame, orient=HORIZONTAL).grid(
            row=5, column=0, columnspan=2, sticky=EW, pady=15, padx=10
        )

        ttk.Label(
            geometry_frame, text="Chimney dimensions", font=("Helvetica", 10, "bold")
        ).grid(row=6, column=0, columnspan=2, sticky=W, padx=5, pady=5)
        ttk.Label(geometry_frame, text="Width").grid(
            row=7, column=0, padx=5, pady=5, sticky=W
        )
        self._chimney_width_entry = ttk.Entry(geometry_frame)
        self._chimney_width_entry.grid(row=7, column=1, padx=5, pady=5)

        ttk.Label(geometry_frame, text="Height").grid(
            row=8, column=0, padx=5, pady=5, sticky=W
        )
        self._chimney_height_entry = ttk.Entry(geometry_frame)
        self._chimney_height_entry.grid(row=8, column=1, padx=5, pady=5)

        ttk.Label(geometry_frame, text="").grid(row=9, column=1, columnspan=2)

        geometry_frame.columnconfigure(1, weight=1)

        # ---------------------- Meshing Frame --------------------------
        meshing_frame = ttk.LabelFrame(self._lframe, text="Meshing")
        meshing_frame.pack(fill=X, pady=15)

        ttk.Label(meshing_frame, text="Characteritics mesh size").grid(
            row=0, column=0, padx=5, pady=5
        )
        self._mesh_size_entry = ttk.Entry(meshing_frame)
        self._mesh_size_entry.grid(row=0, column=1, padx=10, pady=10)

        meshing_frame.columnconfigure(1, weight=1)

    def _generate_output_widget(self):
        self._tabs = ttk.Notebook(self._rframe)
        self._tabs.pack(fill=BOTH, expand=YES)

        self._tabs.add(
            child=ttk.Label(self._tabs, text="Showing mesh computed"), text="Mesh 1"
        )

        ttk.Label(self._rframe, text="Outputs :").pack(anchor=W, pady=5)

        self._outputs = ttk.ScrolledText(self._rframe, height=2)
        self._outputs.pack(fill=BOTH, expand=YES)

    def _on_reset(self):
        self._center_entry.delete(0, END)
        self._reactor_radius_entry.delete(0, END)
        self._reactor_height_entry.delete(0, END)
        self._per_squarre_entry.delete(0, END)
        self._chimney_width_entry.delete(0, END)
        self._chimney_height_entry.delete(0, END)
        self._mesh_size_entry.delete(0, END)

    def _on_generate(self):
        center = self._center_entry.get()
        radius = self._reactor_radius_entry.get()
        height = self._reactor_height_entry.get()
        per_squarre = self._per_squarre_entry.get()
        chimney_w = self._chimney_width_entry.get()
        chimney_h = self._chimney_height_entry.get()
        mesh_size = self._mesh_size_entry.get()

        self._outputs.insert(END, f"\n--- Generation started ---\n\n")
        self._outputs.insert(END, f"Center: {center}\n")
        self._outputs.insert(END, f"Reactor radius: {radius}\n")
        self._outputs.insert(END, f"Reactor height: {height}\n")
        self._outputs.insert(END, f"Reactor per_squarre: {per_squarre}\n")
        self._outputs.insert(END, f"Chimney width: {chimney_w}\n")
        self._outputs.insert(END, f"Chimney height: {chimney_h}\n")
        self._outputs.insert(END, f"Mesh size: {mesh_size}\n")

        self._outputs.see(END)

        maker = ReactorMaker()

        center = center.split(";")

        geometry = maker.create_geometry(
            center=vector3(float(center[0]), float(center[1]), float(center[2])),
            reactor_dim=vector2(float(radius), float(height)),
            chimney_dim=vector2(float(chimney_w), float(chimney_h)),
            per_square=float(per_squarre),
            mesh_size=float(mesh_size),
        ).unwrap()

        self._mesh = maker.mesh(geometry).unwrap()

        self._outputs.insert(END, f"\nMesh succesfully computed !\n")

        showinfo(title="Info", message="Mesh computed !")

    def _on_save_as(self):
        if self._mesh is None:
            return

        filename = asksaveasfilename(title="Save As", defaultextension=".unv",)

        if self._mesh.export_to(filename):
            self._outputs.insert(END, f"\nMesh succesfully saved !\n")
            showinfo(title="Info", message="File saved !")

    def _on_about(self):
        showinfo(title="About", message="Reactor Maker\nv1.0.0")

    def run(self):
        self._window.mainloop()


def main():
    application = Application()
    application.run()


if __name__ == "__main__":
    main()
