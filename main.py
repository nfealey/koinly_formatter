
import importlib
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os


class GUI:
    def __init__(self, master):
        self.master = master
        master.title("Koinly Converter")

        self.source_label = tk.Label(master, text="Select Source File:")
        self.source_label.pack()

        self.source_entry = tk.Entry(master, width=50)
        self.source_entry.pack()

        self.browse_button = tk.Button(
            master, text="Browse", command=self.browse_source
        )
        self.browse_button.pack()

        self.format_var = tk.StringVar()
        self.wallet_types = {
            "Sparrow Wallet": "supported_wallets.sparrow_to_koinly.SparrowToKoinly",
            "Zeus Wallet": "supported_wallets.zeus_koinly.ZeusToKoinly",
        }
        self.format_var.set(list(self.wallet_types.keys())[0])
        self.format_label = tk.Label(master, text="Select Format:")
        self.format_label.pack()
        self.format_option = tk.OptionMenu(master, self.format_var, *self.wallet_types.keys())
        self.format_option.pack()

        self.output_label = tk.Label(master, text="Select Output Directory:")
        self.output_label.pack()

        import os
        download_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
        self.output_entry = tk.Entry(master, width=50)
        self.output_entry.insert(0, download_dir)
        self.output_entry.pack()

        self.browse_output_button = tk.Button(
            master, text="Browse", command=self.browse_output
        )
        self.browse_output_button.pack()

        self.convert_button = tk.Button(master, text="Convert", command=self.convert)
        self.convert_button.pack()

    def browse_source(self):
        filename = filedialog.askopenfilename()
        self.source_entry.delete(0, tk.END)
        self.source_entry.insert(tk.END, filename)

    def browse_output(self):
        directory = filedialog.askdirectory()
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, directory)

    def convert(self):
        source_file = self.source_entry.get()
        output_dir = self.output_entry.get()
        format = self.format_var.get()

        wallet_module, wallet_class = self.wallet_types[self.format_var.get()].rsplit('.', 1)
        module = importlib.import_module(wallet_module)
        converter_class = getattr(module, wallet_class)
        
        # Special handling for Zeus wallet which needs 3 files
        if format == "Zeus Wallet":
            # Ask for the three required files
            invoices_file = filedialog.askopenfilename(
                title="Select invoices.csv file",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            if not invoices_file:
                messagebox.showwarning("Warning", "invoices.csv file is required")
                return
                
            payments_file = filedialog.askopenfilename(
                title="Select payments.csv file",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            if not payments_file:
                messagebox.showwarning("Warning", "payments.csv file is required")
                return
                
            onchain_file = filedialog.askopenfilename(
                title="Select onchain.csv file",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            if not onchain_file:
                messagebox.showwarning("Warning", "onchain.csv file is required")
                return
                
            converter = converter_class(source_file, output_dir, invoices_file, payments_file, onchain_file)
        else:
            converter = converter_class(source_file, output_dir)

        try:
            converter.convert()
            messagebox.showinfo("Success", "Conversion complete!")
        except Exception as e:
            messagebox.showerror("Error", f"Conversion failed: {str(e)}")


root = tk.Tk()
my_gui = GUI(root)
root.mainloop()
