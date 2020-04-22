import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class ourwindow2(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Deep Docking")
        Gtk.Window.set_default_size(self, 400,325)
        Gtk.Window.set_position(self, Gtk.WindowPosition.CENTER)
        
        #outer_box = Gtk.VBox(False,spacing=10)
        #self.add(self.outter_box)

        self.morgan_directory = '/groups/cherkasvgrp/share/progressive_docking/ZINC_15_morgan_1024_2D'
        self.smile_directory = '/groups/cherkasvgrp/share/progressive_docking/ZINC_15_2D_SMILES'
        self.sdf_directory = '/groups/cherkasvgrp/share/progressive_docking/ZINC_15_3D'
        self.docking_software = 'GLIDE'
        self.nhp = 48
        self.n_mols = '3000000'

        self.text=Gtk.Entry()
        self.text.set_activates_default(True)


        button = Gtk.Button("Next")
        button.connect("clicked", self.on_file_open_activate)
        
        cover_box = Gtk.Box(spacing=10)
        cover_box.set_homogeneous(False)
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=10)
        left_box.set_homogeneous(False)
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=10)
        right_box.set_homogeneous(False)

        self.add(cover_box)

        cover_box.pack_start(left_box,True,True,0)
        cover_box.pack_start(right_box,True,True,0)
        #cover_box.pack_end(outer_box,True,True,0)

        
        label=Gtk.Label("name of the protein")
        left_box.pack_start(label,False,True,0)
        right_box.pack_start(self.text,False,True,0)

        label=Gtk.Label("")
        left_box.pack_start(label,False,True,0)

        combobox1 = Gtk.ComboBox()
        store1 = Gtk.ListStore(str)
        cell = Gtk.CellRendererText()
        combobox1.pack_start(cell,True)
        combobox1.add_attribute(cell,'text',0)

        store1.append(['GLIDE'])
        store1.append(['OEDDOCKING'])

        combobox1.set_model(store1)
        combobox1.connect('changed',self.on_changed)
        combobox1.set_active(0)

        combobox_label = Gtk.Label('Which Docking Software')

        left_box.pack_start(combobox_label,False,True,0)
        left_box.pack_start(combobox1,False,True,0)

        combobox2 = Gtk.ComboBox()
        store2 = Gtk.ListStore(str)
        cell = Gtk.CellRendererText()
        combobox2.pack_start(cell,True)
        combobox2.add_attribute(cell,'text',0)

        store2.append(['24'])
        store2.append(['48'])
        store2.append(['72'])
        store2.append(['144'])

        combobox2.set_model(store2)
        combobox2.connect('changed',self.on_changed2)
        combobox2.set_active(0)

        combobox_label2 = Gtk.Label('How many hyperparamaters')

        combobox3 = Gtk.ComboBox()
        store3 = Gtk.ListStore(str)
        cell = Gtk.CellRendererText()
        combobox3.pack_start(cell,True)
        combobox3.add_attribute(cell,'text',0)

        store3.append(['3000000'])
        store3.append(['2000000'])
        store3.append(['1000000'])
        store3.append(['500000'])
        store3.append(['250000'])
        store3.append(['6000000'])
        store3.append(['9000000'])

        combobox3.set_model(store3)
        combobox3.connect('changed',self.on_changed_3)
        combobox3.set_active(0)

        combobox_label_3 = Gtk.Label('Sample size')   

        left_box.pack_start(combobox_label2,False,True,0)
        left_box.pack_start(combobox2,False,True,0)

        left_box.pack_start(combobox_label_3,False,True,0)
        left_box.pack_start(combobox3,False,True,0)

        #label=Gtk.Label("path to grid file")
        button1 = Gtk.Button("Grid file")
        button1.connect("clicked", self.on_file_open_activate2)
        #left_box.pack_start(label,False,True,0)
        right_box.pack_start(button1,False,True,0)


        
        button2 = Gtk.Button("Morgan Directory")
        button2.connect("clicked", self.on_file_open_activate3)
        right_box.pack_start(button2,False,True,0)

        
        button3 = Gtk.Button("Smile Directory")
        button3.connect("clicked", self.on_file_open_activate4)
        right_box.pack_start(button3,False,True,0)

        
        button4 = Gtk.Button("Sdf Directory")
        button4.connect("clicked", self.on_file_open_activate5)
        right_box.pack_start(button4,False,True,0)

        hbox = Gtk.ButtonBox.new(Gtk.Orientation.HORIZONTAL)
        hbox.set_layout(Gtk.ButtonBoxStyle.SPREAD) 

        right_box.pack_end(hbox, False, True, 0)

        #hbox.add(self.text)
        hbox.add(button)


    def on_changed(self,widget):
    	#self.label.set_label(widget.get_active_text())
    	tree_iter = widget.get_active_iter()
    	if tree_iter is not None:
    		model = widget.get_model()
    		self.docking_software = model[tree_iter][0]
    		print(self.docking_software)

    def on_changed2(self,widget):
    	#self.label.set_label(widget.get_active_text())
    	tree_iter = widget.get_active_iter()
    	if tree_iter is not None:
    		model = widget.get_model()
    		self.nhp = model[tree_iter][0]
    		print(self.nhp)
    	

    def on_changed_3(self,widget):
    	#self.label.set_label(widget.get_active_text())
    	tree_iter = widget.get_active_iter()
    	if tree_iter is not None:
    		model = widget.get_model()
    		self.n_mols = model[tree_iter][0]
    	print(self.n_mols)

    def on_file_open_activate3(self, menuitem, data=None):
		fcd = Gtk.FileChooserDialog("Open...",
             None,
             Gtk.FileChooserAction.SELECT_FOLDER,
             (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
  		response = fcd.run()
  		if response == Gtk.ResponseType.OK:
			print "Selected filepath: %s" % fcd.get_filename()
			self.morgan_directory = fcd.get_filename()
			fcd.destroy()
		if response == Gtk.ResponseType.CANCEL:
			fcd.destroy()
		try:
			print(self.morgan_directory)
		except:
			pass

    def on_file_open_activate4(self, menuitem, data=None):
		fcd = Gtk.FileChooserDialog("Open...",
             None,
             Gtk.FileChooserAction.SELECT_FOLDER,
             (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
  		response = fcd.run()
  		if response == Gtk.ResponseType.OK:
			print "Selected filepath: %s" % fcd.get_filename()
			self.smile_directory = fcd.get_filename()
			fcd.destroy()
		if response == Gtk.ResponseType.CANCEL:
			fcd.destroy()
		try:
			print(self.smile_directory)
		except:
			pass

    def on_file_open_activate5(self, menuitem, data=None):
		fcd = Gtk.FileChooserDialog("Open...",
             None,
             Gtk.FileChooserAction.SELECT_FOLDER,
             (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
  		response = fcd.run()
  		if response == Gtk.ResponseType.OK:
			print "Selected filepath: %s" % fcd.get_filename()
			self.sdf_directory = fcd.get_filename()
			fcd.destroy()
		if response == Gtk.ResponseType.CANCEL:
			fcd.destroy()
		try:
			print(self.sdf_directory)
		except:
			pass

    def new_wind(self,labs):
    	win = Gtk.Window()
    	win.set_default_size(100,50)
    	win.set_position(Gtk.WindowPosition.CENTER)
    	cover_box = Gtk.Box(spacing=10)
    	cover_box.set_homogeneous(True)
    	label = Gtk.Label(labs)
    	cover_box.pack_start(label,True,True,0)
    	win.add(cover_box)
    	win.show_all()
    	win.set_keep_above(True)

    def on_file_open_activate(self, button):
		self.port = self.text.get_text()
		if self.port=='':
			self.new_wind('Please fill the information')
		else:
			try:
				print(self.grid_file_name)
				self.destroy()
				Gtk.main_quit()
			except:
				self.new_wind('Please fill the information')


    def on_file_open_activate2(self, menuitem, data=None):
		fcd = Gtk.FileChooserDialog("Open...",
             None,
             Gtk.FileChooserAction.OPEN,
             (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
  		response = fcd.run()
  		if response == Gtk.ResponseType.OK:
			print "Selected filepath: %s" % fcd.get_filename()
			self.grid_file_name = fcd.get_filename()
			fcd.destroy()
		if response == Gtk.ResponseType.CANCEL:
			fcd.destroy()
		try:
			print(self.grid_file_name)
		except:
			pass

#window = ourwindow2()        
#window.connect("delete-event", Gtk.main_quit)
#window.show_all()
#Gtk.main()

