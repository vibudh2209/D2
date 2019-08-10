#!/usr/bin/python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from subprocess import call
from pd_window_2 import ourwindow2
from pd_window_3 import ourwindow3
from os.path import expanduser
import sys

home_path = expanduser("~")
pd_path = '/groups/cherkasvgrp/share/progressive_docking/pd_python'

class ourwindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Progressie Docking")
        Gtk.Window.set_default_size(self, 400,325)
        Gtk.Window.set_position(self, Gtk.WindowPosition.CENTER)
        
        #grid = Gtk.Grid()
        #self.add(grid)
        self.outter_box = Gtk.VBox(True,spacing=10)
        self.add(self.outter_box)

        button1 = Gtk.Button("New Project")
        button1.connect("clicked", self.on_file_open_activate)
        button2 = Gtk.Button("Load Project")
        button2.connect("clicked", self.on_file_open_activate_2)
        #button3 = Gtk.Button("Something")

           
        hbox = Gtk.ButtonBox.new(Gtk.Orientation.HORIZONTAL)
        hbox.set_layout(Gtk.ButtonBoxStyle.SPREAD) 

        self.outter_box.pack_start(hbox, False, True, 0)

        hbox.add(button1)
        hbox.add(button2)
        #hbox.add(button3)


    def on_file_open_activate(self, menuitem, data=None):
		fcd = Gtk.FileChooserDialog("Open...",
             None,
             Gtk.FileChooserAction.SELECT_FOLDER,
             (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
  		response = fcd.run()
  		if response == Gtk.ResponseType.OK:
			print "Selected filepath: %s" % fcd.get_filename()
			self.file_name = fcd.get_filename()
			fcd.destroy()
		if response == Gtk.ResponseType.CANCEL:
			fcd.destroy()
		self.new_project =True
		self.destroy()
		Gtk.main_quit()
		#window.show_all()
		#print(window.port)
		#self.show()

    def on_file_open_activate_2(self, menuitem, data=None):
		fcd = Gtk.FileChooserDialog("Open...",
             None,
             Gtk.FileChooserAction.SELECT_FOLDER,
             (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
  		response = fcd.run()
  		if response == Gtk.ResponseType.OK:
			print "Selected filepath: %s" % fcd.get_filename()
			self.file_name = fcd.get_filename()
			fcd.destroy()
		if response == Gtk.ResponseType.CANCEL:
			fcd.destroy()
		self.new_project = False
		self.destroy()
		Gtk.main_quit()

    def on_delete_event(self):
    	self.hide()
    	self.destroy_app()
    	return True


window = ourwindow()        
window.connect("delete-event", Gtk.main_quit)

window.show_all()
Gtk.main()

try:
	new_pr = window.new_project
	print(new_pr)
except:
	sys.exit()

if new_pr:
	try:
		file_name = window.file_name
	except:
		sys.exit()
else:
	try:
		protein = window.file_name.split('/')[-1]
		print(protein)
		file_name = ('/').join(window.file_name.split('/')[:-1])
		print(file_name)
	except:
		sys.exit()
	with open(file_name+'/'+protein+'/logs.txt','r') as ref:
		file_name = ref.readline().rstrip()
		protein = ref.readline().rstrip()
		grid_file = ref.readline().rstrip()
		ref.readline()
		ref.readline()
		ref.readline()
		docking_software = ref.readline().rstrip()


if new_pr:
	window = ourwindow2()
	window.connect("delete-event", Gtk.main_quit)
	window.show_all()
	Gtk.main()
	morgan_file = window.morgan_directory
	smile_file = window.smile_directory
	sdf_file = window.sdf_directory
	docking_software = window.docking_software
	nhp = window.nhp
	n_mols = window.n_mols
	try:
		protein = window.port
		grid_file = window.grid_file_name
		call(['python',pd_path+'/start_project.py','-fp',file_name,'-pn',protein])
	except:
		sys.exit()
	with open(file_name+'/'+protein+'/logs.txt','w') as ref:
		ref.write(file_name+'\n')
		ref.write(protein+'\n')
		ref.write(grid_file+'\n')
		ref.write(morgan_file+'\n')
		ref.write(smile_file+'\n')
		ref.write(sdf_file+'\n')
		ref.write(docking_software+'\n')
		ref.write(str(nhp)+'\n')
		ref.write(str(n_mols)+'\n')
	window = ourwindow3(file_name,protein,grid_file,docking_software)        
	window.connect("delete-event", Gtk.main_quit)
	window.show_all()
	Gtk.main()
else:
	window = ourwindow3(file_name,protein,grid_file,docking_software)        
	window.connect("delete-event", Gtk.main_quit)
	window.show_all()
	Gtk.main()
		















