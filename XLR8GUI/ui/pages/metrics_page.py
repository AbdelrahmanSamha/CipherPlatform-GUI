from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QGroupBox, QScrollArea, QMessageBox, QHeaderView,
    QSizePolicy
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PySide6.QtGui import QPainter, QColor
import json
import os
import tempfile
import traceback
from datetime import datetime


class MetricsPage(QWidget):

    FPGA_CYCLES = {
        "key_expansion": {
            128: 83,
            192: 99,
            256: 115,
        },
        "block_cipher": {
            128: 22,
            192: 26,
            256: 30,
        },
        "uart_block": 8640,
    }

    FPGA_CLOCK_HZ = 50_000_000  # 50 MHz

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.metrics_history = []

        self.metrics_dir = "metrics"
        if not os.path.exists(self.metrics_dir):
            os.makedirs(self.metrics_dir)

        self.metrics_file = os.path.join(self.metrics_dir, "metrics_history.json")

        self.current_metric = None

        # Load history from file (robust)
        self._load_metrics()
        self._create_ui()

        # Connect controller signal
        self.controller.metrics_store_signal.connect(self.record_metric)

    def _create_ui(self):

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(12)

        title = QLabel("Performance Metrics Dashboard")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # ================= LATEST OPERATION =================
        latest_group = QGroupBox("Latest Operation")
        latest_layout = QVBoxLayout()

        self.operation_info_label = QLabel("No operations recorded yet")
        self.operation_info_label.setStyleSheet("font-size: 14px; padding: 5px;")
        latest_layout.addWidget(self.operation_info_label)

        self.comparison_table = QTableWidget(4, 3)
        self.comparison_table.setHorizontalHeaderLabels(
            ["Software", "FPGA (Measured)", "FPGA (Pure)"]
        )
        self.comparison_table.setVerticalHeaderLabels(
            ["Time (ms)", "Throughput (MB/s)", "Blocks/sec", "Winner"]
        )
        self.comparison_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.comparison_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Ensure full latest operation area visible (show all 4 rows)
        # Approximate minimum: header + 4 rows (row ~30 px each) => ~150-180
        self.comparison_table.setMinimumHeight(160)
        self.comparison_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        latest_layout.addWidget(self.comparison_table)
        latest_group.setLayout(latest_layout)

        # Add latest_group without stretch factors (inside scroll area these are unreliable)
        layout.addWidget(latest_group)

        # ================= CHARTS =================
        graphs_group = QGroupBox("Performance Comparison")
        graphs_layout = QHBoxLayout()

        self.time_chart_view = self._create_bar_chart("Time Comparison (ms)")
        graphs_layout.addWidget(self.time_chart_view)

        self.throughput_chart_view = self._create_bar_chart("Throughput (MB/s)")
        graphs_layout.addWidget(self.throughput_chart_view)

        graphs_group.setLayout(graphs_layout)
        layout.addWidget(graphs_group)

        self.winner_label = QLabel("")
        self.winner_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 10px; "
            "background-color: #f0f0f0; border-radius: 5px;"
        )
        self.winner_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.winner_label)

        # ================= PIE =================
        pie_group = QGroupBox("FPGA Time Breakdown")
        pie_layout = QVBoxLayout()

        self.pie_chart_view = self._create_pie_chart()
        pie_layout.addWidget(self.pie_chart_view)

        self.uart_label = QLabel("UART Overhead: -- ms (--%)")
        self.encryption_label = QLabel("Pure Encryption: -- ms (--%)")
        self.processing_label = QLabel("Processing Overhead: -- ms (--%)")
        self.processing_label.setStyleSheet("padding: 4px;")
        self.uart_label.setStyleSheet("padding: 4px;")
        self.encryption_label.setStyleSheet("padding: 4px;")

        pie_layout.addWidget(self.uart_label)
        pie_layout.addWidget(self.encryption_label)
        pie_layout.addWidget(self.processing_label)

        pie_group.setLayout(pie_layout)
        layout.addWidget(pie_group)

        # ================= HISTORY =================
        history_group = QGroupBox("Operation History")
        history_layout = QVBoxLayout()

        clear_btn = QPushButton("Clear All History")
        clear_btn.clicked.connect(self.clear_all_history)
        clear_btn.setMaximumWidth(150)
        history_layout.addWidget(clear_btn)

        self.history_table = QTableWidget(0, 8)
        self.history_table.setHorizontalHeaderLabels([
            "Timestamp", "Operation", "Size", "Mode",
            "FPGA (ms)", "Software (ms)", "Winner", "Actions"
        ])
        # Keep the same header behaviour as before
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Guarantee at least 6 rows visible:
        # assume row height ~30; header ~30 => (6 rows + 1 header) * 30 = 210
        self.history_table.setMinimumHeight(240)
        self.history_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)

        history_layout.addWidget(self.history_table)
        history_group.setLayout(history_layout)

        layout.addWidget(history_group)

        scroll.setWidget(main_widget)

        page_layout = QVBoxLayout(self)
        page_layout.addWidget(scroll)
        page_layout.setContentsMargins(0, 0, 0, 0)

        # If we have history, populate UI
        if self.metrics_history:
            # keep behavior: show latest metric and populate history table
            self.update_history_table()
            self.display_metric(self.metrics_history[-1])

    # ================= CHART CREATION =================

    def _create_bar_chart(self, title):
        chart = QChart()
        chart.setTitle(title)
        chart.setAnimationOptions(QChart.SeriesAnimations)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)

        # KEEP THE CHART SIZES EXACTLY AS REQUESTED
        chart_view.setMinimumHeight(400)

        return chart_view

    def _create_pie_chart(self):
        chart = QChart()
        chart.setTitle("Where Does FPGA Time Go?")
        chart.setAnimationOptions(QChart.SeriesAnimations)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)

        # KEEP THE PIE SIZE
        chart_view.setMinimumHeight(400)

        return chart_view

    # ================= METRICS =================

    def calculate_theoretical_fpga_time(self, data_size, key_size):

        # number of AES blocks (rounded up)
        num_blocks = (data_size + 15) // 16

        key_exp_cycles = self.FPGA_CYCLES["key_expansion"].get(key_size, 0)
        cipher_cycles = self.FPGA_CYCLES["block_cipher"].get(key_size, 0)
        uart_cycles = self.FPGA_CYCLES["uart_block"]

        total_key_exp_cycles = key_exp_cycles
        total_cipher_cycles = num_blocks * cipher_cycles
        total_uart_cycles = num_blocks * uart_cycles

        total_cycles = (
            total_key_exp_cycles +
            total_cipher_cycles +
            total_uart_cycles
        )

        def cycles_to_ms(c):
            return (c / self.FPGA_CLOCK_HZ) * 1000

        return {
            "key_expansion_ms": cycles_to_ms(total_key_exp_cycles),
            "encryption_ms": cycles_to_ms(total_cipher_cycles),
            "uart_ms": cycles_to_ms(total_uart_cycles),
            "total_ms": cycles_to_ms(total_cycles),
            "num_blocks": num_blocks
        }

    def calculate_metrics(self, metric_data):

        data_size = metric_data.get("data_size", 0)
        software_time_ms = metric_data.get("software_time_ms", 0)
        fpga_time_ms = metric_data.get("fpga_time_ms", 0)
        key_size = metric_data.get("key_size", 128)

        # Use consistent rounding for blocks everywhere
        num_blocks = (data_size + 15) // 16

        def throughput(size, time_ms):
            if size == 0 or time_ms == 0:
                return 0.0
            return (size / (1024 * 1024)) / (time_ms / 1000.0)

        def blocks_per_sec(blocks, time_ms):
            if blocks == 0 or time_ms == 0:
                return 0.0
            return blocks / (time_ms / 1000.0)

        theoretical = self.calculate_theoretical_fpga_time(data_size, key_size)

        # Pure FPGA encryption time = key expansion (once) + per-block cipher cycles.
        pure_time = theoretical["encryption_ms"] + theoretical["key_expansion_ms"]
        total_theoretical = theoretical["total_ms"]
        # Real measured FPGA time
        measured_total = fpga_time_ms

        # Theoretical components
        theoretical_uart = theoretical["uart_ms"]
        theoretical_encryption = pure_time

        # Software / system overhead (everything unexplained)
        processing_overhead = measured_total - (theoretical_uart + theoretical_encryption)

        # Clamp to zero to avoid negative values if measurement < theoretical
        processing_overhead = max(0.0, processing_overhead)

        # Percentages relative to measured total
        if measured_total > 0:
            uart_percent_real = (theoretical_uart / measured_total) * 100.0
            encryption_percent_real = (theoretical_encryption / measured_total) * 100.0
            processing_percent_real = (processing_overhead / measured_total) * 100.0
        else:
            uart_percent_real = encryption_percent_real = processing_percent_real = 0.0

        return {
            "software_throughput": throughput(data_size, software_time_ms),
            "software_blocks_per_sec": blocks_per_sec(num_blocks, software_time_ms),

            "fpga_throughput": throughput(data_size, fpga_time_ms),
            "fpga_blocks_per_sec": blocks_per_sec(num_blocks, fpga_time_ms),

            # fpga_pure_time_ms now correctly excludes UART overhead
            "fpga_pure_time_ms": pure_time,
            "fpga_pure_throughput": throughput(data_size, pure_time),
            "fpga_pure_blocks_per_sec": blocks_per_sec(num_blocks, pure_time),

            "fpga_uart_overhead_ms": theoretical_uart,
            "fpga_encryption_ms": theoretical_encryption,
            "fpga_processing_overhead_ms": processing_overhead,

            "fpga_uart_percent": uart_percent_real,
            "fpga_encryption_percent": encryption_percent_real,
            "fpga_processing_percent": processing_percent_real,

        }

    # ================= DISPLAY =================

    def display_metric(self, metric_data):

        if not metric_data:
            return

        self.current_metric = metric_data
        calculated = self.calculate_metrics(metric_data)

        # Basic displayed fields
        op_type = metric_data.get("operation", "Unknown")
        timestamp = metric_data.get("timestamp", "Unknown")
        mode = metric_data.get("mode", "Unknown")
        key_size = metric_data.get("key_size", 0)
        direction = "Encryption" if metric_data.get("direction") == "enc" else "Decryption"
        data_size = metric_data.get("data_size", 0)

        info_text = (f"Operation: {op_type.title()} | "
                    f"Time: {timestamp} | "
                    f"Config: {mode}-{key_size}, {direction}, {data_size} bytes")
        self.operation_info_label.setText(info_text)

        software_time = metric_data.get("software_time_ms", 0.0)
        fpga_time = metric_data.get("fpga_time_ms", 0.0)
        fpga_pure_time = calculated.get("fpga_pure_time_ms", 0.0)

        # Row 0: Time
        self.comparison_table.setItem(0, 0, QTableWidgetItem(f"{software_time:.2f}"))
        self.comparison_table.setItem(0, 1, QTableWidgetItem(f"{fpga_time:.2f}"))
        self.comparison_table.setItem(0, 2, QTableWidgetItem(f"{fpga_pure_time:.2f}"))

        # Row 1: Throughput (MB/s)
        self.comparison_table.setItem(1, 0, QTableWidgetItem(f"{calculated['software_throughput']:.2f}"))
        self.comparison_table.setItem(1, 1, QTableWidgetItem(f"{calculated['fpga_throughput']:.2f}"))
        self.comparison_table.setItem(1, 2, QTableWidgetItem(f"{calculated['fpga_pure_throughput']:.2f}"))

        # Row 2: Blocks/sec
        self.comparison_table.setItem(2, 0, QTableWidgetItem(f"{calculated['software_blocks_per_sec']:.0f}"))
        self.comparison_table.setItem(2, 1, QTableWidgetItem(f"{calculated['fpga_blocks_per_sec']:.0f}"))
        self.comparison_table.setItem(2, 2, QTableWidgetItem(f"{calculated['fpga_pure_blocks_per_sec']:.0f}"))

        # Row 3: Winner marker (measured)
        # Clear first
        self.comparison_table.setItem(3, 0, QTableWidgetItem(""))
        self.comparison_table.setItem(3, 1, QTableWidgetItem(""))
        self.comparison_table.setItem(3, 2, QTableWidgetItem(""))

        winner_marker = "N/A"
        if software_time > 0 and fpga_time > 0:
            if software_time < fpga_time:
                winner_marker = "Software"
                self.comparison_table.setItem(3, 0, QTableWidgetItem("✅"))
            else:
                winner_marker = "FPGA"
                self.comparison_table.setItem(3, 1, QTableWidgetItem("✅"))
        else:
            # can't decide
            winner_marker = "N/A"

        # Update bar charts (time and throughput)
        try:
            self._update_bar_chart(self.time_chart_view, "Time (ms)",
                                   software_time, fpga_time, fpga_pure_time)
            self._update_bar_chart(self.throughput_chart_view, "Throughput (MB/s)",
                                   calculated['software_throughput'],
                                   calculated['fpga_throughput'],
                                   calculated['fpga_pure_throughput'])
        except Exception:
            # don't let chart errors break UI
            print("Error updating charts:", traceback.format_exc())

        # Update winner label (safe math)
        speedup_measured = (software_time / fpga_time) if (fpga_time and software_time) else None
        speedup_theoretical = (software_time / fpga_pure_time) if (fpga_pure_time and software_time) else None

        if speedup_measured is None:
            winner_text = "No valid measured speedup"
        else:
            if speedup_measured >= 1.0:
                winner_text = f"🏆 FPGA wins by {speedup_measured:.2f}x (measured)"
            else:
                # avoid division by zero
                inv = (1.0 / speedup_measured) if speedup_measured != 0 else float('inf')
                winner_text = f"🏆 Software wins by {inv:.2f}x (measured)"

        if speedup_theoretical is None:
            winner_text += " | FPGA theoretical: N/A"
        else:
            winner_text += f" | FPGA theoretical: {speedup_theoretical:.2f}x faster"

        self.winner_label.setText(winner_text)

        # Update pie chart and breakdown labels
        try:
            self._update_pie_chart(
                calculated['fpga_uart_overhead_ms'],
                calculated['fpga_encryption_ms'],
                calculated['fpga_processing_overhead_ms']
            )
        except Exception:
            print("Error updating pie chart:", traceback.format_exc())

        uart_pct = calculated.get('fpga_uart_percent', 0.0)
        enc_pct = calculated.get('fpga_encryption_percent', 0.0)
        proc_pct = calculated.get('fpga_processing_percent', 0.0)

        self.uart_label.setText(f"UART Overhead: {calculated['fpga_uart_overhead_ms']:.2f} ms ({uart_pct:.1f}%)")
        self.encryption_label.setText(f"Pure Encryption: {calculated['fpga_encryption_ms']:.2f} ms ({enc_pct:.1f}%)")
        self.processing_label.setText( f"Processing Overhead: {calculated['fpga_processing_overhead_ms']:.2f} ms ({proc_pct:.1f}%)")
        
    def _update_bar_chart(self, chart_view, y_label, soft_value, fpga_value, fpga_pure_value):
        """Update a bar chart with new values"""
        chart = chart_view.chart()

        # Remove old series/axes to avoid duplication
        chart.removeAllSeries()
        # copy list to avoid modifying while iterating
        axes = list(chart.axes())
        for axis in axes:
            try:
                chart.removeAxis(axis)
            except Exception:
                pass

        bar_set = QBarSet("Performance")
        # append values in order
        bar_set.append([soft_value, fpga_value, fpga_pure_value])

        # keep color consistent
        try:
            bar_set.setColor(QColor("#4CAF50"))
        except Exception:
            pass

        series = QBarSeries()
        series.append(bar_set)
        chart.addSeries(series)

        categories = ["Software", "FPGA (Measured)", "FPGA (Pure)"]
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        max_val = max(soft_value, fpga_value, fpga_pure_value)
        if max_val == 0:
            max_val = 1.0
        axis_y.setRange(0, max_val * 1.2)
        axis_y.setTitleText(y_label)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)

        chart.legend().setVisible(False)

    def _update_pie_chart(self, uart_ms, encryption_ms, processing_ms):
        """Update pie chart with FPGA time breakdown"""
        chart = self.pie_chart_view.chart()
        chart.removeAllSeries()

        series = QPieSeries()

        # Protect against zero values (QPieSeries expects non-negative)
        uart_ms_v = max(0.0, float(uart_ms or 0.0))
        proc_ms_v = max(0.0, float(processing_ms or 0.0))
        enc_ms_v = max(0.0, float(encryption_ms or 0.0))

        # If both zero, add a single 'No data' slice to avoid Pie errors
        if uart_ms_v == 0 and enc_ms_v == 0 and proc_ms_v == 0:
            slice_none = series.append("No Data", 1.0)
            slice_none.setLabelVisible(True)
            chart.addSeries(series)
            chart.legend().setAlignment(Qt.AlignBottom)
            return

        slice_uart = series.append("UART Overhead", uart_ms_v)
        slice_uart.setColor(QColor("#FF5252"))
        slice_uart.setLabelVisible(True)

        slice_enc = series.append("Encryption", enc_ms_v)
        slice_enc.setColor(QColor("#4CAF50"))
        slice_enc.setLabelVisible(True)

        slice_proc = series.append("Processing Overhead", proc_ms_v)
        slice_proc.setColor(QColor("#2196F3"))
        slice_proc.setLabelVisible(True)
        # Explode the larger slice slightly
        if uart_ms_v > enc_ms_v:
            slice_uart.setExploded(True)
            slice_uart.setExplodeDistanceFactor(0.1)
        else:
            slice_enc.setExploded(True)
            slice_enc.setExplodeDistanceFactor(0.1)

        chart.addSeries(series)
        chart.legend().setAlignment(Qt.AlignBottom)

    # ================= HISTORY =================

    def update_history_table(self):
        """Update the history table with all metrics (including action buttons)"""

        # Clear all existing rows and widgets
        self.history_table.clearContents()
        self.history_table.setRowCount(0)

        # Set row count
        row_count = len(self.metrics_history)
        self.history_table.setRowCount(row_count)

        for row, metric in enumerate(self.metrics_history):
            # Timestamp
            self.history_table.setItem(row, 0, QTableWidgetItem(metric.get("timestamp", "")))

            # Operation
            self.history_table.setItem(row, 1, QTableWidgetItem(metric.get("operation", "").title()))

            # Size
            size = metric.get("data_size", 0)
            size_str = f"{size} B" if size < 1024 else f"{size/1024:.1f} KB"
            self.history_table.setItem(row, 2, QTableWidgetItem(size_str))

            # Mode
            mode = f"{metric.get('mode', '')}-{metric.get('key_size', '')}"
            self.history_table.setItem(row, 3, QTableWidgetItem(mode))

            # FPGA time
            self.history_table.setItem(row, 4, QTableWidgetItem(f"{metric.get('fpga_time_ms', 0):.2f}"))

            # Software time
            self.history_table.setItem(row, 5, QTableWidgetItem(f"{metric.get('software_time_ms', 0):.2f}"))

            # Winner
            soft_time = metric.get('software_time_ms', 0.0)
            fpga_time = metric.get('fpga_time_ms', 0.0)
            if soft_time > 0 and fpga_time > 0:
                winner = "Software" if soft_time < fpga_time else "FPGA"
            else:
                winner = "N/A"
            self.history_table.setItem(row, 6, QTableWidgetItem(winner))

            # Actions (View and Delete buttons)
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)

            view_btn = QPushButton("View")
            view_btn.setMaximumWidth(60)
            # capture current row with default arg to avoid late-binding
            view_btn.clicked.connect(lambda checked=False, idx=row: self.view_metric(idx))

            delete_btn = QPushButton("Delete")
            delete_btn.setMaximumWidth(60)
            delete_btn.clicked.connect(lambda checked=False, idx=row: self.delete_metric(idx))

            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()

            self.history_table.setCellWidget(row, 7, actions_widget)

        # optionally, keep the history table showing newest at bottom or top
        # (user didn't request sorting; we leave chronological order)

    def view_metric(self, row):
        """View a specific metric from history"""
        if 0 <= row < len(self.metrics_history):
            self.display_metric(self.metrics_history[row])

    def delete_metric(self, row):
        """Delete a metric from history"""
        if 0 <= row < len(self.metrics_history):
            del self.metrics_history[row]
            # save and refresh table
            self._save_metrics()
            self.update_history_table()
            # if we deleted the currently displayed metric, clear display or show new latest
            if self.current_metric and self.current_metric not in self.metrics_history:
                if self.metrics_history:
                    self.display_metric(self.metrics_history[-1])
                else:
                    # clear labels
                    self.current_metric = None
                    self.operation_info_label.setText("No operations recorded yet")
                    self.comparison_table.clearContents()
                    self.winner_label.setText("")
                    self.uart_label.setText("UART Overhead: -- ms (--%)")
                    self.encryption_label.setText("Pure Encryption: -- ms (--%)")

    def clear_all_history(self):
        """Clear all metrics history with confirmation"""
        reply = QMessageBox.question(
            self,
            "Clear All History",
            "Are you sure you want to delete all metrics history?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.metrics_history = []
            self._save_metrics()
            self.update_history_table()

            # Clear display
            self.current_metric = None
            self.operation_info_label.setText("No operations recorded yet")
            self.comparison_table.clearContents()
            self.winner_label.setText("")
            self.uart_label.setText("UART Overhead: -- ms (--%)")
            self.encryption_label.setText("Pure Encryption: -- ms (--%)")

    # ================= PERSISTENCE =================

    def _load_metrics(self):
        """
        Robust loader:
         - Accepts either {"metrics": [...]} or a bare list [...]
         - If file is corrupt, back it up to .bak and reset to empty list
        """
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Accept both dict with "metrics" and direct list formats
                    if isinstance(data, dict) and "metrics" in data and isinstance(data["metrics"], list):
                        self.metrics_history = data["metrics"]
                    elif isinstance(data, list):
                        # older format: a list of metrics
                        self.metrics_history = data
                    else:
                        # unexpected format: back up and reset
                        bak = self.metrics_file + ".bak"
                        try:
                            os.rename(self.metrics_file, bak)
                            print(f"⚠️ metrics file unexpected format; backed up to {bak}")
                        except Exception:
                            pass
                        self.metrics_history = []
            except Exception as e:
                # If JSON invalid/corrupt, back up file and reset to empty list
                try:
                    bak = self.metrics_file + ".corrupt"
                    os.rename(self.metrics_file, bak)
                    print(f"❌ Error loading metrics file; moved corrupt file to {bak}")
                except Exception:
                    print("❌ Error loading metrics file and failed to move corrupt file.")
                print("Error:", e)
                self.metrics_history = []
        else:
            self.metrics_history = []

    def _save_metrics(self):
        """
        Save metrics atomically to avoid corrupting the JSON file on crashes.
        """
        try:
            # use a temp file in the same directory, then atomically replace
            dirpath = os.path.dirname(self.metrics_file) or "."
            fd, tmp_path = tempfile.mkstemp(dir=dirpath, prefix="metrics_tmp_", suffix=".json")
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as tmpf:
                    json.dump({"metrics": self.metrics_history}, tmpf, indent=2)
                    tmpf.flush()
                    os.fsync(tmpf.fileno())
                # atomic replace
                os.replace(tmp_path, self.metrics_file)
            finally:
                # in case of errors, ensure temp file is removed
                if os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass
        except Exception as e:
            # don't crash UI; print error for debugging
            print("❌ Error saving metrics:", e)
            print(traceback.format_exc())

    # ================= PUBLIC API =================

    @Slot(dict)
    def record_metric(self, metric_data):
        """
        Append a metric (expected dict) and refresh UI + persist.
        Example metric_data:
        {
          "timestamp": "2026-02-13 14:23:45",
          "operation": "stream",
          "data_size": 10240,
          "mode": "CBC",
          "key_size": 256,
          "direction": "enc",
          "fpga_time_ms": 125.3,
          "software_time_ms": 89.2,
        }
        """
        # Add timestamp if missing
        if "timestamp" not in metric_data:
            metric_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Append and persist
        self.metrics_history.append(metric_data)
        self._save_metrics()

        # Update UI
        self.update_history_table()
        self.display_metric(metric_data)

        print(f"✅ Recorded metric: {metric_data.get('operation','?')} at {metric_data.get('timestamp','?')}")
