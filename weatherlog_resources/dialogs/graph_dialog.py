# -*- coding: utf-8 -*-


# This file defines the graph dialog.


# Import GTK for the dialog.
from gi.repository import Gtk
# Import datetime for sorting by dates.
import datetime
# Import matplotlib for graphing.
from matplotlib.figure import Figure
from matplotlib.dates import date2num
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas


class GenericGraphDialog(Gtk.Dialog):
    """Shows the graph dialog."""
    def __init__(self, parent, title, data, last_profile, units):
        """Create the dialog."""
        
        prec_amount_labels = ["Rain", "Snow", "Sleet", "Hail"]
        prec_amount_colors = ["green", "orangered", "royalblue", "plum"]
        prec_days_labels = ["None", "Rain", "Snow", "Sleet", "Hail"]
        prec_days_colors = ["green", "orangered", "royalblue", "plum", "white"]
        
        # This window should be modal.
        Gtk.Dialog.__init__(self, title, parent, Gtk.DialogFlags.MODAL)
        self.set_default_size(1000, 600)
        
        # Create the tab notebook.
        notebook = Gtk.Notebook()
        notebook.set_tab_pos(Gtk.PositionType.LEFT)
        info_box = self.get_content_area()
        
        # Add the buttons.
        self.add_button("Close", Gtk.ResponseType.CLOSE)
        
        # Tab 1: Temperature graph.
        info_box1 = Gtk.Box()
        info_box1_lbl = Gtk.Label("Temperature")
        f1 = Figure(figsize = (12, 6))
        f1.subplots_adjust(bottom = 0.2)
        a1 = f1.add_subplot(1,1,1)
        a1.plot(data[1], data[2])
        a1.set_title("Temperature - %s" % last_profile)
        a1.set_xlabel("Date")
        a1.set_ylabel("Temperature")
        a1.set_xticks(data[1])
        a1.set_xticklabels(
                data[0], rotation = "vertical"
        )
        canvas1 = FigureCanvas(f1)
        scrolled_win1 = Gtk.ScrolledWindow()
        scrolled_win1.set_hexpand(True)
        scrolled_win1.set_vexpand(True)
        scrolled_win1.add(canvas1)
        
        # Tab 2: Precipitation graph.
        info_box2 = Gtk.Box()
        info_box2_lbl = Gtk.Label("Precipitation")
        f2 = Figure(figsize = (12, 6))
        f2.subplots_adjust(bottom = 0.2)
        a2 = f2.add_subplot(1,1,1)
        a2.plot(data[1], data[3])
        a2.set_title("Precipitation - %s" % last_profile)
        a2.set_xlabel("Date")
        a2.set_ylabel("Precipitation")
        a2.set_xticks(data[1])
        a2.set_xticklabels(
                data[0], rotation = "vertical"
        )
        canvas2 = FigureCanvas(f2)
        scrolled_win2 = Gtk.ScrolledWindow()
        scrolled_win2.set_hexpand(True)
        scrolled_win2.set_vexpand(True)
        scrolled_win2.add(canvas2)
        
        # Tab 3: Precipitation amount pie chart
        info_box6 = Gtk.Box()
        info_box6_lbl = Gtk.Label("Precipitation (Amount)")
        f6 = Figure(figsize = (12, 6))
        a6 = f6.add_subplot(1,1,1)
        a6.pie(data[7], labels = prec_amount_labels, colors = prec_amount_colors, autopct = "%1.1f%%", startangle = 90)
        a6.axis("equal")
        canvas6 = FigureCanvas(f6)
        scrolled_win6 = Gtk.ScrolledWindow()
        scrolled_win6.set_hexpand(True)
        scrolled_win6.set_vexpand(True)
        scrolled_win6.add(canvas6)
        
        # Tab 4: Precipitation days pie chart
        info_box7 = Gtk.Box()
        info_box7_lbl = Gtk.Label("Precipitation (Days)")
        f7 = Figure(figsize = (12, 6))
        a7 = f7.add_subplot(1,1,1)
        a7.pie(data[8], labels = prec_days_labels, colors = prec_days_colors, autopct = "%1.1f%%", startangle = 90)
        a7.axis("equal")
        canvas7 = FigureCanvas(f7)
        scrolled_win7 = Gtk.ScrolledWindow()
        scrolled_win7.set_hexpand(True)
        scrolled_win7.set_vexpand(True)
        scrolled_win7.add(canvas7)
        
        # Tab 5: Wind graph.
        info_box3 = Gtk.Box()
        info_box3_lbl = Gtk.Label("Wind")
        f3 = Figure(figsize = (12, 6))
        f3.subplots_adjust(bottom = 0.2)
        a3 = f3.add_subplot(1,1,1)
        a3.plot(data[1], data[4])
        a3.set_title("Wind Speed - %s" % last_profile)
        a3.set_xlabel("Date")
        a3.set_ylabel("Wind Speed")
        a3.set_xticks(data[1])
        a3.set_xticklabels(
                data[0], rotation = "vertical"
        )
        canvas3 = FigureCanvas(f3)
        scrolled_win3 = Gtk.ScrolledWindow()
        scrolled_win3.set_hexpand(True)
        scrolled_win3.set_vexpand(True)
        scrolled_win3.add(canvas3)
        
        # Tab 6: Humidity graph.
        info_box4 = Gtk.Box()
        info_box4_lbl = Gtk.Label("Humidity")
        f4 = Figure(figsize = (12, 6))
        f4.subplots_adjust(bottom = 0.2)
        a4 = f4.add_subplot(1,1,1)
        a4.plot(data[1], data[5])
        a4.set_title("Humidity - %s" % last_profile)
        a4.set_xlabel("Date")
        a4.set_ylabel("Humidity")
        a4.set_xticks(data[1])
        a4.set_xticklabels(
                data[0], rotation = "vertical"
        )
        canvas4 = FigureCanvas(f4)
        scrolled_win4 = Gtk.ScrolledWindow()
        scrolled_win4.set_hexpand(True)
        scrolled_win4.set_vexpand(True)
        scrolled_win4.add(canvas4)
        
        # Tab 7: Air Pressure graph.
        info_box5 = Gtk.Box()
        info_box5_lbl = Gtk.Label("Air Pressure")
        f5 = Figure(figsize = (12, 6))
        f5.subplots_adjust(bottom = 0.2)
        a5 = f5.add_subplot(1,1,1)
        a5.plot(data[1], data[6])
        a5.set_title("Air Pressure - %s" % last_profile)
        a5.set_xlabel("Date")
        a5.set_ylabel("Air Pressure")
        a5.set_xticks(data[1])
        a5.set_xticklabels(
                data[0], rotation = "vertical"
        )
        canvas5 = FigureCanvas(f5)
        scrolled_win5 = Gtk.ScrolledWindow()
        scrolled_win5.set_hexpand(True)
        scrolled_win5.set_vexpand(True)
        scrolled_win5.add(canvas5)
        
        # Add the tabs to the notebook.
        notebook.append_page(scrolled_win1, info_box1_lbl)
        notebook.append_page(scrolled_win2, info_box2_lbl)
        notebook.append_page(scrolled_win6, info_box6_lbl)
        notebook.append_page(scrolled_win7, info_box7_lbl)
        notebook.append_page(scrolled_win3, info_box3_lbl)
        notebook.append_page(scrolled_win4, info_box4_lbl)
        notebook.append_page(scrolled_win5, info_box5_lbl)
        info_box.add(notebook)
        
        # Show the dialog. There's no need to get the response.
        self.show_all()