#!/usr/bin/env python
# -*- coding: utf-8 -*-


################################################################################

# WeatherLog
# Version 1.10

# WeatherLog is an application for keeping track of the weather and
# getting information about past trends.

# Released under the MIT open source license:
license_text = """
Copyright (c) 2013-2014 Adam Chesak

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

################################################################################


# Import any needed modules.
# Import Gtk and Gdk for the interface.
from gi.repository import Gtk, Gdk, GdkPixbuf
# Import json for loading and saving the data.
import json
# Import collections.Counter for getting the mode of the data.
from collections import Counter
# Import webbrowser for opening the help in the user's browser.
import webbrowser
# Import datetime for getting the difference between two dates, and 
# for sorting based on dates.
import datetime
# Import shutil for removing a directory.
import shutil
# Import os for creating a directory.
import os
# Import os.path for seeing if a directory exists.
import os.path
# Import sys for closing the application.
import sys
# Import time for working with dates and times.
import time
# Import pickle for loading and saving the data.
# Try importing cPickle (for most Python 2 implementations), then
# fall back to pickle (for Python 2 implementations lacking this module
# and Python 3) if needed.
try:
    import cPickle as pickle
except ImportError:
    import pickle
# Import urlopen and urlencode for opening a file from a URL.
# Try importing Python 3 module, then fall back to Python 2 if needed.
try:
    from urllib.request import urlopen
    from urllib.parse import urlencode
    py_version = 3
except ImportError:
    from urllib import urlopen, urlencode
    py_version = 2

# Tell Python not to create bytecode files, as they mess with the git repo.
# This line can be removed be the user, if desired.
sys.dont_write_bytecode = True

# Import the application's UI data.
from weatherlog_resources.ui import VERSION, TITLE, MENU_DATA
# Import the functions for setting up the application.
import weatherlog_resources.launch as launch
# Import the functions for various tasks.
import weatherlog_resources.utility_functions as utility_functions
# Import the functions for getting and calculating the data.
import weatherlog_resources.info_functions as info_functions
# Import the functions for reading and writing profiles.
import weatherlog_resources.io as io
# Import the functions for exporting the data.
import weatherlog_resources.export as export
# Import the function for exporting the info.
import weatherlog_resources.export_info as export_info
# Import the function for converting the data.
import weatherlog_resources.convert as convert
# Import the functions for getting the info.
import weatherlog_resources.info as info
# Import the functions for getting the chart data.
import weatherlog_resources.charts as charts
# Import the functions for handling command line arguments.
import weatherlog_resources.command_line as command_line
# Import the functions for filtering the data.
import weatherlog_resources.filter_data as filter_data
# Import the dialog for getting new data.
from weatherlog_resources.dialogs.new_dialog import AddNewDialog
# Import the dialog for editing a row of data.
from weatherlog_resources.dialogs.edit_dialog import EditDialog
# Import the dialog for displaying information.
from weatherlog_resources.dialogs.info_dialog import GenericInfoDialog
# Import the dialog for telling the user there is no data.
from weatherlog_resources.dialogs.data_dialog import show_no_data_dialog
# Import the dialog for entering a profile name.
from weatherlog_resources.dialogs.profile_name_dialog import ProfileNameDialog
# Import the dialog for selecting a profile from a list.
from weatherlog_resources.dialogs.profile_selection_dialog import ProfileSelectionDialog
# Import the dialog for selecting a date from a calendar.
from weatherlog_resources.dialogs.calendar_dialog import CalendarDialog
# Import the dialog for selecting a date from a list.
from weatherlog_resources.dialogs.date_selection_dialog import DateSelectionDialog
# Import the dialog for changing the options.
from weatherlog_resources.dialogs.options_dialog import OptionsDialog
# Import the dialog for displaying the charts.
from weatherlog_resources.dialogs.chart_dialog import GenericChartDialog
# Import the dialogs for selecting data subsets.
from weatherlog_resources.dialogs.select_simple_dialog import SelectDataSimpleDialog
from weatherlog_resources.dialogs.select_advanced_dialog import SelectDataAdvancedDialog
# Import the dialog for displaying data subsets.
from weatherlog_resources.dialogs.data_subset_dialog import DataSubsetDialog
# Import the miscellaneous dialogs.
from weatherlog_resources.dialogs.misc_dialogs import show_alert_dialog, show_error_dialog, show_question_dialog, show_file_dialog, show_save_dialog


# Get any required variables and set up the application.
# Get the main program directory.
main_dir = launch.get_main_dir()
# Check if the directory and base files exist, and create them if they don't.
launch.check_files_exist(main_dir)
# Get the last profile.
last_profile, original_profile, profile_exists = launch.get_last_profile(main_dir)
# Get the configuration.
config = launch.get_config(main_dir)
# Get the previous window size.
last_width, last_height = launch.get_window_size(main_dir, config)
# Get the units.
units = launch.get_units(config)
# Get the data.
data = launch.get_data(main_dir, last_profile)


class Weather(Gtk.Window):
    """Shows the main application."""
    def __init__(self):
        """Create the application."""
        
        # Create the window.
        Gtk.Window.__init__(self, title = "WeatherLog")
        self.set_default_size(last_width, last_height)
        self.set_icon_from_file("weatherlog_resources/images/icon_small.png")
        
        # Create the ListStore for storing the data. ListStore has 8 columns, all strings.
        self.liststore = Gtk.ListStore(str, str, str, str, str, str, str, str)
        
        # Add the data.
        for i in data:
            self.liststore.append(i)
        
        # Create the main UI.
        self.treeview = Gtk.TreeView(model = self.liststore)
        date_text = Gtk.CellRendererText()
        self.date_col = Gtk.TreeViewColumn("Date", date_text, text = 0)
        self.treeview.append_column(self.date_col)
        temp_text = Gtk.CellRendererText()
        self.temp_col = Gtk.TreeViewColumn("Temperature (%s)" % units["temp"], temp_text, text = 1)
        self.treeview.append_column(self.temp_col)
        prec_text = Gtk.CellRendererText()
        self.prec_col = Gtk.TreeViewColumn("Precipitation (%s)" % units["prec"], prec_text, text = 2)
        self.treeview.append_column(self.prec_col)
        wind_text = Gtk.CellRendererText()
        self.wind_col = Gtk.TreeViewColumn("Wind (%s)" % units["wind"], wind_text, text = 3)
        self.treeview.append_column(self.wind_col)
        humi_text = Gtk.CellRendererText()
        self.humi_col = Gtk.TreeViewColumn("Humidity (%)", humi_text, text = 4)
        self.treeview.append_column(self.humi_col)
        airp_text = Gtk.CellRendererText()
        self.airp_col = Gtk.TreeViewColumn("Air Pressure (%s)" % units["airp"], airp_text, text = 5)
        self.treeview.append_column(self.airp_col)
        clou_text = Gtk.CellRendererText()
        self.clou_col = Gtk.TreeViewColumn("Cloud Cover", clou_text, text = 6)
        self.treeview.append_column(self.clou_col)
        note_text = Gtk.CellRendererText()
        self.note_col = Gtk.TreeViewColumn("Notes", note_text, text = 7)
        self.treeview.append_column(self.note_col)
        
        # Create the ScrolledWindow for displaying the list with a scrollbar.
        scrolled_win = Gtk.ScrolledWindow()
        scrolled_win.set_hexpand(True)
        scrolled_win.set_vexpand(True)
        
        # Display the TreeView.
        scrolled_win.add(self.treeview)
        
        # Create the menus.
        action_group = Gtk.ActionGroup("actions")
        action_group.add_actions([
            ("weather_menu", None, "_Weather"),
            ("add_new", Gtk.STOCK_ADD, "Add _New...", "<Control>n", "Add a new day to the list", self.add_new),
            ("edit", None, "_Edit...", "<Control>e", None, self.edit),
            ("remove", Gtk.STOCK_REMOVE, "Remo_ve...", "<Control>r", "Remove a day from the list", self.remove),
            ("clear_data", Gtk.STOCK_CLEAR, "Clear Current _Data...", "<Control>d", "Clear the data", self.clear),
            ("clear_all", None, "Clear _All Data...", "<Control><Alt>d", None, self.clear_all),
            ("exit", Gtk.STOCK_QUIT, "_Quit...", None, "Close the application", lambda x: self.exit("ignore", "this"))
        ])
        action_group.add_actions([
            ("file_menu", None, "_File"),
            ("import", Gtk.STOCK_OPEN, "_Import...", None, "Import data from a file", self.import_file),
            ("import_profile", None, "Import as New _Profile...", "<Control><Shift>o", None, self.import_new_profile),
            ("import_merge", None, "Imp_ort and Merge...", "<Alt><Shift>o", None, self.import_merge),
            ("export", Gtk.STOCK_SAVE, "_Export...", None, "Export data to a file", lambda x: self.export_file(mode = "raw"))
        ])
        action_weather_export_group = Gtk.Action("export_menu", "E_xport to", None, None)
        action_group.add_action(action_weather_export_group)
        action_group.add_actions([
            ("export_html", None, "Export to _HTML...", "<Control><Alt>h", None, lambda x: self.export_file(mode = "html")),
            ("export_csv", None, "Export to _CSV...", "<Control><Alt>c", None, lambda x: self.export_file(mode = "csv")),
            ("export_pastebin", None, "Export to Paste_bin...", None, None, lambda x: self.export_pastebin("raw")),
            ("export_pastebin_html", None, "_Export to Pastebin (HTML)...", None, None, lambda x: self.export_pastebin("html")),
            ("export_pastebin_csv", None, "E_xport to Pastebin (CSV)...", None, None, lambda x: self.export_pastebin("csv")),
            ("reload_current", None, "Reload _Current Data...", "F5", None, self.reload_current),
            ("manual_save", None, "Man_ual Save...", "<Control>m", None, lambda x: self.save(show_dialog = True, automatic = False))
        ])
        action_group.add_actions([
            ("info_global_menu", None, "_Info"),
            ("info", Gtk.STOCK_INFO, "_Info...", "<Control>i", "Show info about the data", lambda x: self.show_info_generic(event = "ignore", info_type = "General", data = data))
        ])
        action_weather_info_group = Gtk.Action("info_menu", "_More Info", None, None)
        action_group.add_action(action_weather_info_group)
        action_group.add_actions([
            ("temperature", None, "_Temperature...", "<Control>t", None, lambda x: self.show_info_generic(event = "ignore", info_type = "Temperature", data = data)),
            ("precipitation", None, "_Precipitation...", "<Control>p", None, lambda x: self.show_info_generic(event = "ignore", info_type = "Precipitation", data = data)),
            ("wind", None, "_Wind...", "<Control>w", None, lambda x: self.show_info_generic(event = "ignore", info_type = "Wind", data = data)),
            ("humidity", None, "_Humidity...", "<Control>h", None, lambda x: self.show_info_generic(event = "ignore", info_type = "Humidity", data = data)),
            ("air_pressure", None, "_Air Pressure...", "<Control>a", None, lambda x: self.show_info_generic(event = "ignore", info_type = "Air Pressure", data = data)),
            ("cloud_cover", None, "_Cloud Cover...", "<Control>c", None, lambda x: self.show_info_generic(event = "ignore", info_type = "Cloud Cover", data = data)),
            ("notes", None, "_Notes...", "<Control>e", None, lambda x: self.show_info_generic(event = "ignore", info_type = "Notes", data = data)),
            ("info_range", None, "Info in _Range...", "<Control><Shift>i", None, lambda x: self.info_range("General"))
        ])
        action_weather_info_range_group = Gtk.Action("info_range_menu", "More In_fo in Range", None, None)
        action_group.add_action(action_weather_info_range_group)
        action_group.add_actions([
            ("temperature_range", None, "_Temperature in Range...", "<Control><Shift>t", None, lambda x: self.info_range("Temperature")),
            ("precipitation_range", None, "_Precipitation in Range...", "<Control><Shift>p", None, lambda x: self.info_range("Precipitation")),
            ("wind_range", None, "_Wind in Range...", "<Control><Shift>w", None, lambda x: self.info_range("Wind")),
            ("humidity_range", None, "_Humidity in Range...", "<Control><Shift>h", None, lambda x: self.info_range("Humidity")),
            ("air_pressure_range", None, "_Air Pressure in Range...", "<Control><Shift>a", None, lambda x: self.info_range("Air Pressure")),
            ("cloud_cover_range", None, "_Cloud Cover in Range...", "<Control><Shift>c", None, lambda x: self.info_range("Cloud Cover")),
            ("notes_range", None, "_Notes in Range...", "<Control><Shift>e", None, lambda x: self.info_range("Notes")),
            ("info_selected", None, "Info for Se_lected Dates...", None, None, lambda x: self.info_selected("General"))
        ])
        action_weather_info_selected_group = Gtk.Action("info_selected_menu", "More Info for Selected _Dates", None, None)
        action_group.add_action(action_weather_info_selected_group)
        action_group.add_actions([
            ("temperature_selected", None, "_Temperature for Selected Dates...", None, None, lambda x: self.info_selected("Temperature")),
            ("precipitation_selected", None, "_Precipitation for Selected Dates...", None, None, lambda x: self.info_selected("Precipitation")),
            ("wind_selected", None, "_Wind for Selected Dates...", None, None, lambda x: self.info_selected("Wind")),
            ("humidity_selected", None, "_Humidity for Selected Dates...", None, None, lambda x: self.info_selected("Humidity")),
            ("air_pressure_selected", None, "_Air Pressure for Selected Dates...", None, None, lambda x: self.info_selected("Air Pressure")),
            ("cloud_cover_selected", None, "_Cloud Cover for Selected Dates...", None, None, lambda x: self.info_selected("Cloud Cover")),
            ("notes_selected", None, "_Notes for Selected Dates...", None, None, lambda x: self.info_selected("Notes"))
        ])
        action_weather_charts_group = Gtk.Action("info_charts_menu", "Chart_s", None, None)
        action_group.add_action(action_weather_charts_group)
        action_group.add_actions([
            ("temperature_chart", None, "_Temperature Chart...", "<Alt><Shift>t", None, lambda x: self.show_chart_generic(event = "ignore", info_type = "Temperature", data = data)),
            ("precipitation_chart", None, "_Precipitation Chart...", "<Alt><Shift>p", None, lambda x: self.show_chart_generic(event = "ignore", info_type = "Precipitation", data = data)),
            ("wind_chart", None, "_Wind Chart...", "<Alt><Shift>w", None, lambda x: self.show_chart_generic(event = "ignore", info_type = "Wind", data = data)),
            ("humidity_chart", None, "_Humidity Chart...", "<Alt><Shift>h", None, lambda x: self.show_chart_generic(event = "ignore", info_type = "Humidity", data = data)),
            ("air_pressure_chart", None, "_Air Pressure Chart...", "<Alt><Shift>a", None, lambda x: self.show_chart_generic(event = "ignore", info_type = "Air Pressure", data = data)),
        ])
        action_weather_charts_range_group = Gtk.Action("info_charts_range_menu", "C_harts in Range", None, None)
        action_group.add_action(action_weather_charts_range_group)
        action_group.add_actions([
            ("temperature_range_chart", None, "_Temperature Chart in Range...", None, None, lambda x: self.chart_range("Temperature")),
            ("precipitation_range_chart", None, "_Precipitation Chart in Range...", None, None, lambda x: self.chart_range("Precipitation")),
            ("wind_range_chart", None, "_Wind Chart in Range...", None, None, lambda x: self.chart_range("Wind")),
            ("humidity_range_chart", None, "_Humidity Chart in Range...", None, None, lambda x: self.chart_range("Humidity")),
            ("air_pressure_range_chart", None, "_Air Pressure Chart in Range...", None, None, lambda x: self.chart_range("Air Pressure"))
        ])
        action_weather_charts_selected_group = Gtk.Action("info_charts_selected_menu", "Charts for Selec_ted Dates", None, None)
        action_group.add_action(action_weather_charts_selected_group)
        action_group.add_actions([
            ("temperature_selected_chart", None, "_Temperature for Selected Dates...", None, None, lambda x: self.chart_selected("Temperature")),
            ("precipitation_selected_chart", None, "_Precipitation for Selected Dates...", None, None, lambda x: self.chart_selected("Precipitation")),
            ("wind_selected_chart", None, "_Wind for Selected Dates...", None, None, lambda x: self.chart_selected("Wind")),
            ("humidity_selected_chart", None, "_Humidity for Selected Dates...", None, None, lambda x: self.chart_selected("Humidity")),
            ("air_pressure_selected_chart", None, "_Air Pressure for Selected Dates...", None, None, lambda x: self.chart_selected("Air Pressure")),
            ("select_data", None, "S_elect Data...", None, None, self.select_data_simple),
            ("select_data_advanced", None, "Select Data (_Advanced)...", None, None, self.select_data_advanced)
        ])
        action_group.add_actions([
            ("profiles_menu", None, "_Profiles"),
            ("switch_profile", None, "_Switch Profile...", "<Control><Shift>s", None, self.switch_profile),
            ("add_profile", None, "_Add Profile...", "<Control><Shift>n", None, self.add_profile),
            ("remove_profile", None, "_Remove Profile...", "<Control><Shift>d", None, self.remove_profile),
            ("rename_profile", None, "Re_name Profile...", None, None, self.rename_profile),
            ("merge_profiles", None, "_Merge Profiles...", None, None, self.merge_profiles)
        ])
        action_copy_group = Gtk.Action("copy_menu", "_Copy Data", None, None)
        action_group.add_action(action_copy_group)
        action_group.add_actions([
            ("copy_new", None, "To _New Profile...", None, None, lambda x: self.data_profile_new(mode = "Copy")),
            ("copy_existing", None, "To _Existing Profile...", None, None, lambda x: self.data_profile_existing(mode = "Copy"))
        ])
        action_move_group = Gtk.Action("move_menu", "Mo_ve Data", None, None)
        action_group.add_action(action_move_group)
        action_group.add_actions([
            ("move_new", None, "To _New Profile...", None, None, lambda x: self.data_profile_new(mode = "Move")),
            ("move_existing", None, "To _Existing Profile...", None, None, lambda x: self.data_profile_existing(mode = "Move"))
        ])
        action_group.add_actions([
            ("options_menu", None, "_Options"),
            ("options", None, "_Options...", "F2", None, self.options)
        ])
        action_group.add_actions([
            ("help_menu", None, "_Help"),
            ("about", Gtk.STOCK_ABOUT, "_About...", "<Shift>F1", None, self.show_about),
            ("mobile_link", None, "_Firefox OS App...", None, None, lambda x: webbrowser.open("https://marketplace.firefox.com/app/weatherfire")),
            ("help", Gtk.STOCK_HELP, "_Help...", None, None, self.show_help)
        ])
        
        # Set up the menus.
        ui_manager = Gtk.UIManager()
        ui_manager.add_ui_from_string(MENU_DATA)
        accel_group = ui_manager.get_accel_group()
        self.add_accel_group(accel_group)
        ui_manager.insert_action_group(action_group)
        
        # Create the grid for the UI and add the UI items.
        grid = Gtk.Grid()
        menubar = ui_manager.get_widget("/menubar")
        grid.add(menubar)
        toolbar = ui_manager.get_widget("/toolbar")
        grid.attach_next_to(toolbar, menubar, Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to(scrolled_win, toolbar, Gtk.PositionType.BOTTOM, 1, 1)
        self.add(grid)
        self.show_all()
        
        # Set the new title.
        self.update_title()
        
        # Bind the event for window close.
        self.connect("delete-event", self.delete_event)
        
        # Change the titles, if the user doesn't want units to be displayed.
        if not config["show_units"]:
            self.temp_col.set_title("Temperature")
            self.prec_col.set_title("Precipitation")
            self.wind_col.set_title("Wind")
            self.humi_col.set_title("Humidity")
            self.airp_col.set_title("Air Pressure")
        
        # Show the dialog telling the user the profile couldn't be found, if neccessary:
        if not profile_exists:
            show_alert_dialog(self, "WeatherLog", "The profile \"%s\" could not be found." % original_profile)
            self.save(show_dialog = False)
    
    
    def delete_event(self, widget, event):
        """Saves the window size."""
        
        # Get the current window size.
        height, width = self.get_size()
        
        # Save the window size.
        try:
            wins_file = open("%s/window_size" % main_dir, "w")
            wins_file.write("%d\n%d" % (height, width))
            wins_file.close()
        
        except IOError:
            # Show the error message if something happened, but continue.
            # This one is shown if there was an error writing to the file.
            print("Error saving window size file (IOError).")
    
    
    def add_new(self, event):
        """Shows the dialog for input of new data."""
        
        global data
        
        # Get the data to add.
        new_dlg = AddNewDialog(self, last_profile, config["location"], config["pre-fill"], config["show_pre-fill"], units)
        response = new_dlg.run()
        year, month, day = new_dlg.date_cal.get_date()
        date = "%d/%d/%d" % (day, month + 1, year)
        temp = new_dlg.temp_sbtn.get_value()
        prec = new_dlg.prec_sbtn.get_value()
        prec_type = new_dlg.prec_com.get_active_text()
        wind = new_dlg.wind_sbtn.get_value()
        wind_dir = new_dlg.wind_com.get_active_text()
        humi = new_dlg.humi_sbtn.get_value()
        airp = new_dlg.airp_sbtn.get_value()
        airp_read = new_dlg.airp_com.get_active_text()
        clou = new_dlg.clou_com.get_active_text()
        note = new_dlg.note_ent.get_text().strip()
        new_dlg.destroy()
        
        # If the user did not click OK, don't continue:
        if response != Gtk.ResponseType.OK:
            return
            
        # If the precipitation or wind are zero, set the appropriate type/direction to "None".
        if not prec:
            prec_type = "None"
        if not wind:
            wind_dir = "None"
        
        # If the date has already been entered, tell the user and don't continue.
        if date in utility_functions.get_column(data, 0):
            show_error_dialog(self, "Add New", "The date %s has already been entered." % date)
            
        else:
            # Format the data and add it to the list.
            new_data = [date, ("%.2f" % temp), "%s%s" % ((("%.2f" % prec) + " " if prec_type != "None" else ""), prec_type), "%s%s" % ((("%.2f" % wind) + " " if wind_dir != "None" else ""), wind_dir), ("%.2f" % humi), ("%.2f %s" % (airp, airp_read)), clou, note]
            data.append(new_data)
            
            # Sort the list by date.
            data = sorted(data, key = lambda x: datetime.datetime.strptime(x[0], "%d/%m/%Y"))
            
            # Add the new row to the interface.
            self.liststore.append(new_data)
        
        # Update the title and save the data.
        self.update_title()
        self.save(show_dialog = False)
    
    
    def edit(self, event):
        """Edits a row of data."""
        
        # Get the selected date.
        try:
            tree_sel = self.treeview.get_selection()
            tm, ti = tree_sel.get_selected()
            date = tm.get_value(ti, 0)
        
        except:
            # Tell the user there is nothing selected.
            show_error_dialog(self, "Edit - %s" % last_profile, "No date selected.")
            return
        
        # Get the index of the date.
        index = utility_functions.get_column(data, 0).index(date)
        
        # Get the new data.
        edit_dlg = EditDialog(self, last_profile, data[index], date, units)
        response = edit_dlg.run()
        temp = edit_dlg.temp_sbtn.get_value()
        prec = edit_dlg.prec_sbtn.get_value()
        prec_type = edit_dlg.prec_com.get_active_text()
        wind = edit_dlg.wind_sbtn.get_value()
        wind_dir = edit_dlg.wind_com.get_active_text()
        humi = edit_dlg.humi_sbtn.get_value()
        airp = edit_dlg.airp_sbtn.get_value()
        airp_read = edit_dlg.airp_com.get_active_text()
        clou = edit_dlg.clou_com.get_active_text()
        note = edit_dlg.note_ent.get_text().strip()
        edit_dlg.destroy()
        
        # If the user did not click OK, don't continue.
        if response != Gtk.ResponseType.OK:
            return
        
        # If the precipitation or wind are zero, set the appropriate type/direction to "None".
        if not prec:
            prec_type = "None"
        if not wind:
            wind_dir = "None"
        
        # Create and store the edited list of data.
        new_data = [date, ("%.2f" % temp), "%s%s" % ((("%.2f" % prec) + " " if prec_type != "None" else ""), prec_type), "%s%s" % ((("%.2f" % wind) + " " if wind_dir != "None" else ""), wind_dir), ("%.2f" % humi), ("%.2f %s" % (airp, airp_read)), clou, note]
        data[index] = new_data
        
        # Update the ListStore.
        self.liststore.clear()
        for i in data:
            self.liststore.append(i)
        
        # Save the data.
        self.save(show_dialog = False)
    
    
    def remove(self, event):
        """Removes a row of data from the list."""
        
        # Get the dates.
        dates = []
        for i in data:
            dates.append([i[0]])
        
        # Get the dates to remove.
        rem_dlg = DateSelectionDialog(self, "Remove - %s" % last_profile, dates)
        response = rem_dlg.run()
        model, treeiter = rem_dlg.treeview.get_selection().get_selected_rows()
        rem_dlg.destroy()
        
        # If the user did not click OK or nothing was selected, don't continue.
        if response != Gtk.ResponseType.OK or treeiter == None:
            return
        
        # Get the dates.
        ndates = []
        for i in treeiter:
            ndates.append(model[i][0])
        
        # If there is no data, don't continue.
        if len(ndates) == 0:
            return
        
        # Only show the confirmation dialog if the user wants that.
        if config["confirm_del"]:
            
            # Confirm that the user wants to delete the row.
            response = show_question_dialog(self, "Remove - %s" % last_profile, "Are you sure you want to delete the selected date%s?\n\nThis action cannot be undone." % ("s" if len(ndates) > 1 else ""))
            if response != Gtk.ResponseType.OK:
                return
        
        # Loop through the list of dates and delete them.
        for i in ndates:
            
            # Find each index and delete the item at that index.
            index = utility_functions.get_column(data, 0).index(i)
            del data[index]
        
        # Refresh the ListStore.
        self.liststore.clear()
        for i in data:
            self.liststore.append(i)
        
        # Update the title and save the data.
        self.update_title()
        self.save(show_dialog = False)
        
    
    def info_range(self, info):
        """Gets the range for the info to display."""
        
        # If there is no data, tell the user and don't show the info dialog.
        if len(data) == 0:
            show_no_data_dialog(self, "%s Info - %s" % (info, last_profile))
            return
        
        # Get the first and last entered dates.
        days, months, years = utility_functions.split_date(data[0][0])
        daye, monthe, yeare = utility_functions.split_date(data[len(data) - 1][0])
        
        # Get the starting date.
        start_dlg = CalendarDialog(self, "%s Info in Range - %s" % (info, last_profile), "Select the starting date:", days, months, years)
        response1 = start_dlg.run()
        year1, month1, day1 = start_dlg.info_cal.get_date()
        date1 = "%d/%d/%d" % (day1, month1 + 1, year1)
        start_dlg.destroy()
        
        # If the user did not click OK, don't continue.
        if response1 != Gtk.ResponseType.OK:
            return
            
        # Check to make sure this date is valid, and cancel the action if not.
        if date1 not in utility_functions.get_column(data, 0):
            show_error_dialog(self, "%s Info in Range - %s" % (info, last_profile), "%s is not a valid date." % date1)
            return
        
        # Get the ending date.
        end_dlg = CalendarDialog(self, "%s Info in Range - %s" % (info, last_profile), "Select the ending date:", daye, monthe, yeare)
        response2 = end_dlg.run()
        year2, month2, day2 = end_dlg.info_cal.get_date()
        date2 = "%d/%d/%d" % (day2, month2 + 1, year2)
        end_dlg.destroy()
        
        # If the user did not click OK, don't continue.
        if response2 != Gtk.ResponseType.OK:
            return
        
        # Check to make sure this date is valid, and cancel the action if not.
        if date2 not in utility_functions.get_column(data, 0):
            show_error_dialog(self, "%s Info in Range - %s" % (info, last_profile), "%s is not a valid date." % date2)
            return
        
        # Convert the dates to ISO notation for comparison.
        nDate1 = utility_functions.date_to_iso(day1, month1, year1)
        nDate2 = utility_functions.date_to_iso(day2, month2, year2)
        
        # Check to make sure this date is later than the starting date, 
        # and cancel the action if not.
        if date1 == date2 or nDate1 > nDate2:
            show_error_dialog(self, "%s Info in Range - %s" % (info, last_profile), "The ending date must later than the starting date.")
            return
        
        # Get the indices.
        date_col = utility_functions.get_column(data, 0)
        index1 = date_col.index(date1)
        index2 = date_col.index(date2)
        
        # Get the new list.
        data2 = data[index1:index2 + 1]
        
        # Pass the data to the appropriate function.
        self.show_info_generic(event = "ignore", info_type = info, data = data2)
    
    
    def info_selected(self, info = "General"):
        """Gets the selected dates to for the info to display."""
        
        # If there is no data, tell the user and don't show the info dialog.
        if len(data) == 0:
            show_no_data_dialog(self, "%s Info - %s" % (info, last_profile))
            return
        
        # Get the dates.
        dates = []
        for i in data:
            dates.append([i[0]])
        
        # Get the selected dates.
        info_dlg = DateSelectionDialog(self, "%s Info for Selected Dates - %s" % (info, last_profile), dates)
        response = info_dlg.run()
        model, treeiter = info_dlg.treeview.get_selection().get_selected_rows()
        info_dlg.destroy()
        
        # If the user did not click OK or nothing was selected, don't continue.
        if response != Gtk.ResponseType.OK or treeiter == None:
            return
        
        # Get the dates.
        ndates = []
        for i in treeiter:
            ndates.append(model[i][0])
        
        # Get the data.
        ndata = []
        for i in range(0, len(data)):
            if data[i][0] in ndates:
                ndata.append(data[i])
        
        # If there is no data, don't continue.
        if len(ndata) == 0:
            return
        
        # Pass the data to the appropriate function.
        self.show_info_generic(event = "ignore", info_type = info, data = ndata)
    
    
    def show_info_generic(self, event, info_type = "General", data = data):
        """Shows info about the data."""
        
        # If there is no data, tell the user and don't show the dialog.
        if len(data) == 0:
            show_no_data_dialog(self, "%s Info - %s" % (info_type, last_profile))
            return
        
        # Get the info.
        if info_type == "General":
            data2 = info.general_info(data, units)
        elif info_type == "Temperature":
            data2 = info.temp_info(data, units)
        elif info_type == "Precipitation":
            data2 = info.prec_info(data, units)
        elif info_type == "Wind":
            data2 = info.wind_info(data, units)
        elif info_type == "Humidity":
            data2 = info.humi_info(data, units)
        elif info_type == "Air Pressure":
            data2 = info.airp_info(data, units)
        elif info_type == "Cloud Cover":
            data2 = info.clou_info(data, units)
        elif info_type == "Notes":
            data2 = info.note_info(data, units)
        
        # Show the info.
        info_dlg = GenericInfoDialog(self, "%s Info - %s" % (info_type, last_profile), data2)
        response = info_dlg.run()
        
        # If the user clicked Export:
        if response == 9:
            
            # Create the dialog.
            export_dlg = Gtk.FileChooserDialog("Export %s Info - %s" % (info_type, last_profile), self, Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
            export_dlg.set_do_overwrite_confirmation(True)
            
            # Get the response.
            response2 = export_dlg.run()
            if response2 == Gtk.ResponseType.OK:
                
                # Export the info.
                filename = export_dlg.get_filename()
                export_info.export_info(data2, filename)
                
            # Close the dialog.
            export_dlg.destroy()
        
        # Close the dialog.
        info_dlg.destroy()
        
    
    def chart_range(self, info):
        """Gets the range for the chart to display."""
        
        # If there is no data, tell the user and don't show the info dialog.
        if len(data) == 0:
            
            # Show the dialog.
            show_no_data_dialog(self, "%s Chart - %s" % (info, last_profile))
            return
        
        # Get the first and last entered dates.
        days, months, years = utility_functions.split_date(data[0][0])
        daye, monthe, yeare = utility_functions.split_date(data[len(data) - 1][0])
        
        # Get the starting date.
        start_dlg = CalendarDialog(self, "%s Chart in Range - %s" % (info, last_profile), "Select the starting date:", days, months, years)
        response1 = start_dlg.run()
        year1, month1, day1 = start_dlg.info_cal.get_date()
        date1 = "%d/%d/%d" % (day1, month1 + 1, year1)
        start_dlg.destroy()
        
        # If the user did not click OK, cancel the action.
        if response1 != Gtk.ResponseType.OK:
            return
            
        # Check to make sure this date is valid, and cancel the action if not.
        if date1 not in utility_functions.get_column(data, 0):
            show_error_dialog(self, "%s Chart in Range - %s" % (info, last_profile), "%s is not a valid date." % date1)
            return
        
        # Get the ending date.
        end_dlg = CalendarDialog(self, "%s Chart in Range - %s" % (info, last_profile), "Select the ending date:", daye, monthe, yeare)
        response2 = end_dlg.run()
        year2, month2, day2 = end_dlg.info_cal.get_date()
        date2 = "%d/%d/%d" % (day2, month2 + 1, year2)
        end_dlg.destroy()
        
        # If the user did not click OK, don't continue.
        if response2 != Gtk.ResponseType.OK:
            return
        
        # Check to make sure this date is valid, and cancel the action if not.
        if date2 not in utility_functions.get_column(data, 0):
            show_error_dialog(self, "%s Chart in Range - %s" % (info, last_profile), "%s is not a valid date." % date2)
            return
        
        # Convert the dates to ISO notation for comparison.
        nDate1 = utility_functions.date_to_iso(day1, month1, year1)
        nDate2 = utility_functions.date_to_iso(day2, month2, year2)
        
        # Check to make sure this date is later than the starting date, 
        # and cancel the action if not.
        if date1 == date2 or nDate1 > nDate2:
            show_error_dialog(self, "%s Chart in Range - %s" % (info, last_profile), "The ending date must be later than the starting date.")
            return
        
        # Get the indices.
        date_col = utility_functions.get_column(data, 0)
        index1 = date_col.index(date1)
        index2 = date_col.index(date2)
        
        # Get the new list.
        data2 = data[index1:index2 + 1]
        
        # Pass the data to the appropriate function.
        self.show_chart_generic(event = "ignore", info_type = info, data = data2)
    
    
    def chart_selected(self, info = "General"):
        """Gets the selected dates to for the charts to display."""
        
        # If there is no data, tell the user and don't show the info dialog.
        if len(data) == 0:
            show_no_data_dialog(self, "%s Chart - %s" % (info, last_profile))
            return
        
        # Get the dates.
        dates = []
        for i in data:
            dates.append([i[0]])
        
        # Get the selected dates.
        info_dlg = DateSelectionDialog(self, "%s Chart for Selected Dates - %s" % (info, last_profile), dates)
        response = info_dlg.run()
        model, treeiter = info_dlg.treeview.get_selection().get_selected_rows()
        info_dlg.destroy()
        
        # If the user did not click OK or nothing was selected, don't continue.
        if response != Gtk.ResponseType.OK or treeiter == None:
            return
        
        # Get the dates.
        ndates = []
        for i in treeiter:
            ndates.append(model[i][0])
        
        # Get the data.
        ndata = []
        for i in range(0, len(data)):
            if data[i][0] in ndates:
                ndata.append(data[i])
        
        # If there is no data, don't continue.
        if len(ndata) == 0:
            return
        
        # Pass the data to the appropriate function.
        self.show_chart_generic(event = "ignore", info_type = info, data = ndata)
    
    
    def show_chart_generic(self, event, info_type, data = data):
        """Shows a chart about the data."""
        
        # If there is no data, tell the user and don't show the chart dialog.
        if len(data) == 0:
            show_no_data_dialog(self, "%s Chart - %s" % (info_type, last_profile))
            return
        
        # Get the chart data.
        if info_type == "Temperature":
            data2 = charts.temp_chart(data, units)
        elif info_type == "Precipitation":
            data2 = charts.prec_chart(data, units)
        elif info_type == "Wind":
            data2 = charts.wind_chart(data, units)
        elif info_type == "Humidity":
            data2 = charts.humi_chart(data, units)
        elif info_type == "Air Pressure":
            data2 = charts.airp_chart(data, units)
        
        # Show the chart.
        chart_dlg = GenericChartDialog(self, "%s Chart - %s" % (info_type, last_profile), data2)
        response = chart_dlg.run()
        
        # If the user clicked Export:
        if response == 9:
            
            # Create the dialog.
            export_dlg = Gtk.FileChooserDialog("Export %s Chart - %s" % (info_type, last_profile), self, Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
            export_dlg.set_do_overwrite_confirmation(True)
            
            # Get the response.
            response2 = export_dlg.run()
            if response2 == Gtk.ResponseType.OK:
                
                # Export the info.
                filename = export_dlg.get_filename()
                export_info.export_chart(data2, filename)
                
            # Close the dialog.
            export_dlg.destroy()
        
        # Close the dialog.
        chart_dlg.destroy()
    
    
    def select_data_simple(self, event):
        """Shows the simple data selection dialog."""
        
        # Get the field, condition, and value.
        sel_dlg = SelectDataSimpleDialog(self, last_profile)
        response = sel_dlg.run()
        field = sel_dlg.field_com.get_active_text()
        operator = sel_dlg.op_com.get_active_text()
        value = sel_dlg.value_ent.get_text()
        sel_dlg.destroy()
        
        # If the user did not press OK, don't continue.
        if response != Gtk.ResponseType.OK:
            return
        
        # If the column that is being compared is precipitation type, wind direction, air pressure change, 
        # or cloud cover, and the comparison is numerical, don't continue.
        if field == "precipitation type" or field == "wind direction" or field == "air pressure change" or field == "cloud cover":
            if operator != "equal to" and operator != "not equal to":
                show_error_dialog(self, "Select Data - %s" % last_profile, "Invalid comparison: %s cannot use the \"%s\" operator." % (field, operator))
                return
        
        # If the value was left blank, show and error message and don't continue.
        if value.lstrip().rstrip() == "":
            show_error_dialog(self, "Select Data - %s" % last_profile, "Value field cannot be left blank.")
            return
        
        # Filter the list.
        filtered = filter_data.filter_data(data, [field, operator, value])
        
        # If there are no items that match the condition, don't show the main dialog.
        if len(filtered) == 0:
            show_alert_dialog(self, "Data Subset - %s" % last_profile, "No data matches the specified condition.")
            return
        
        # Show the subset.
        sub_dlg = DataSubsetDialog(self, "Data Subset - %s" % last_profile, filtered, config["show_units"], units)
        response = sub_dlg.run()
        sub_dlg.destroy()
        
        # If the user clicked Export:
        if response == 9:
            
            # Create the dialog.
            export_dlg = Gtk.FileChooserDialog("Export Data Subset - %s" % last_profile, self, Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
            export_dlg.set_do_overwrite_confirmation(True)
            
            # Get the response.
            response2 = export_dlg.run()
            if response2 == Gtk.ResponseType.OK:
                
                # Export the info.
                filename = export_dlg.get_filename()
                export_info.export_subset(filtered, units, filename)
                
            # Close the dialog.
            export_dlg.destroy()
    
    
    def select_data_advanced(self, event):
        """Shows the advanced data selection dialog."""
        
        # Get the selection mode and all of the fields, conditions, and values.
        sel_dlg = SelectDataAdvancedDialog(self, last_profile)
        response = sel_dlg.run()
        sel_mode = sel_dlg.mode_com.get_active_text()
        temp_chk = sel_dlg.sel_chk1.get_active()
        temp_op = sel_dlg.op_com1.get_active_text()
        temp_val = sel_dlg.value_ent1.get_text()
        prec_chk = sel_dlg.sel_chk2.get_active()
        prec_op = sel_dlg.op_com2.get_active_text()
        prec_val = sel_dlg.value_ent2.get_text()
        prect_chk = sel_dlg.sel_chk3.get_active()
        prect_op = sel_dlg.op_com3.get_active_text()
        prect_val = sel_dlg.value_ent3.get_text()
        wind_chk = sel_dlg.sel_chk4.get_active()
        wind_op = sel_dlg.op_com4.get_active_text()
        wind_val = sel_dlg.value_ent4.get_text()
        windd_chk = sel_dlg.sel_chk5.get_active()
        windd_op = sel_dlg.op_com5.get_active_text()
        windd_val = sel_dlg.value_ent5.get_text()
        humi_chk = sel_dlg.sel_chk6.get_active()
        humi_op = sel_dlg.op_com6.get_active_text()
        humi_val = sel_dlg.value_ent6.get_text()
        airp_chk = sel_dlg.sel_chk7.get_active()
        airp_op = sel_dlg.op_com7.get_active_text()
        airp_val = sel_dlg.value_ent7.get_text()
        airpc_chk = sel_dlg.sel_chk8.get_active()
        airpc_op = sel_dlg.op_com8.get_active_text()
        airpc_val = sel_dlg.value_ent8.get_text()
        clou_chk = sel_dlg.sel_chk9.get_active()
        clou_op = sel_dlg.op_com9.get_active_text()
        clou_val = sel_dlg.value_ent9.get_text()
        sel_dlg.destroy()
        
        # If the user did not press OK, don't continue.
        if response != Gtk.ResponseType.OK:
            return
        
        # Put the values into a list to work with them more easily.
        conditions = []
        conditions.append(["temperature", temp_chk if temp_val.lstrip().rstrip() != "" else False, temp_op, temp_val])
        conditions.append(["precipitation amount", prec_chk if prec_val.lstrip().rstrip() != "" else False, prec_op, prec_val])
        conditions.append(["precipitation type", prect_chk if prect_val.lstrip().rstrip() != "" else False, prect_op, prect_val])
        conditions.append(["wind speed", wind_chk if wind_val.lstrip().rstrip() != "" else False, wind_op, wind_val])
        conditions.append(["wind direction", windd_chk if windd_val.lstrip().rstrip() != "" else False, windd_op, windd_val])
        conditions.append(["humidity", humi_chk if humi_val.lstrip().rstrip() != "" else False, humi_op, humi_val])
        conditions.append(["air pressure", airp_chk if airp_val.lstrip().rstrip() != "" else False, airp_op, airp_val])
        conditions.append(["air pressure change", airpc_chk if airpc_val.lstrip().rstrip() != "" else False, airpc_op, airpc_val])
        conditions.append(["cloud cover", clou_chk if clou_val.lstrip().rstrip() != "" else False, clou_op, clou_val])
        
        # Loop through the conditions and filter the data.
        filtered = []
        first = True
        for i in conditions:
            
            # If this condition isn't being checked, continue to the next.
            if not i[1]:
                continue
            
            # Get the filtered list.
            subset = filter_data.filter_data(data, [i[0], i[2], i[3]])
            
            # If this is the first condition, add all the data to the filtered list.
            if first:
                filtered += subset
                first = False
            
            # Otherwise, make sure it is combined correctly.
            # AND combination mode:
            elif sel_mode == "match all":
                filtered = filter_data.filter_and(filtered, subset)
            
            # OR combination mode or NOT combination mode:
            elif sel_mode == "match at least one" or sel_mode == "match none":
                filtered = filter_data.filter_or(filtered, subset)
        
        # If the NOT combination mode is used, apply that filter as well.
        if sel_mode == "match none":
            filtered = filter_data.filter_not(filtered, data)
        
        # If there are no items that match the condition, don't show the main dialog.
        if len(filtered) == 0:
            show_alert_dialog(self, "Data Subset - %s" % last_profile, "No data matches the specified condition(s).")
            return
        
        # Show the subset.
        sub_dlg = DataSubsetDialog(self, "Data Subset - %s" % last_profile, filtered, config["show_units"], units)
        response = sub_dlg.run()
        sub_dlg.destroy()
        
        # If the user clicked Export:
        if response == 9:
            
            # Create the dialog.
            export_dlg = Gtk.FileChooserDialog("Export Data Subset - %s" % last_profile, self, Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
            export_dlg.set_do_overwrite_confirmation(True)
            
            # Get the response.
            response2 = export_dlg.run()
            if response2 == Gtk.ResponseType.OK:
                
                # Export the info.
                filename = export_dlg.get_filename()
                export_info.export_subset(filtered, units, filename)
                
            # Close the dialog.
            export_dlg.destroy()
    
    
    def import_file(self, event):
        """Imports data from a file."""
        
        global data
        
        # Get the filename.
        response, filename = show_file_dialog(self, "Import - %s" % last_profile)
        
        # If the user did not click OK, don't continue.
        if response != Gtk.ResponseType.OK:
            return
            
        # Confirm that the user wants to overwrite the data, if the profile isn't blank.
        if len(data) > 0:
            response2 = show_question_dialog(self, "Confirm Import - %s" % last_profile, "Are you sure you want to import the data?\n\nCurrent data will be overwritten.")
            if response2 != Gtk.ResponseType.OK:
                return
        
        # Clear the data.
        data[:] = []
        # Clear the ListStore.
        self.liststore.clear()
        
        # Read and add the data.
        data = io.read_profile(filename = filename)
        for i in data:
            self.liststore.append(i)
        
        # Update the title and save the data.
        self.update_title()
        self.save(show_dialog = False)
    
    
    def import_merge(self, event):
        """Imports data and merges it into the current list."""
        
        global data
        
        # Get the filename.
        response, filename = show_file_dialog(self, "Import and Merge - %s" % last_profile)
        
        # If the user did not click OK, don't continue.
        if response != Gtk.ResponseType.OK:
            return
            
        # Read the data.
        data2 = io.read_profile(filename = filename)
        
        # If the imported dataset is empty, or if there was an error, don't continue.
        if len(data) == 0:
            return
            
        # Filter the new data to make sure there are no duplicates.
        new_data = []
        date_col = utility_functions.get_column(data, 0)
        for i in data2:
            
            # If the date already appears, don't include it.
            if i[0] not in date_col:
                new_data.append(i)
        
        # Append, sort, and add the data.
        data += new_data
        data = sorted(data, key = lambda x: datetime.datetime.strptime(x[0], "%d/%m/%Y"))
        self.liststore.clear()
        for i in data:
            self.liststore.append(i)
        
        # Update the title and save the data.
        self.update_title()
        self.save(show_dialog = False)      
    
    
    def import_new_profile(self, event):
        """Imports data from a file and inserts it in a new profile."""
        
        global last_profile
        global data
        
        # Get the new profile name.
        new_dlg = ProfileNameDialog(self, "Add Profile")
        response = new_dlg.run()
        name = new_dlg.nam_ent.get_text().lstrip().rstrip()
        new_dlg.destroy()
        
        # If the user did not press OK, don't continue.
        if response != Gtk.ResponseType.OK:
            return
            
        # Validate the name. If it contains a non-alphanumeric character or is just space,
        # show a dialog and cancel the action.
        validate = utility_functions.validate_profile(main_dir, name)
        if validate != "":
            show_error_dialog(self, "Add Profile", validate)
            return

        # Otherwise if there are no problems with the name, create the directory and file.
        last_profile = name
        os.makedirs("%s/profiles/%s" % (main_dir, name))
        open("%s/profiles/%s/weather" % (main_dir, name), "w").close()
        
        # Clear the old data.
        data[:] = []
        self.liststore.clear()

        # Get the filename.
        response, filename = show_file_dialog(self, "Import - %s" % last_profile)
        
        # If the user pressed OK, import the data:
        if response == Gtk.ResponseType.OK:
            
            # Read and add the data.
            data = io.read_profile(filename = filename)
            for i in data:
                self.liststore.append(i)
            
            # Update the title and save the data.
            self.update_title()
            self.save(show_dialog = False)
    
    
    def export_file(self, mode = "raw"):
        """Exports the data to a file."""
        
        # Get the title.
        title = "Export"
        if mode == "html":
            title += "to HTML"
        elif mode == "csv":
            title += "to CSV"
        title += " - %s" % (last_profile)
        
        # If there is no data, tell the user and cancel the action.
        if len(data) == 0:
            show_alert_dialog(self, title, "There is no data to export.")
            return
        
        # Get the filename.
        response, filename = show_save_dialog(self, title)
        
        # If the user pressed OK, export the data:
        if response == Gtk.ResponseType.OK:
            
            # Convert the data if needed.
            if mode == "html":
                converted = export.html(data, units)
            elif mode == "csv":
                converted = export.csv(data, units)
            
            # Save the data.
            if mode == "raw":
                io.write_profile(filename = filename, data = data)
            else:
                io.write_standard_file(filename = filename, data = converted)
    
    
    def export_pastebin(self, mode):
        """Exports the data to Pastebin."""
        
        # If there is no data, tell the user and cancel the action.
        if len(data) == 0:
            show_alert_dialog(self, "Export to Pastebin - %s" % last_profile, "There is no data to export.")
            return
        
        # Convert the data.
        if mode == "html":
            new_data = export.html(data, units)
        elif mode == "csv":
            new_data = export.csv(data, units)
        elif mode == "raw":
            new_data = json.dumps(data)
        
        # Build the api string.
        api = {"api_option": "paste",
               "api_dev_key": config["pastebin"],
               "api_paste_code": new_data}
        if mode == "html":
            api["api_paste_format"] = "html5"
        elif mode == "raw":
            api["api_paste_format"] = "javascript"
        
        # Upload the text.
        try:
            pastebin = urlopen("http://pastebin.com/api/api_post.php", urlencode(api))
            result = pastebin.read()
            pastebin.close()
            
            # Tell the user the URL.
            show_alert_dialog(self, "Export to Pastebin - %s" % last_profile, "The data has been uploaded to Pastebin, and can be accessed at the following URL:\n\n%s" % result)
            
        except:
            show_error_dialog(self, "Export to Pastebin - %s" % last_profile, "The data could not be uploaded to Pastebin.")
    
    
    def clear(self, event):
        """Clears the data."""
        
        global data
        
        # Only show the dialog if the user wants that.
        if config["confirm_del"]:
            response = show_question_dialog(self, "Clear Current Data - %s" % last_profile, "Are you sure you want to clear the data?\n\nThis action cannot be undone.")
            if response != Gtk.ResponseType.OK:
                return
        
        # Clear the data.
        data[:] = []
        self.liststore.clear()
        
        # Update the title and save the data.
        self.update_title()
        self.save(show_dialog = False)
        
    
    def clear_all(self, event):
        """Clears all data."""
        
        global last_profile
        global config
        global units
        
        # Only show the confirmation dialog if the user wants that.
        if config["confirm_del"]:
            response = show_question_dialog(self, "Clear All Data", "Are you sure you want to clear all the data?\n\nThis action cannot be undone.")
            if response != Gtk.ResponseType.OK:
                return

        # Clear the old data and reset the profile name.
        data[:] = []
        self.liststore.clear()
        last_profile = "Main Profile"
        
        # Restore all files to their default states.
        shutil.rmtree(main_dir)
        launch.check_files_exist(main_dir)
        
        # Set the default config.
        config = {"pre-fill": False,
                  "restore": True,
                  "location": "",
                  "units": "metric",
                  "pastebin": "d2314ff616133e54f728918b8af1500e",
                  "show_units": True,
                  "show_dates": True,
                  "auto_save": True,
                  "confirm_del": True,
                  "show_pre-fill": True,
                  "confirm_exit": False}
        
        # Configure the units.
        units = launch.get_units(config)
        
        # Update the main window.
        self.temp_col.set_title("Temperature (%s)" % units["temp"])
        self.prec_col.set_title("Precipitation (%s)" % units["prec"])
        self.wind_col.set_title("Wind (%s)" % units["wind"])
        self.humi_col.set_title("Humidity (%)")
        self.airp_col.set_title("Air Pressure (%s)" % units["airp"])
        
        # Update the title and save the data.
        self.update_title()
        self.save(show_dialog = False, from_options = True)
    
    
    def switch_profile(self, event):
        """Switches profiles."""
        
        global last_profile
        global data
        
        # Get the list of profiles
        profiles = io.get_profile_list(main_dir, last_profile)
        
        # If there are no other profiles, cancel the action.
        if len(profiles) == 0:
            show_alert_dialog(self, "Switch Profile", "There are no other profiles.")
        
        # Get the profile to switch to.
        swi_dlg = ProfileSelectionDialog(self, "Switch Profile", profiles)
        response = swi_dlg.run()
        model, treeiter = swi_dlg.treeview.get_selection().get_selected()
        swi_dlg.destroy()
        
        # If the user did not press OK or nothing was selected, don't continue:
        if response != Gtk.ResponseType.OK or treeiter == None:
            return
        
        # Get the profile name and clear the old data.
        name = model[treeiter][0]
        data[:] = []
        self.liststore.clear()
        
        # Read the data and switch to the other profile.
        data = io.read_profile(main_dir = main_dir, name = name)
        last_profile = name
        for i in data:
            self.liststore.append(i)
        
        # Update the title and save the data.
        self.update_title()
        self.save(show_dialog = False)
    
    
    def add_profile(self, event):
        """Adds a new profile."""
        
        global last_profile
        global data
        
        # Get the name for the new profile.
        new_dlg = ProfileNameDialog(self, "Add Profile")
        response = new_dlg.run()
        name = new_dlg.nam_ent.get_text().lstrip().rstrip()
        new_dlg.destroy()
        
        # If the user did not press OK, don't continue:
        if response != Gtk.ResponseType.OK:
            return
        
        # Validate the name. If the name isn't valid, don't continue.
        validate = utility_functions.validate_profile(main_dir, name)
        if validate != "":
            show_error_dialog(self, "Add Profile", validate)
            return
        
        # Create the new profile and clear the old data.
        io.write_blank_profile(main_dir, name)
        last_profile = name
        data[:] = []
        self.liststore.clear()
        
        # Update the title.
        self.update_title()
    
    
    def remove_profile(self, event):
        """Removes a profile."""
        
        global last_profile
        
        # Get the list of profiles.
        profiles = io.get_profile_list(main_dir, last_profile)
        
        # If there are no other profiles, cancel the action.
        if len(profiles) == 0:
            show_alert_dialog(self, "Remove Profile", "There are no other profiles.")
            return
        
        # Get the profiles to remove.
        rem_dlg = ProfileSelectionDialog(self, "Remove Profile", profiles, select_mode = "multiple")
        response = rem_dlg.run()
        model, treeiter = rem_dlg.treeview.get_selection().get_selected_rows()
        rem_dlg.destroy()
        
        # If the user did not press OK or nothing was selected, don't continue:
        if response != Gtk.ResponseType.OK or treeiter == None:
            return
        
        # Get the profiles.
        profiles = []
        for i in treeiter:
            profiles.append(model[i][0])
        
        # Only show the confirmation dialog if the user wants that.
        if config["confirm_del"]:
            response = show_question_dialog(self, "Remove Profile", "Are you sure you want to remove the profile%s?\n\nThis action cannot be undone." % ("" if len(profiles) == 1 else "s"))
            if response != Gtk.ResponseType.OK:
                return
        
        # Delete the selected profiles.
        for name in profiles:
            shutil.rmtree("%s/profiles/%s" % (main_dir, name))
    
    
    def rename_profile(self, event):
        """Renames the current profile."""
        
        global last_profile
        global data
        
        # Get the new profile name.
        ren_dlg = ProfileNameDialog(self, "Rename Profile")
        response = ren_dlg.run()
        name = ren_dlg.nam_ent.get_text().lstrip().rstrip()
        ren_dlg.destroy()
        
        # If the user did not press OK, don't continue:
        if response != Gtk.ResponseType.OK:
            return
        
        # Validate the name. If the name isn't valid, don't continue.
        validate = utility_functions.validate_profile(main_dir, name)
        if validate != "":
            show_error_dialog(self, "Rename Profile", validate)
            return
            
        # Rename the directory.
        os.rename("%s/profiles/%s" % (main_dir, last_profile), "%s/profiles/%s" % (main_dir, name))
        
        # Clear the old data.
        data[:] = []
        self.liststore.clear()
        
        # Read the data and switch to the new profile.
        data = io.read_profile(main_dir = main_dir, name = name)
        last_profile = name
        for i in data:
            self.liststore.append(i)
        
        # Update the title.
        self.update_title()
    
    
    def merge_profiles(self, event):
        """Merges two profiles."""
        
        global last_profile
        global data
        
        # Get the list of profiles.
        profiles = io.get_profile_list(main_dir, last_profile)
        
        # If there are no other profiles, tell the user and cancel the action.
        if len(profiles) == 0:
            show_alert_dialog(self, "Merge Profiles", "There are no other profiles.")
            return
        
        # Get the profile to merge.
        mer_dlg = ProfileSelectionDialog(self, "Merge Profiles", profiles)
        response = mer_dlg.run()
        model, treeiter = mer_dlg.treeview.get_selection().get_selected()
        mer_dlg.destroy()
        
        # If the user did not press OK or nothing was selected, don't continue:
        if response != Gtk.ResponseType.OK or treeiter == None:
            return
        
        # Get the profile name and read the data.
        name = model[treeiter][0]
        data2 = io.read_profile(main_dir = main_dir, name = name)
        
        # Filter the new data to make sure there are no duplicates.
        new_data = []
        date_col = utility_functions.get_column(data, 0)
        for i in data2:
            
            # If the date already appears, don't include it.
            if i[0] not in date_col:
                new_data.append(i)
        
        # Append, sort, and update the data.
        data += new_data
        data = sorted(data, key = lambda x: datetime.datetime.strptime(x[0], "%d/%m/%Y"))
        self.liststore.clear()
        for i in data:
            self.liststore.append(i)
        
        # Update the title.
        self.update_title()
        
        # Delete the directory of the profile that was merged in.
        shutil.rmtree("%s/profiles/%s" % (main_dir, name))
        
    
    def data_profile_new(self, mode = "Copy"):
        """Copies or moves data to a new profile."""
        
        global data
        
        # If there is no data, tell the user and don't continue.
        if len(data) == 0:
            show_no_data_dialog(self, "%s Data to New Profile" % mode)
            return
        
        # Get the dates.
        dates = []
        dates2 = []
        for i in data:
            dates.append([i[0]])
            dates2.append(i[0])
        
        # Get the profile name.
        new_dlg = ProfileNameDialog(self, "%s Data to New Profile" % mode)
        response = new_dlg.run()
        name = new_dlg.nam_ent.get_text().lstrip().rstrip()
        new_dlg.destroy()
        
        # If the user did not press OK, don't continue:
        if response != Gtk.ResponseType.OK:
            return
        
        # Validate the name. If the name isn't valid, don't continue.
        validate = utility_functions.validate_profile(main_dir, name)
        if validate != "":
            show_error_dialog(self, "%s Data to New Profile" % mode, validate)
            return
        
        # Create the directory and file.
        os.makedirs("%s/profiles/%s" % (main_dir, name))
        new_prof_file = open("%s/profiles/%s/weather" % (main_dir, name), "w")
        pickle.dump([], new_prof_file)
        new_prof_file.close()
            
        # Get the dates to move or copy.
        date_dlg = DateSelectionDialog(self, "%s Data to New Profile" % mode, dates)
        response = date_dlg.run()
        model, treeiter = date_dlg.treeview.get_selection().get_selected_rows()
        date_dlg.destroy()
        
        # If the user did not click OK or nothing was selected, don't continue:
        if response != Gtk.ResponseType.OK or treeiter == None:
            return
        
        # Get the dates.
        ndates = []
        for i in treeiter:
            ndates.append(model[i][0])
        
        # Get the data.
        ndata = []
        for i in range(0, len(data)):
            if data[i][0] in ndates:
                ndata.append(data[i])
        
        # If the user wants to move the data, delete the items in the current profile.
        if mode == "Move":
            
            data = [x for x in data if x[0] not in ndates]
        
            # Reset the list.
            self.liststore.clear()
            for i in data:
                self.liststore.append(i)
        
            # Update the title.
            self.update_title()
        
        # Put the data in the new profile.
        io.write_profile(main_dir = main_dir, name = name, data = ndata)
    
    
    def data_profile_existing(self, mode = "Copy"):
        """Copies or moves data to an existing profile."""
        
        global data
        
        # If there is no data, tell the user and don't continue.
        if len(data) == 0:
            show_no_data_dialog(self, "%s Data to Existing Profile" % mode)
            return
        
        # Get the dates.
        dates = []
        dates2 = []
        for i in data:
            dates.append([i[0]])
            dates2.append(i[0])
        
        # Get the profile list.
        profiles = io.get_profile_list(main_dir, last_profile)
        
        # If there are no other profiles, don't continue.
        if len(profiles) == 0:
            show_alert_dialog(self, "%s Data to Existing Profile" % mode, "There are no other profiles.")
            return
        
        # Get the profile.
        exi_dlg = ProfileSelectionDialog(self, "%s Data to Existing Profile" % mode, profiles)
        response = exi_dlg.run()
        model, treeiter = exi_dlg.treeview.get_selection().get_selected()
        exi_dlg.destroy()
        
        # If the user did not press OK or nothing was selected, don't continue.
        if response != Gtk.ResponseType.OK or treeiter == None:
            return
            
        # Get the profile name.
        name = model[treeiter][0]
        
        # Get the dates to move or copy.
        date_dlg = DateSelectionDialog(self, "%s Data to Existing Profile" % mode, dates)
        response = date_dlg.run()
        model, treeiter = date_dlg.treeview.get_selection().get_selected_rows()
        date_dlg.destroy()
        
        # If the user did not click OK or nothing was selected, don't continue:
        if response != Gtk.ResponseType.OK or treeiter == None:
            return
            
        # Get the dates.
        ndates = []
        for i in treeiter:
            ndates.append(model[i][0])
        
        # Get the data.
        ndata = []
        for i in range(0, len(data)):
            if data[i][0] in ndates:
                ndata.append(data[i])

        # If the user wants to move the data, delete the items in the current profile.
        if mode == "Move":
            
            data = [x for x in data if x[0] not in ndates]
        
            # Reset the list.
            self.liststore.clear()
            for i in data:
                self.liststore.append(i)
        
            # Set the new title.
            self.update_title()
        
        # Load the data.
        data2 = io.read_profile(main_dir = main_dir, name = name)
        
        # Filter the new data to make sure there are no duplicates.
        new_data = []
        date_col = utility_functions.get_column(data2, 0)
        for i in ndata:
            
            # If the date already appears, don't include it.
            if i[0] not in date_col:
                new_data.append(i)
        
        # Append and sort the data.
        data2 += new_data
        data2 = sorted(data2, key = lambda x: datetime.datetime.strptime(x[0], '%d/%m/%Y'))
        
        # Save the data.
        io.write_profile(main_dir = main_dir, name = name, data = data2)
    
    
    def options(self, event):
        """Shows the Options dialog."""
        
        global units
        global config
        current_units = config["units"]
        
        # Get the new options.
        opt_dlg = OptionsDialog(self, config)
        response = opt_dlg.run()
        prefill = opt_dlg.pre_chk.get_active()
        restore = opt_dlg.win_chk.get_active()
        location = opt_dlg.loc_ent.get_text()
        units_ = opt_dlg.unit_com.get_active_text().lower()
        show_dates = opt_dlg.date_chk.get_active()
        show_units = opt_dlg.unit_chk.get_active()
        auto_save = opt_dlg.sav_chk.get_active()
        confirm_del = opt_dlg.del_chk.get_active()
        show_prefill = opt_dlg.pdl_chk.get_active()
        confirm_exit = opt_dlg.cex_chk.get_active()
        opt_dlg.destroy()
        
        # If the user pressed OK, change the options.
        if response == Gtk.ResponseType.OK:
            
            # Set the configuration.
            config["pre-fill"] = prefill
            config["restore" ] = restore
            config["location"] = location
            config["units"] = units_
            config["show_dates"] = show_dates
            config["show_units"] = show_units
            config["auto_save"] = auto_save
            config["confirm_del"] = confirm_del
            config["show_pre-fill"] = show_prefill
            config["confirm_exit"] = confirm_exit
            
            # Configure the units.
            units = launch.get_units(config)
            
            # If the units changed, ask the user if they want to convert the data.
            if current_units != units_:
                response = show_question_dialog(opt_dlg, "Options", "The units have changed from %s to %s.\n\nWould you like to convert the data to the new units?" % (current_units, config["units"]))
                if response == Gtk.ResponseType.OK:
                    
                    # Convert the data.
                    new_data = convert.convert(data, units_)
                    
                    # Update the list.
                    data[:] = []
                    data[:] = new_data[:]
                    self.liststore.clear()
                    for i in data:
                        self.liststore.append(i)
            
            # Add/remove the units, if desired:
            if not config["show_units"]:
                self.temp_col.set_title("Temperature")
                self.prec_col.set_title("Precipitation")
                self.wind_col.set_title("Wind")
                self.humi_col.set_title("Humidity")
                self.airp_col.set_title("Air Pressure")
            else:
                self.temp_col.set_title("Temperature (%s)" % units["temp"])
                self.prec_col.set_title("Precipitation (%s)" % units["prec"])
                self.wind_col.set_title("Wind (%s)" % units["wind"])
                self.humi_col.set_title("Humidity (%)")
                self.airp_col.set_title("Air Pressure (%s)" % units["airp"])
        
        # If the user pressed Reset:
        elif response == 3:
            
            # Confirm that the user wants to reset the options.
            reset = show_question_dialog(opt_dlg, "Options", "Are you sure you want to reset the options to the default values?")
            if response == Gtk.ResponseType.CANCEL:
                return
            
            # Set the config variables.
            config = {"pre-fill": False,
                      "restore": True,
                      "location": "",
                      "units": "metric",
                      "pastebin": "d2314ff616133e54f728918b8af1500e",
                      "show_units": True,
                      "show_dates": True,
                      "auto_save": True,
                      "confirm_del": True,
                      "show_pre-fill": True,
                      "confirm_exit": False}
            
            # Configure the units.
            units = launch.get_units(config)
            
            # If the units changed, ask the user if they want to convert the data.
            if current_units != config["units"]:
                response = show_question_dialog(opt_dlg, "Options", "The units have changed from %s to %s.\n\nWould you like to convert the data to the new units?" % (current_units, config["units"]))
                if response == Gtk.ResponseType.OK:
                    
                    # Convert the data.
                    new_data = convert.convert(data, config["units"])
                    
                    # Update the list.
                    data[:] = []
                    data[:] = new_data[:]
                    self.liststore.clear()
                    for i in data:
                        self.liststore.append(i)
            
            # Reset the main window.
            self.temp_col.set_title("Temperature (%s)" % units["temp"])
            self.prec_col.set_title("Precipitation (%s)" % units["prec"])
            self.wind_col.set_title("Wind (%s)" % units["wind"])
            self.humi_col.set_title("Humidity (%)")
            self.airp_col.set_title("Air Pressure (%s)" % units["airp"])
            
        # Update the title and save the data.
        self.update_title()
        self.save(show_dialog = False, from_options = True)
    
    
    def save(self, show_dialog = True, automatic = True, from_options = False):
        """Saves the data."""
        
        # If the user doesn't want automatic saves, don't continue.
        if automatic and not config["auto_save"] and not from_options:
            return
        
        # Save to the file.
        try:
            # This should save to ~/.weatherlog/[profile name]/weather on Linux.
            data_file = open("%s/profiles/%s/weather" % (main_dir, last_profile), "w")
            pickle.dump(data, data_file)
            data_file.close()
            
        except IOError:
            # Show the error message if something happened, but continue.
            # This one is shown if there was an error writing to the file.
            print("Error saving data file (IOError).")
        
        except (TypeError, ValueError):
            # Show the error message if something happened, but continue.
            # This one is shown if there was an error with the data type.
            print("Error saving data file (TypeError or ValueError).")
        
        # Save the configuration.
        try:
            config_file = open("%s/config" % main_dir, "w")
            json.dump(config, config_file)
            config_file.close()
            
        except IOError:
            # Show the error message if something happened, but continue.
            # This one is shown if there was an error writing to the file.
            print("Error saving configuration file (IOError).")
        
        except (TypeError, ValueError):
            # Show the error message if something happened, but continue.
            # This one is shown if there was an error with the data type.
            print("Error saving configuration file (TypeError or ValueError).")
        
        # Save the last profile.
        try:
            # This should save to ~/.weatherlog/lastprofile on Linux.
            prof_file = open("%s/lastprofile" % main_dir, "w")
            prof_file.write(last_profile)
            prof_file.close()
            
        except IOError:
            # Show the error message if something happened, but continue.
            # This one is shown if there was an error writing to the file.
            print("Error saving profile file (IOError).")
        
        # Show the dialog, if specified.
        if show_dialog:
            show_alert_dialog(self, "Manual Save - %s" % last_profile, "Data has been saved.")
    
    
    def update_title(self):
        """Updates the window title."""
        
        # Update the title.
        if config["show_dates"]:
            self.set_title("WeatherLog - %s - %s to %s" % (last_profile, (data[0][0] if len(data) != 0 else "None"), (data[len(data)-1][0] if len(data) != 0 else "None")))
        else:
            self.set_title("WeatherLog - %s" % last_profile)
    
    
    def reload_current(self, event):
        """Reloads the current data."""
        
        global data
        
        # Show the confirmation dialog, but only if auto-saving isn't turned on.
        if config["auto_save"] == False:
            response = show_question_dialog(self, "Reload Current Data - %s" % last_profile, "Are you sure you want to reload the current data?\n\nUnsaved changes will be lost.")
        else:
            response = Gtk.ResponseType.OK
        
        # If the user wants to continue:
        if response == Gtk.ResponseType.OK:
            
            # Clear the list.
            data[:] = []
            self.liststore.clear()
            
            # Load the data.   
            try:
                # This should be ~/.weatherlog/[profile name]/weather on Linux.
                data_file = open("%s/profiles/%s/weather" % (main_dir, last_profile), "r")
                data = pickle.load(data_file)
                data_file.close()
                
            except IOError:
                # Show the error message, and close the application.
                # This one shows if there was a problem reading the file.
                print("Error reloading data (IOError).")
                data = []
                
            except (TypeError, ValueError):
                # Show the error message, and close the application.
                # This one shows if there was a problem with the data type.
                print("Error reloading data (TypeError or ValueError).")
                data = []
            
            # Update the list.
            for i in data:
                self.liststore.append(i)
        
        # Tell the user the data has been reloaded.
        show_alert_dialog(self, "Reload Current Data - %s" % last_profile, "Data has been reloaded.")
    
    
    def show_about(self, event):
        """Shows the About dialog."""
        
        # Load the icon.
        img_file = open("weatherlog_resources/images/icon_med.png", "rb")
        img_bin = img_file.read()
        img_file.close()
        loader = GdkPixbuf.PixbufLoader.new_with_type("png")
        loader.write(img_bin)
        loader.close()
        pixbuf = loader.get_pixbuf()
        
        # Create the dialog.
        about_dlg = Gtk.AboutDialog()
        
        # Set the details.
        about_dlg.set_title("About WeatherLog")
        about_dlg.set_program_name(TITLE)
        about_dlg.set_logo(pixbuf)
        about_dlg.set_version(VERSION)
        about_dlg.set_comments("WeatherLog is an application for keeping track of the weather\nand getting information about past trends.")
        about_dlg.set_copyright("Copyright (c) 2013-2014 Adam Chesak")
        about_dlg.set_authors(["Adam Chesak <achesak@yahoo.com>"])
        about_dlg.set_license(license_text)
        about_dlg.set_website("http://poultryandprogramming.wordpress.com/")
        about_dlg.set_website_label("http://poultryandprogramming.wordpress.com/")
        
        # Show the dialog.
        about_dlg.show_all()
        about_dlg.run()
        about_dlg.destroy()

    
    def show_help(self, event):
        """Shows the help in a web browser."""
        
        # Open the help file.
        webbrowser.open_new("weatherlog_resources/help/help.html")    
    

    def exit(self, x, y):
        """Closes the application."""
        
        # Save the data.
        self.save(show_dialog = False)
        
        # Show the confirmation dialog, if the user wants that.
        if config["confirm_exit"]:
            response = show_question_dialog(self, "Quit", "Are you sure you want to close the application?")
        
        # If the user wants to continue:
        if config["confirm_exit"] and response == Gtk.ResponseType.OK:
        
            # Save the data.
            self.save(show_dialog = False, from_options = True)
            
            # Close the application.
            Gtk.main_quit()
            return False
        
        # If the user pressed cancel:
        elif config["confirm_exit"] and response == Gtk.ResponseType.CANCEL:
            return True
        
        # If the user doesn't want a confirmation dialog, quit immediately.
        if not config["confirm_exit"]:
            
            # Save the data.
            self.save(show_dialog = False, from_options = True)
            
            # Close the  application.
            Gtk.main_quit()


# Show the window and start the application, but only if there are no exta arguments.
if __name__ == "__main__" and len(sys.argv) == 1:
    
    # Show the window and start the application.
    win = Weather()
    win.connect("delete-event", win.exit)
    win.show_all()
    Gtk.main()

# If there are arguments, run the application from the command line.
elif __name__ == "__main__" and len(sys.argv) > 1:
    
    # Add a row of data:
    if sys.argv[1] == "add":
        command_line.add(data, main_dir, last_profile, sys.argv)
        
    # Remove a row of data:
    elif sys.argv[1] == "remove":
        command_line.remove(data, main_dir, last_profile, sys.argv)
    
    # Clear the current profile:
    elif sys.argv[1] == "clear":
        command_line.clear(main_dir, last_profile)
    
    # Clear all the data:
    elif sys.argv[1] == "clear_all":
        shutil.rmtree(main_dir)
    
    # Switch profiles:
    elif sys.argv[1] == "switch_profile":
        command_line.switch_profile(main_dir, sys.argv[2])
    
    # Add a new profile:
    elif sys.argv[1] == "add_profile":
        command_line.add_profile(main_dir, sys.argv[2])
    
    # Remove an existing profile:
    elif sys.argv[1] == "remove_profile":
        command_line.remove_profile(main_dir, last_profile, sys.argv[2])
    
    # Show the help:
    elif sys.argv[1] == "help":
        webbrowser.open_new("weatherlog_resources/help/help.html")
    
    # Set the options:
    elif sys.argv[1] == "options":
        command_line.options(py_version, config, main_dir)
    
    # Reset the options:
    elif sys.argv[1] == "reset_options":
        command_line.reset_options(config, main_dir)
    
    # Set the window size:
    elif sys.argv[1] == "window_size":
        command_line.window_size(main_dir, sys.argv)
