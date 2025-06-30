import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle


class TimeSeriesLabeler:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        self.master.title("Time Series Labeler")
        self.data: pd.DataFrame | None = None
        self.labels: list[tuple[float, float, str]] = []
        self.start: float | None = None

        # UI elements
        open_btn = tk.Button(master, text="Open CSV", command=self.open_csv)
        open_btn.pack(side=tk.TOP, pady=5)

        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.mpl_connect("button_press_event", self.on_press)

        btn_frame = tk.Frame(master)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        save_btn = tk.Button(btn_frame, text="Save & Compute", command=self.save)
        save_btn.pack(side=tk.RIGHT, padx=5)

    def open_csv(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not path:
            return
        try:
            df = pd.read_csv(path)
        except Exception as exc:  # pylint: disable=broad-except
            messagebox.showerror("Error", f"Could not read file: {exc}")
            return
        if "time" not in df.columns or "value" not in df.columns:
            messagebox.showerror("Error", "CSV must contain 'time' and 'value' columns")
            return
        self.data = df
        self.labels.clear()
        self.start = None
        self.plot_data()

    def plot_data(self) -> None:
        assert self.data is not None
        self.ax.clear()
        self.ax.plot(self.data["time"], self.data["value"], label="value")
        for start, end, label in self.labels:
            self.ax.add_patch(
                Rectangle(
                    (start, self.data["value"].min()),
                    end - start,
                    self.data["value"].max() - self.data["value"].min(),
                    alpha=0.3,
                    label=label,
                )
            )
        self.ax.set_xlabel("time")
        self.ax.set_ylabel("value")
        self.ax.legend(loc="upper right")
        self.canvas.draw()

    def on_press(self, event) -> None:
        if self.data is None or event.inaxes != self.ax:
            return
        if self.start is None:
            self.start = float(event.xdata)
            return
        end = float(event.xdata)
        if end <= self.start:
            self.start = None
            return
        label = simpledialog.askstring("Label", "Etiqueta para este rango:")
        if not label:
            self.start = None
            return
        self.labels.append((self.start, end, label))
        self.start = None
        self.plot_data()

    def save(self) -> None:
        if self.data is None:
            return
        df = self.data.copy()
        df["label"] = None
        for start, end, label in self.labels:
            df.loc[(df["time"] >= start) & (df["time"] <= end), "label"] = label
        out_path = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV Files", "*.csv")]
        )
        if not out_path:
            return
        df.to_csv(out_path, index=False)
        labeled_mean = df.dropna(subset=["label"])["value"].mean()
        unlabeled_mean = df[df["label"].isna()]["value"].mean()
        messagebox.showinfo(
            "Stats",
            f"Media etiquetada: {labeled_mean:.3f}\nMedia no etiquetada: {unlabeled_mean:.3f}",
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = TimeSeriesLabeler(root)
    root.mainloop()
