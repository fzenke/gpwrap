#!/usr/bin/python
# gpwrap - a slim python wrapper to use gnuplot from within Jupyter
# version 0.1
# Copyright 2017 F. Zenke 

import os
import numpy as np
import shutil
import tempfile

class GnuPlotWrapper:
    def __init__(self):
        # TODO add exception management
        self.tmpdir = tempfile.mkdtemp("gpw")
        self.keeptmp = False
        self.verbose = False
        self.datadir = 'data'
        self.datadirpath = "%s/%s"%(self.tmpdir,self.datadir)
        os.mkdir(self.datadirpath)
        self.imgcount = 0
        self.imgdir = 'img'
        self.imgdirpath = "%s/%s"%(self.tmpdir,self.imgdir)
        os.mkdir(self.imgdirpath)
        self.outputdir = self.tmpdir
        self.terminal = 'pdfcairo'
        self.terminal_options = ''
        self.datafiles = dict()
        self.outputfile = 'plot.png'
        self.clear()

    def __del__(self):
        if not self.keeptmp:
            self.log("Removing temp dir %s"%self.tmpdir)
            shutil.rmtree(self.tmpdir)

    def clear(self):
        self.plot_code = []
        self.plot_command = ""

    def log(self,msg):
        if self.verbose:
            print(msg)
        
        
    def sanify_filename(self, filename):
        keepcharacters = ('.','_','-')
        return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()
        
    def import_data(self, data, name=None):
        if name is None:
            name = "default%i"%len(self.datafiles)
            # name = "default"
        filename = self.sanify_filename(name)
        datafilename = '%s/%s.dat'%(self.datadirpath,filename)
        self.log("Wrinting data to %s"%datafilename)
        self.datafiles[name] = datafilename
        np.savetxt(datafilename, data)  
        return name

    def import_xydata(self, xdata, ydata, name=None):
        return self.import_data( np.vstack([diag_gg,diag_gu]).T, name )
    
    def cm(self, command):
        self.plot_code.append(command)
    
    def get_term_commands(self):
        cmds = []
        cmds.append('set out \'%s/%s\'\n'%(self.outputdir,self.outputfile))
        cmds.append('set term %s %s\n'%(self.terminal, self.terminal_options))
        return cmds
        
    def write_to_file(self, filename):
        f = open(filename,'wb')
        commands = self.get_term_commands()
        commands.extend(self.plot_code)
        for l in commands:
            f.write("%s\n"%(l))

        f.write("%s\n"%self.plot_command)
        f.write('unset out\n')
        f.close()
        
    def execute(self):
        scriptfile = "%s/plot.gnu"%(self.tmpdir)
        self.log("Writing to %s"%scriptfile)
        self.write_to_file(scriptfile)
        self.log("Plotting ... ")
        return os.system("gnuplot %s"%scriptfile)

    def saveplot(self, filename):
        bn, ext = os.path.splitext(filename)
        if ext=='.pdf':
            self.terminal = 'pdfcairo'
        else: # png
            self.terminal = 'pngcairo'

        rc = self.execute()
        if rc:
            print("Error in gnuplot script")
            # TODO exception handling
        else:
            shutil.copy('%s/%s'%(self.outputdir,self.outputfile),filename)

    def show(self):
        imgfilename = "%s/plot%i.png"%(self.imgdirpath, self.imgcount)
        self.imgcount += 1
        self.saveplot(imgfilename)
        return imgfilename

    def title(self, title_str):
        self.cm("set title '%s'"%title_str) 

    def xlabel(self, label_str=""):
        self.cm("set xlabel '%s'"%label_str) 

    def ylabel(self, label_str=""):
        self.cm("set ylabel '%s'"%label_str) 

    def axlabels(self, xlabel, ylabel):
        self.xlabel(xlabel)
        self.ylabel(ylabel)

    def key(self, fmt="samplen=2"):
        self.cm("set key %s"%(fmt) ) 

    def nokey(self):
        self.cm("unset key" ) 

    def plot(self, data, fmt="with points"):
        """ Takes a numpy array or the name of a data file and plots it using the fmt specifier fmt

        args:
            data a numpy array or a string which refers to datafile name created with import_data
            fmt a format string which is the gnuplot command line behind the filename of the plot command
        """
        if isinstance(data, str):
            dfname = data
        else:
            dfname = self.import_data(data)

        pc = self.plot_command
        if len(pc) == 0:
            pc = 'plot '
        else:
            pc += ',\\\n     '

        pc += '\'%s/%s\''%(self.datadirpath, os.path.basename(self.datafiles[dfname]))
        pc += ' %s'%fmt
        self.plot_command = pc

    # def plot_batch(self, xdata, ydata, fmt="with points"):



if __name__ == "__main__": 
    gp = GnuPlotWrapper()
    dat = np.random.rand(100,2)
    gp.nokey()
    gp.axlabels("Foo (ms)", "Bar (ms)")
    gp.plot(dat, "with points pt 7 lc -1")
    gp.saveplot('foo.pdf')
    # gp.saveplot('foo.png')

