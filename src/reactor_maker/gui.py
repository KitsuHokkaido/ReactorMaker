import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showinfo, showwarning

import yaml
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from typing import Dict, Optional, List

from .engine import ReactorMaker
from .vector import vector2, vector3


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

        self._per_square_var = tk.StringVar(value="0.50")
        self._per_curvature_var = tk.StringVar(value="0.10")

        self._generate_parameters_widget()

        button_frame = ttk.Frame(self._lframe)
        button_frame.pack(side=BOTTOM, fill=X, pady=5)

        self._optimize_var = ttk.IntVar()

        self._optimize_button = ttk.Checkbutton(
            self._lframe, text="Optimize mesh (beta)", variable=self._optimize_var
        )
        self._optimize_button.pack(side=LEFT, padx=5)
        self._optimize_button.invoke()
        self._optimize_button.invoke()

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
        self._file_menu.add_command(label="New", command=self._on_reset)
        self._file_menu.add_command(label="Open", command=self._on_open)
            
        self._file_menu.add_separator()
        
        self._save_menu = ttk.Menu(self._menu)
        self._save_menu.add_command(label="YAML", command=self._on_yaml)
        self._save_menu.add_command(label="TOML", command=self._on_toml)
        self._file_menu.add_cascade(label="Save As", menu=self._save_menu)

        self._file_menu.add_separator()
        self._file_menu.add_command(label="Exit", command=self._window.quit)
        self._menu.add_cascade(label="File", menu=self._file_menu)

        self._mesh_menu = ttk.Menu(self._menu)
        self._mesh_menu.add_command(label="Generate", command=self._on_generate)
        self._export_mesh_menu = ttk.Menu(self._menu)
        self._export_mesh_menu.add_command(label="UNV", command=self._on_export_unv)
        self._mesh_menu.add_cascade(label="Export", menu=self._export_mesh_menu)
        self._menu.add_cascade(label="Mesh", menu=self._mesh_menu)

        self._geometry_menu = ttk.Menu(self._menu)
        self._geometry_menu.add_command(label="Export")
        self._menu.add_cascade(label="Geometry", menu=self._geometry_menu)

        self._help_menu = ttk.Menu(self._menu)
        self._help_menu.add_command(label="Documentation")
        self._help_menu.add_command(label="About", command=self._on_about)
        self._menu.add_cascade(label="Help", menu=self._help_menu)

    def _on_open(self):
        filename = askopenfilename(title="Select File", filetypes=(("yaml files", "*.yaml"), ("toml file", "*.toml")))
        
        datas = None
        with open(filename, "r") as f:
            datas = yaml.safe_load(f)

        reactor = datas["reactor"]
        chimney = datas["chimney"]
        meshing = datas["meshing"]

        self._on_reset()
         
        for i, entry in enumerate(self._center_entry):
            entry.insert(0, reactor["center"][i])

        self._reactor_radius_entry.insert(0, reactor["radius"])

        self._reactor_height_entry.insert(0, reactor["height"])

        self._chimney_width_entry.insert(0, chimney["width"])

        self._chimney_height_entry.insert(0, chimney["height"])

        self._mesh_size_entry.insert(0, meshing["size"])

        if meshing["optimize"] == 1:
            self._optimize_button.invoke()

        self._per_squarre_entry.set(meshing["square_ratio"]*100)

        self._per_curvature_entry.set(meshing["curvature_ratio"]*100)


    def _on_yaml(self):
        datas = self._get_datas()
        if datas is None:
            return
 
        filename = asksaveasfilename(
            title="Save As",
            defaultextension=".yaml",
        )

        with open(filename, "w") as f:
            yaml.dump(datas, f)


        showinfo(title="Info", message="File saved to yaml format !")

    def _on_toml(self):
        return

    def _generate_reactor_widget(self, geometry_frame):
        ttk.Label(
            geometry_frame, text="Reactor dimensions", font=("Helvetica", 10, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky=W, padx=5, pady=5)

        ttk.Label(geometry_frame, text="Center position").grid(
            row=1, column=0, padx=5, pady=5, sticky=W
        )

        frame_center = ttk.Frame(geometry_frame)
        frame_center.grid(row=1, column=1, padx=5, pady=5, sticky=EW)

        self._center_entry = []
        labels = ["X:", "Y:", "Z:"]

        for label_text in labels:
            ttk.Label(frame_center, text=label_text, font=("Helvetica", 10)).pack(
                side=LEFT, padx=(5, 2)
            )
            entry = ttk.Entry(frame_center, width=3)
            entry.pack(side=LEFT, padx=(0, 5))
            self._center_entry.append(entry)

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

    def _generate_chimney_widget(self, geometry_frame):
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

    def _generate_meshing_widgets(self, meshing_frame):
        ttk.Label(meshing_frame, text="Characteritics mesh size").grid(
            row=0, column=0, padx=5, pady=5
        )
        self._mesh_size_entry = ttk.Entry(meshing_frame)
        self._mesh_size_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(meshing_frame, text="Square mesh size").grid(
            row=4, column=0, padx=5, pady=5, sticky=W
        )

        frame_scale = ttk.Frame(meshing_frame)
        frame_scale.grid(row=4, column=1, pady=5, sticky=EW)

        self._per_squarre_entry = ttk.Scale(
            frame_scale,
            orient=HORIZONTAL,
            value=50,
            from_=0,
            to=99,
            length=80,
            command=self._update_per_square,
        )
        self._per_squarre_entry.pack(side=LEFT, fill=X, expand=True, padx=(28, 10))

        ttk.Label(frame_scale, textvariable=self._per_square_var, width=6).pack(
            side=RIGHT
        )

        ttk.Label(meshing_frame, text="Square mesh curvature").grid(
            row=5, column=0, padx=5, pady=5, sticky=W
        )

        frame_scale = ttk.Frame(meshing_frame)
        frame_scale.grid(row=5, column=1, pady=5, sticky=EW)

        self._per_curvature_entry = ttk.Scale(
            frame_scale,
            orient=HORIZONTAL,
            value=10,
            from_=0,
            to=99,
            length=80,
            command=self._update_per_curvature,
        )
        self._per_curvature_entry.pack(side=LEFT, fill=X, expand=True, padx=(28, 10))

        ttk.Label(frame_scale, textvariable=self._per_curvature_var, width=6).pack(
            side=RIGHT
        )

        meshing_frame.columnconfigure(1, weight=1)

    def _generate_parameters_widget(self):
        # ---------------------- Geometry Frame -----------------------
        geometry_frame = ttk.LabelFrame(self._lframe, text="Geometry")
        geometry_frame.pack(side=TOP, fill=X)
        
        self._generate_reactor_widget(geometry_frame)

        ttk.Separator(geometry_frame, orient=HORIZONTAL).grid(
            row=5, column=0, columnspan=2, sticky=EW, pady=15, padx=10
        )

        self._generate_chimney_widget(geometry_frame)

        # ---------------------- Meshing Frame --------------------------
        meshing_frame = ttk.LabelFrame(self._lframe, text="Meshing")
        meshing_frame.pack(fill=X, pady=15)

        self._generate_meshing_widgets(meshing_frame)

    def _update_per_square(self, value):
        self._per_square_var.set(f"{float(value)/100:.2f}")

    def _update_per_curvature(self, value):
        self._per_curvature_var.set(f"{float(value)/100:.2f}")

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
        for entry in self._center_entry:
            entry.delete(0, END)
        self._reactor_radius_entry.delete(0, END)
        self._reactor_height_entry.delete(0, END)
        self._per_squarre_entry.set(50)
        self._per_curvature_entry.set(50)
        self._chimney_width_entry.delete(0, END)
        self._chimney_height_entry.delete(0, END)
        self._mesh_size_entry.delete(0, END)

    def _get_datas(self) -> Optional[Dict]:
        center = [entry.get() for entry in self._center_entry]
        radius = self._reactor_radius_entry.get()
        height = self._reactor_height_entry.get()
        per_squarre = self._per_squarre_entry.get() / 100
        per_curvature = self._per_curvature_entry.get() / 100
        chimney_w = self._chimney_width_entry.get()
        chimney_h = self._chimney_height_entry.get()
        mesh_size = self._mesh_size_entry.get()
        optimize = self._optimize_var.get() != 0

        datas = [radius, height, per_squarre, chimney_w, chimney_h, mesh_size, *center, per_curvature]

        for data in datas:
            if not data:
                showwarning(title="Warning", message="Some values aren't filled !")
                return None
            if not isinstance(data, float):
                if not self._is_float(data):
                    showwarning(title="Warning", message="Numbers are expected !")
                    return None
        if optimize:
            if float(datas[0]) < float(datas[3]):
                showwarning(
                    title="Warning",
                    message="Squarre meshing size must be greater than the width of the chimney !",
                )
                return None
        else:
            if float(datas[2]) * float(datas[0]) < float(datas[3]):
                showwarning(
                    title="Warning",
                    message="Squarre meshing size must be greater than the width of the chimney !",
                )
                return None

        data = {
            "reactor": {
                "center": center,
                "radius" : radius, 
                "height": height
            }, 
            "chimney": {
                "width": chimney_w, 
                "height": chimney_h
            }, 
            "meshing": {
                "size": mesh_size,
                "square_ratio": per_squarre,
                "curvature_ratio": per_curvature,
                "optimize":self._optimize_var.get()
            }
        }

        return data

    def _on_generate(self):
        datas = self._get_datas() 
        if datas is None:
            return

        reactor = datas["reactor"]
        chimney = datas["chimney"]
        meshing = datas["meshing"]

        self._outputs.insert(END, f"\n----------- Generation started ----------\n\n")
        self._outputs.insert(END, f"Center: {reactor["center"]}\n")
        self._outputs.insert(END, f"Reactor radius: {reactor["radius"]}\n")
        self._outputs.insert(END, f"Reactor height: {reactor["height"]}\n")
        self._outputs.insert(END, f"Reactor per_squarre: {meshing["square_ratio"]:0.2f}\n")
        self._outputs.insert(END, f"Curvature ratio: {meshing["curvature_ratio"]:0.2f}\n\n")
        self._outputs.insert(END, f"Chimney width: {chimney["width"]}\n")
        self._outputs.insert(END, f"Chimney height: {chimney["height"]}\n")
        self._outputs.insert(END, f"Mesh size: {meshing["size"]}\n\n")

        self._outputs.see(END)

        maker = ReactorMaker()

        maker.set_output_widget(self._outputs)

        optimize = meshing["optimize"] != 0

        geometry = maker.create_geometry(
            center=vector3(float(reactor["center"][0]), float(reactor["center"][1]), float(reactor["center"][2])),
            reactor_dim=vector2(float(reactor["radius"]), float(reactor["height"])),
            chimney_dim=vector2(float(chimney["width"]), float(chimney["height"])),
            per_square=float(meshing["square_ratio"]),
            mesh_size=float(meshing["size"]),
            per_curvature=meshing["curvature_ratio"], 
            optimize=optimize
        ).unwrap()

        self._mesh = maker.mesh(geometry, optimize).unwrap()

        maker.reset_output()

        self._outputs.insert(END, f"\nMesh succesfully computed !\n")

        showinfo(title="Info", message="Mesh computed !")
    
    def _on_export_unv(self):
        if self._mesh is None:
            showinfo(title="Info", message="No mesh generated")
            return

        filename = asksaveasfilename(
            title="Export As",
            defaultextension=".unv",
        )

        if self._mesh.export_to(filename):
            self._outputs.insert(END, f"\nMesh succesfully saved !\n")
            showinfo(title="Info", message="File exported to unv format !")

    def _on_about(self):
        showinfo(title="About", message="Reactor Maker\nv1.0.0")

    def _is_float(self, value: str) -> bool:
        if value is None:
            return False
        try:
            float(value)
            return True
        except:
            return False

    def run(self):
        self._window.mainloop()


def main():
    application = Application()
    application.run()


if __name__ == "__main__":
    main()
