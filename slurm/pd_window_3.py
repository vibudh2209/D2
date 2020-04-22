import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import glob
import os
from os.path import expanduser
import glib
from subprocess import check_output

home_path = expanduser("~")
user = home_path.split('/')[-1]

pd_path = '/groups/cherkasvgrp/share/progressive_docking/pd_python'

class ourwindow3(Gtk.Window):

    def __init__(self,file_name,protein,grid_file,docking_software):
        Gtk.Window.__init__(self, title="Deep Docking")
        Gtk.Window.set_default_size(self, 400,325)
        Gtk.Window.set_position(self, Gtk.WindowPosition.CENTER)
        

        self.file_name = file_name
        self.protein = protein
        self.grid_file = grid_file
        self.docking_software = docking_software

        self.new_wind_3()

        combobox1 = Gtk.ComboBox()
        store1 = Gtk.ListStore(str)
        cell = Gtk.CellRendererText()
        combobox1.pack_start(cell,True)
        combobox1.add_attribute(cell,'text',0)


        store1.append(['19'])
        store1.append(['64'])
        store1.append(['32'])
        #store1.append(['1'])

        combobox1.set_model(store1)
        combobox1.connect('changed',self.on_changed)
        combobox1.set_active(0)

        combobox_label = Gtk.Label('Number of CPUs')

        combobox2 = Gtk.ComboBox()
        store2 = Gtk.ListStore(str)
        cell = Gtk.CellRendererText()
        combobox2.pack_start(cell,True)
        combobox2.add_attribute(cell,'text',0)

        store2.append(['130'])
        store2.append(['100'])
        store2.append(['24'])
        store2.append(['48'])
        store2.append(['64'])
        store2.append(['1'])

        combobox2.set_model(store2)
        combobox2.connect('changed',self.on_changed_2)
        combobox2.set_active(0)

        combobox_label_2 = Gtk.Label('#glide licenses per job (total X3)')      
 

        iteration_label = Gtk.Label('Current iteration number')
        phase_label = Gtk.Label('Phase to perform')

        cover_box = Gtk.Box(spacing=10)
        cover_box.set_homogeneous(True)
        left_left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=10)
        left_left_box.set_homogeneous(False)
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=10)
        left_box.set_homogeneous(False)
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=10)
        right_box.set_homogeneous(True)
        right_right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=10)
        right_right_box.set_homogeneous(True)

        self.add(cover_box)

        cover_box.pack_start(left_left_box,False,True,0)
        cover_box.pack_start(left_box,False,True,0)
        cover_box.pack_start(right_box,True,True,0)
        cover_box.pack_start(right_right_box,True,True,0)
        #cover_box.pack_end(outer_box,True,True,0)

        button1 = Gtk.Button("phase_1")
        button1.connect("clicked", self.on_button_phase)
        button2 = Gtk.Button("phase_2")
        button2.connect("clicked", self.on_button_phase)
        button3 = Gtk.Button("phase_3")
        button3.connect("clicked", self.on_button_phase)
        button4 = Gtk.Button("phase_4")
        button4.connect("clicked", self.on_button_phase)
        button5 = Gtk.Button("phase_5")
        button5.connect("clicked", self.on_button_phase)

        button6 = Gtk.Button("phase_1_check")
        button6.connect("clicked", self.on_button_check)
        button7 = Gtk.Button("phase_2_check")
        button7.connect("clicked", self.on_button_check)
        button8 = Gtk.Button("phase_3_check")
        button8.connect("clicked", self.on_button_check)
        button9 = Gtk.Button("phase_4_check")
        button9.connect("clicked", self.on_button_check)
        button10 = Gtk.Button("phase_5_check")
        button10.connect("clicked", self.on_button_check)

        button11=Gtk.Button("Refresh")
        button11.connect("clicked", self.on_button_11)

        button12=Gtk.Button("Phase_f")
        button12.connect("clicked", self.on_button_12)

        button13=Gtk.Button("phase_f_check")
        button13.connect("clicked", self.on_button_check)

        button14=Gtk.Button("latest status")
        button14.connect("clicked", self.latest_stats)

        button15=Gtk.Button("slurm clearer")
        button15.connect("clicked", self.clear_slurm)

        self.log = {}
        self.update_latest_data()

        self.it_label = Gtk.Label(str(self.log['iteration_no']))
        self.phase_label = Gtk.Label(str(self.log['phase_no']))

        #self.sanity_check()
        left_left_box.pack_start(button11,False,True,0)
        left_left_box.pack_start(button12,False,True,0)
        left_left_box.pack_start(button13,False,True,0)
        left_left_box.pack_start(button14,False,True,0)
        left_left_box.pack_start(button15,False,True,0)

        left_box.pack_start(combobox_label,False,True,0)
        left_box.pack_start(combobox1,False,True,0)

        left_box.pack_start(combobox_label_2,False,True,0)
        left_box.pack_start(combobox2,False,True,0)

        left_box.pack_start(iteration_label,False,True,0)
        left_box.pack_start(self.it_label,False,True,0)

        left_box.pack_start(phase_label,False,True,0)
        left_box.pack_start(self.phase_label,False,True,0)

        right_box.pack_start(button1,True,True,0)
        right_right_box.pack_start(button6,True,True,0)
        right_box.pack_start(button2,True,True,0)
        right_right_box.pack_start(button7,True,True,0)
        right_box.pack_start(button3,True,True,0)
        right_right_box.pack_start(button8,True,True,0)
        right_box.pack_start(button4,True,True,0)
        right_right_box.pack_start(button9,True,True,0)
        right_box.pack_start(button5,True,True,0)
        right_right_box.pack_start(button10,True,True,0)



    def new_wind_3(self):
    	win = Gtk.Window()
    	win.set_default_size(300,200)
    	win.set_position(Gtk.WindowPosition.CENTER)
    	cover_box = Gtk.Box(spacing=10)
    	cover_box.set_homogeneous(True)
    	the_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=10)
        the_box.set_homogeneous(False)
        cover_box.pack_start(the_box,False,True,0)
    	output = check_output(["sinfo"])
    	output = output.split('\n')
    	labels = []
    	for indstr in output:
    		print(indstr)
    		labels.append(Gtk.Label(indstr))
    	#label = Gtk.Label(labs)
    	for indlabs in labels:
    		the_box.pack_start(indlabs,True,True,0)
    	#cover_box.pack_start(label,True,True,0)
    	win.add(cover_box)
    	win.show_all()
    	win.set_keep_above(True)

    def clear_slurm(self,button):
    	for f in glob.glob('slurm*'):
    		tmp = f.split('-')[-1].split('.')[0]
    		if os.system('squeue|grep '+tmp)!=0:
    			try:
    				os.remove(f)
    			except:
    				pass

    
    def latest_stats(self,button):
    	self.update_latest_data()
    	if self.log['iteration_no']==1:
    		self.new_wind('All molecules are left')
    	else:
    		print(self.file_name+'/'+self.protein+'/iteration_'+str(self.log['iteration_no']-1)+'/morgan_1024_predictions/passed_file_ct.txt')
    		with open(self.file_name+'/'+self.protein+'/iteration_'+str(self.log['iteration_no']-1)+'/morgan_1024_predictions/passed_file_ct.txt') as ref:
    			nom=0
    			for line in ref:
    				nom+=int(line.rstrip().split(',')[-1])
    			print(nom)
	    	with open(self.file_name+'/'+self.protein+'/iteration_'+str(self.log['iteration_no']-1)+'/best_model_stats.txt') as ref:
	    		ref.readline()
	    		pr_left = ref.readline().rstrip().split(',')[-1]
	    	self.new_wind('Predicted: '+str(int(float(pr_left)))+' actual: '+str(int(nom)))


    def on_changed(self,widget):
    	#self.label.set_label(widget.get_active_text())
    	tree_iter = widget.get_active_iter()
    	if tree_iter is not None:
    		model = widget.get_model()
    		self.t_pro = model[tree_iter][0]
    		if self.t_pro=='64':
    			x = os.system('sinfo|grep normal|grep idle')
    			if x ==0:
    				print(self.t_pro)
    			else:
    				self.new_wind('No 64 nodes are empty please choose a lower number')
    				self.t_pro = 64
    		if self.t_pro=='24':
    			x = os.system('sinfo|grep gpu|grep idle')
    			if x ==0:
    				print(self.t_pro)
    			else:
    				self.new_wind('No 24 nodes are empty please choose a lower number')
    				self.t_pro = 24

    def on_changed_2(self,widget):
    	#self.label.set_label(widget.get_active_text())
    	tree_iter = widget.get_active_iter()
    	if tree_iter is not None:
    		model = widget.get_model()
    		self.l_pro = model[tree_iter][0]
    	print(self.l_pro)
    

    def on_button_11(self,button):
    	self.update_latest_data()

    def on_button_12(self,button):
    	self.update_latest_data()
    	if self.log['iteration_no']==1:
    		self.new_wind('No iterations are finished')
    	else:
    		for i in range(1,6):
    			if self.phase_test('phase_'+str(i)+'.sh',self.log['iteration_no'])[1] == 'phase_'+str(i)+'_running':
    				self.new_wind('phase_'+str(i)+' for iteration '+str(self.log['iteration_no'])+' is still running')
    				return 0
    				break
    		with open(self.file_name+'/'+self.protein+'/iteration_'+str(self.log['iteration_no']-1)+'/morgan_1024_predictions/passed_file_ct.txt') as ref:
    			nom=0
    			for line in ref:
    				nom+=int(line.rstrip().split(',')[-1])
    			print(nom)
    		#os.system('python count_mols.py -pt '+self.protein+' -it '+str(self.log['iteration_no']-1)+' -fp '+self.file_name+' -t_pos '+str(self.t_pro))
    		#with open(self.file_name+'/'+self.protein+'/iteration_'+str(self.log['iteration_no']-1)+'/morgan_1024_predictions/molecule_count.csv') as ref:
    		#	nom = ref.readline().rstrip()
    		self.new_wind_2('Total molecules left are '+str(nom)+' do you want to continue?')



    def new_wind_2(self,labs):
    	self.new_win = Gtk.Window()
    	self.new_win.set_default_size(10,10)
    	self.new_win.set_position(Gtk.WindowPosition.CENTER)
    	cover_box = Gtk.Box(spacing=10)
    	cover_box.set_homogeneous(False)
    	left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=10)
    	left_box.set_homogeneous(False)
    	right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=10)
    	right_box.set_homogeneous(False)
    	label = Gtk.Label(labs)
    	cover_box.pack_start(label,False,True,0)
    	cover_box.pack_start(left_box,False,True,0)
    	cover_box.pack_start(right_box,False,True,0)
    	button1 = Gtk.Button("Yes")
    	button1.connect("clicked", self.on_button_dec)
    	button2 = Gtk.Button("No")
    	button2.connect("clicked", self.on_button_dec)
    	left_box.pack_start(button1,False,True,0)
    	right_box.pack_start(button2,False,True,0)
    	self.new_win.add(cover_box)
    	self.new_win.show_all()
    	self.new_win.set_keep_above(True)

    def on_button_dec(self,button):
    	if button.get_label()=='Yes':
    		self.new_win.destroy()
    		try:
    			os.mkdir(self.file_name+'/'+self.protein+'/'+'after_iteration')
    		except:
    			pass
    		with open(self.file_name+'/'+self.protein+'/'+'after_iteration'+'/'+'phase_f.sh','w') as ref:
    			ref.write('phase_f.sh')
    		print("Starting final phase")
    		if self.docking_software=='GLIDE':
    			os.system('python phase_maker.py '+'-tpos '+str(self.t_pro)+' -pf '+'final_phase')
    			os.system('sbatch final_phase.sh '+str(self.log['iteration_no']-1)+' '+str(self.t_pro)+' '+str(self.file_name)+' '+str(self.protein)+' '+str(3*int(self.l_pro)))
    			print(3*int(self.l_pro))
    		elif self.docking_software=='OEDDOCKING':
    			#os.system('python phase_maker.py '+'-tpos '+str(self.t_pro)+' -pf '+name)
    			#os.system('python phase_maker.py '+'-tpos '+str(self.t_pro)+' -pf '+name)
    			os.system('sbatch final_phase_alternate.sh '+str(self.log['iteration_no']-1)+' '+str(self.t_pro)+' '+str(self.file_name)+' '+str(self.protein))
    	else:
    		self.new_win.destroy()


    def update_latest_data(self):
    	all_phase_files = {}
    	tmp = []
    	self.log = {}
    	itn =len(glob.glob(self.file_name+'/'+str(self.protein)+'/iteration_*'))
    	for f in range(1,itn+1):
    		t_phases =len(glob.glob(self.file_name+'/'+str(self.protein)+'/iteration_'+str(f)+'/phase_*'))
    		print(glob.glob(self.file_name+'/'+str(self.protein)+'/iteration_'+str(f)+'/phase_*'))
    		print(t_phases)
    		for g in range(1,t_phases+1):
    			a,b = self.phase_test('phase_'+str(g)+'.sh',f)
    			if not a:
    				break
    			else:
    				tmp.append([f,g])
    	print tmp
    	if len(tmp)==0:
    		self.log['iteration_no'] = 1
    		self.log['phase_no'] = 1
    	else:
    		f,g = tmp[-1]
    		if g!=5:
    			self.log['iteration_no'] = f
    			self.log['phase_no'] = g+1
    		else:
    			self.log['iteration_no'] = f+1
    			self.log['phase_no'] = 1
    	try:
    		self.phase_label.set_label(str(self.log['phase_no']))
    		self.it_label.set_label(str(self.log['iteration_no']))
    	except:
    		pass



    def phase_test(self,name,iteration):
        file_name = self.file_name
        protein = self.protein
        all_files= {}
        print(name)
        all_files[name] = 0
        if name=='phase_f.sh':
        	try:
        		for f in glob.glob(file_name+'/'+protein+'/after_iteration'+'/*.sh'):
        			try:
        				all_files[f.split('/')[-1]] +=1
        			except:
        				pass
        		to_pass = True
        		for keys in all_files.keys():
        			if all_files[keys] !=1:
        				print(keys)
        				to_pass = False
        				break

        		if to_pass==False:
        			return False,name[:7]+'_never_started'
        		else:
        			jobids = {}
        			with open(file_name+'/'+protein+'/after_iteration'+'/'+name,'r') as ref:
        				for line in ref:
        					if os.system('squeue -u '+user+' |grep '+line.rstrip())==0:
        						return False,name[:7]+'_running'
        				return True,name[:7]+'_finished'
        	except:
        		return False,name[:7]+'_never_started'
        try:
        	for f in glob.glob(file_name+'/'+protein+'/iteration_'+str(iteration)+'/*.sh'):
        		try:
        			all_files[f.split('/')[-1]] +=1
        		except:
        			pass
        	to_pass = True
        	for keys in all_files.keys():
        		if all_files[keys] !=1:
        			print(keys)
        			to_pass = False
        			break

        	if to_pass==False:
        		return False,name[:7]+'_never_started'
        	else:
        		jobids = {}
        		with open(file_name+'/'+protein+'/iteration_'+str(iteration)+'/'+name,'r') as ref:
        			for line in ref:
        				if os.system('squeue -u '+user+' |grep '+line.rstrip())==0:
        					return False,name[:7]+'_running'
        			return True,name[:7]+'_finished'
        except:
        	self.new_wind('Start with phase 1 for iteration '+str(iteration))
        	return False,name[:7]+'_never_started'

    

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

    def on_button_phase(self,button):
    	name = button.get_label()
    	# Check previous phase if completed, check whether current phase is running/finished, then run
    	self.update_latest_data()
    	iteration_no = self.log['iteration_no']
    	asked_phase = int(name.split('_')[-1])
    	if asked_phase==1 and iteration_no==1:
    		prev_to_check = None
    		it_to_use = iteration_no
    		prev_pass = True
    	elif asked_phase==1 and iteration_no!=1:
    		prev_to_check = 5
    		it_to_use = iteration_no-1
    		prev_pass = self.phase_test('phase_'+str(prev_to_check)+'.sh',it_to_use)[0]
    	else:
    		prev_to_check = asked_phase-1
    		it_to_use = iteration_no
    		prev_pass = self.phase_test('phase_'+str(prev_to_check)+'.sh',it_to_use)[0]
    	if prev_pass:
    		a,b = self.phase_test(name+'.sh',iteration_no)
    		if not a:
    			if b==name+'_running':
    				self.new_wind(name+' is currently running for iteration '+str(iteration_no))
    			else:
    				try:
    					os.mkdir(self.file_name+'/'+self.protein+'/'+'iteration_'+str(iteration_no))
    				except:
    					pass
    				with open(self.file_name+'/'+self.protein+'/'+'iteration_'+str(iteration_no)+'/'+name+'.sh','w') as ref:
    					ref.write(name)
    				print("Starting "+name+" for iteration "+str(iteration_no))
    				if name=='phase_1' or name=='phase_2' or name=='phase_4':
    					os.system('python phase_maker.py '+'-tpos '+str(self.t_pro)+' -pf '+name)
    					os.system('sbatch '+name+'.sh '+str(iteration_no)+' '+str(self.t_pro)+' '+str(self.file_name)+' '+str(self.protein))
    				elif name=='phase_3':
    					if self.docking_software=='GLIDE':
    						os.system('sbatch '+name+'.sh '+str(iteration_no)+' '+str(self.l_pro)+' '+str(self.file_name)+' '+str(self.protein))
    					elif self.docking_software=='OEDDOCKING':
    						os.system('python phase_maker.py '+'-tpos '+str(self.t_pro)+' -pf '+name+'_alternate_1')
    						os.system('python phase_maker.py '+'-tpos '+str(self.t_pro)+' -pf '+name+'_alternate')
    						os.system('sbatch '+name+'_alternate.sh '+str(iteration_no)+' '+str(self.t_pro)+' '+str(self.file_name)+' '+str(self.protein))
    				elif name=='phase_5':
    					os.system('sbatch '+name+'.sh '+str(iteration_no)+' '+str(self.file_name)+' '+str(self.protein))

    		else:
    			self.new_wind(name+' is complete for iteration '+str(iteration_no))
    	else:
    		self.new_wind('Phase '+str(prev_to_check)+' for iteration '+str(it_to_use)+' is not complete')


    def on_button_check(self,button):
    	name=('_').join(button.get_label().split('_')[:-1])
    	self.update_latest_data()
    	iteration_no = self.log['iteration_no']
    	a,b = self.phase_test(name+'.sh',iteration_no)
    	if a:
    		self.new_wind(name+' is complete')
    	elif b==name[:7]+'_running':
    		self.new_wind(name+' is still running')
    	elif b==name[:7]+'_never_started':
    		self.new_wind(name+' never started')

    
	
    #def on_button1(self,button):

#window = ourwindow3('/home/vagrawal','new_prr','/home/vagrawal/grid_file.zip')        
#window.connect("delete-event", Gtk.main_quit)

#window.show_all()
#Gtk.main()

