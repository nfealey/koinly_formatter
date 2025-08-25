"""Koinly Converter GUI Application.

This module provides a graphical user interface for converting various
cryptocurrency wallet export formats to Koinly-compatible CSV format.
"""

import importlib
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import os
import sys
import threading
from typing import Dict, Optional


class GUI:
    """Main GUI class for the Koinly Converter application.

    Provides a user-friendly interface for selecting wallet export files,
    choosing the wallet format, and converting to Koinly format with
    real-time validation and progress feedback.
    """

    def __init__(self, master: tk.Tk) -> None:
        """Initialize the GUI application.

        Args:
            master: The root Tkinter window
        """
        self.master: tk.Tk = master
        master.title("Koinly Converter")
        master.geometry("600x500")
        master.resizable(False, False)

        # Main frame
        main_frame = tk.Frame(master, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Source file section
        source_frame = tk.LabelFrame(main_frame, text="Source File", padx=10, pady=10)
        source_frame.pack(fill=tk.X, pady=(0, 10))

        self.source_entry = tk.Entry(source_frame, width=50)
        self.source_entry.pack(side=tk.LEFT, padx=(0, 10))

        self.browse_button = tk.Button(
            source_frame, text="Browse", command=self.browse_source
        )
        self.browse_button.pack(side=tk.LEFT)

        # Validation indicator for source
        self.source_valid = tk.Label(source_frame, text="", width=2)
        self.source_valid.pack(side=tk.LEFT, padx=(5, 0))

        # Wallet format section
        format_frame = tk.LabelFrame(main_frame, text="Wallet Format", padx=10, pady=10)
        format_frame.pack(fill=tk.X, pady=(0, 10))

        self.format_var: tk.StringVar = tk.StringVar()
        self.wallet_types: Dict[str, str] = {
            "Sparrow Wallet": "supported_wallets.sparrow_to_koinly.SparrowToKoinly",
            "Zeus Wallet (3 files)": "supported_wallets.zeus_koinly.ZeusToKoinly",
            "Zeus Wallet (single file)": "supported_wallets.zeus_single_file.ZeusSingleFileToKoinly",
        }
        self.format_var.set(list(self.wallet_types.keys())[0])
        self.format_var.trace_add("write", self.on_format_change)

        self.format_option = tk.OptionMenu(
            format_frame, self.format_var, *self.wallet_types.keys()
        )
        self.format_option.config(width=30)
        self.format_option.pack()

        # Format info label
        self.format_info = tk.Label(
            format_frame, text="Single CSV file required", fg="gray"
        )
        self.format_info.pack(pady=(5, 0))

        # Output file section
        output_frame = tk.LabelFrame(
            main_frame, text="Output File", padx=10, pady=10
        )
        output_frame.pack(fill=tk.X, pady=(0, 10))

        # Generate initial output filename
        self.output_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        self.output_entry = tk.Entry(output_frame, width=50, state='readonly')
        self.update_output_preview()
        self.output_entry.pack(side=tk.LEFT, padx=(0, 10))

        self.browse_output_button = tk.Button(
            output_frame, text="Browse", command=self.browse_output
        )
        self.browse_output_button.pack(side=tk.LEFT)

        # Validation indicator for output
        self.output_valid = tk.Label(output_frame, text="✓", fg="green", width=2)
        self.output_valid.pack(side=tk.LEFT, padx=(5, 0))

        # Progress section
        progress_frame = tk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(10, 0))

        self.progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate")
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))

        # Convert button
        self.convert_button = tk.Button(
            progress_frame,
            text="Convert",
            command=self.convert,
            bg="#4CAF50",
            fg="black",
            font=("Arial", 12, "bold"),
            padx=30,
            pady=10,
        )
        self.convert_button.pack()

        # Status bar
        self.status_frame = tk.Frame(master, bd=1, relief=tk.SUNKEN)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = tk.Label(
            self.status_frame, text="Ready", anchor=tk.W, padx=10
        )
        self.status_label.pack(fill=tk.X)

        # Bind validation events
        self.source_entry.bind("<KeyRelease>", self.validate_inputs)
        self.source_entry.bind("<KeyRelease>", lambda e: self.update_output_preview())
        self.format_var.trace_add("write", lambda *args: self.update_output_preview())
        
        # Initial validation
        self.validate_inputs()

    def browse_source(self) -> None:
        """Open file dialog to select source CSV file."""
        filename = filedialog.askopenfilename(
            title="Select Source CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if filename:
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(tk.END, filename)
            self.validate_inputs()
            self.update_output_preview()
            self.update_status(f"Selected: {os.path.basename(filename)}")

    def browse_output(self) -> None:
        """Open directory dialog to select output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir = directory
            self.update_output_preview()
            self.validate_inputs()
            self.update_status(f"Output directory: {directory}")

    def on_format_change(self, *args) -> None:
        """Handle wallet format selection changes.

        Updates UI elements based on selected wallet type. Zeus wallet
        requires 3 files, so source file input is disabled.

        Args:
            *args: Unused arguments from StringVar trace
        """
        format_type = self.format_var.get()
        if format_type == "Zeus Wallet (3 files)":
            self.format_info.config(
                text="Requires 3 CSV files (invoices, payments, onchain)"
            )
            self.source_entry.config(state="disabled")
            self.browse_button.config(state="disabled")
            self.source_valid.config(text="")
        else:
            self.format_info.config(text="Single CSV file required")
            self.source_entry.config(state="normal")
            self.browse_button.config(state="normal")
            self.validate_inputs()
            self.update_output_preview()

    def validate_inputs(self, event=None) -> None:
        """Validate input fields and update visual indicators.

        Shows checkmarks for valid inputs and X marks for invalid ones.

        Args:
            event: Optional event from key binding
        """
        format_type = self.format_var.get()

        # Validate source file
        if format_type != "Zeus Wallet (3 files)":
            source_file = self.source_entry.get()
            if (
                source_file
                and os.path.exists(source_file)
                and source_file.lower().endswith(".csv")
            ):
                self.source_valid.config(text="✓", fg="green")
            elif source_file:
                self.source_valid.config(text="✗", fg="red")
            else:
                self.source_valid.config(text="")

        # Validate output directory
        if hasattr(self, 'output_dir') and os.path.exists(self.output_dir) and os.path.isdir(self.output_dir):
            self.output_valid.config(text="✓", fg="green")
        else:
            self.output_valid.config(text="✗", fg="red")

    def update_output_preview(self) -> None:
        """Update the output file preview based on current selections."""
        format_type = self.format_var.get()
        source_file = self.source_entry.get()
        
        # Generate preview filename
        if format_type == "Sparrow Wallet":
            prefix = "sparrow_wallet"
        elif format_type == "Zeus Wallet (3 files)":
            prefix = "zeus_wallet"
        elif format_type == "Zeus Wallet (single file)":
            prefix = "zeus_wallet_single"
        else:
            prefix = "output"
            
        # Create timestamp
        from datetime import datetime
        import pytz
        timestamp = datetime.now(pytz.utc).strftime("%Y-%m-%d_%H-%M-%S")
        
        # Build full output path
        output_filename = f"{prefix}_{timestamp}.csv"
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Update the entry field
        self.output_entry.config(state='normal')
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, output_path)
        self.output_entry.config(state='readonly')

    def update_status(self, message: str) -> None:
        """Update the status bar message.

        Args:
            message: Status message to display
        """
        self.status_label.config(text=message)
        self.master.update_idletasks()

    def convert(self) -> None:
        """Run the conversion in a separate thread to keep GUI responsive.

        Starts progress indicator and launches conversion in background thread
        to prevent UI freezing during file processing.
        """
        # Disable convert button and start progress
        self.convert_button.config(state="disabled")
        self.progress_bar.start(10)
        self.update_status("Starting conversion...")

        # Run conversion in separate thread
        thread = threading.Thread(target=self._convert_thread)
        thread.daemon = True
        thread.start()

    def _convert_thread(self) -> None:
        """Actual conversion logic running in separate thread.

        Handles the conversion process and updates UI through thread-safe
        methods. All UI updates use master.after() for thread safety.
        """
        try:
            source_file = self.source_entry.get()
            output_dir = self.output_dir
            format_type = self.format_var.get()

            # Validate inputs
            if not source_file and format_type != "Zeus Wallet (3 files)":
                self._show_error("Error", "Please select a source file")
                return

            if not hasattr(self, 'output_dir') or not self.output_dir:
                self._show_error("Error", "Please select an output directory")
                return

            if not os.path.exists(output_dir):
                self._show_error(
                    "Error", f"Output directory does not exist: {output_dir}"
                )
                return

            if not os.path.isdir(output_dir):
                self._show_error(
                    "Error", f"Output path is not a directory: {output_dir}"
                )
                return

            self.master.after(0, self.update_status, "Loading converter module...")

            wallet_module, wallet_class = self.wallet_types[format_type].rsplit(".", 1)
            module = importlib.import_module(wallet_module)
            converter_class = getattr(module, wallet_class)

            # Special handling for Zeus wallet which needs 3 files
            if format_type == "Zeus Wallet (3 files)":
                # Show information about Zeus wallet requirements
                self.master.after(0, self._show_zeus_info)

                # Get Zeus files using event to wait for GUI thread
                self.zeus_files = {}
                self.master.after(0, self._get_zeus_files)

                # Wait for files to be selected
                import time

                while "complete" not in self.zeus_files:
                    time.sleep(0.1)

                if not self.zeus_files.get("success"):
                    return

                converter = converter_class(
                    source_file,
                    output_dir,
                    self.zeus_files["invoices"],
                    self.zeus_files["payments"],
                    self.zeus_files["onchain"],
                )
            else:
                converter = converter_class(source_file, output_dir)

            # Run conversion
            self.master.after(0, self.update_status, "Converting files...")
            output_file = converter.convert()

            # Success
            self.master.after(0, self._show_success, output_file)

        except FileNotFoundError as e:
            self._show_error("File Not Found", str(e))
        except PermissionError as e:
            self._show_error("Permission Error", str(e))
        except ValueError as e:
            self._show_error("Invalid Data", str(e))
        except RuntimeError as e:
            self._show_error("Processing Error", str(e))
        except Exception as e:
            self._show_error(
                "Unexpected Error",
                f"An unexpected error occurred:\n{type(e).__name__}: {str(e)}",
            )
        finally:
            # Reset UI
            self.master.after(0, self._reset_ui)

    def _show_zeus_info(self) -> None:
        """Show information dialog about Zeus wallet requirements."""
        messagebox.showinfo(
            "Zeus Wallet",
            "Zeus wallet requires 3 CSV files:\n\n"
            "1. invoices.csv - Lightning invoices\n"
            "2. payments.csv - Lightning payments\n"
            "3. onchain.csv - On-chain transactions\n\n"
            "You will be prompted to select each file.",
        )

    def _get_zeus_files(self) -> None:
        """Get Zeus wallet files through file dialogs.

        Prompts user to select three required CSV files for Zeus wallet.
        Sets self.zeus_files with results for thread communication.
        """
        # Ask for the three required files
        invoices_file = filedialog.askopenfilename(
            title="Select invoices.csv file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not invoices_file:
            messagebox.showwarning(
                "Warning", "invoices.csv file is required for Zeus wallet conversion"
            )
            self.zeus_files = {"success": False, "complete": True}
            return

        payments_file = filedialog.askopenfilename(
            title="Select payments.csv file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not payments_file:
            messagebox.showwarning(
                "Warning", "payments.csv file is required for Zeus wallet conversion"
            )
            self.zeus_files = {"success": False, "complete": True}
            return

        onchain_file = filedialog.askopenfilename(
            title="Select onchain.csv file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not onchain_file:
            messagebox.showwarning(
                "Warning", "onchain.csv file is required for Zeus wallet conversion"
            )
            self.zeus_files = {"success": False, "complete": True}
            return

        self.zeus_files = {
            "invoices": invoices_file,
            "payments": payments_file,
            "onchain": onchain_file,
            "success": True,
            "complete": True,
        }

    def _show_error(self, title: str, message: str) -> None:
        """Show error dialog from thread.

        Thread-safe method to display error messages.

        Args:
            title: Error dialog title
            message: Error message to display
        """
        self.master.after(0, messagebox.showerror, title, message)
        self.master.after(0, self.update_status, f"Error: {title}")

    def _show_success(self, output_file: str) -> None:
        """Show success dialog.

        Args:
            output_file: Path to the generated output file
        """
        messagebox.showinfo(
            "Success", f"Conversion complete!\n\nOutput saved to:\n{output_file}"
        )
        self.update_status(f"Success! Saved to: {os.path.basename(output_file)}")

    def _reset_ui(self) -> None:
        """Reset UI after conversion.

        Stops progress indicator and re-enables convert button.
        """
        self.progress_bar.stop()
        self.convert_button.config(state="normal")
        if not hasattr(self, "zeus_files") or self.zeus_files.get("success", False):
            self.update_status("Ready for next conversion")


if __name__ == "__main__":
    try:
        root = tk.Tk()
        my_gui = GUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)
