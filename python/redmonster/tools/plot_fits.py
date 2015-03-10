# GUI used for quickly plotting BOSS spectra.  Also allows overplotting of best-fit template as
# determined by redmonster pipeline.  Sort of a redmonster version of plotspec.pro, though currently
# with less bells and whistles.
#
# Tim Hutchinson, University of Utah, April 2014
# Signifcantly updated by TH, October 2014
#
# thutchinson@utah.edu


from Tkinter import *
import numpy as n
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from astropy.io import fits
from os import environ
from os.path import join, exists
from redmonster.physics.misc import poly_array
from astropy.convolution import convolve, Box1DKernel

class Plot_Fit(Frame):
    def __init__ (self):
        self.root = Tk()
        self.plate = None
        self.mjd = None
        #
        plate = StringVar()
        plate.set('7848')
        mjd = StringVar()
        mjd.set('56959')
        #
        L1 = Label(self.root, text='Plate')
        L1.grid(sticky=E)
        L2 = Label(self.root, text='MJD')
        L2.grid(sticky=E)
        L3 = Label(self.root, text='Fiber')
        L3.grid(stick=E)
        self.e1 = Entry(self.root, textvariable=plate)
        self.e1.bind()
        self.e1.grid(row=0, column=1)
        self.e2 = Entry(self.root, textvariable=mjd)
        self.e2.grid(row=1, column=1)
        fiber = StringVar()
        fiber.set('0')
        self.e3 = Entry(self.root, textvariable=fiber)
        self.e3.grid(row=2, column=1)
        self.var = BooleanVar()
        self.var.set(1)
        c = Checkbutton(self.root, text='Overplot best-fit model', variable=self.var)
        c.grid(row=3, column=1)
        #
        smooth = StringVar()
        smooth.set('5')
        L4 = Label(self.root, text='Smooth')
        L4.grid(sticky=E)
        self.e4 = Entry(self.root, textvariable=smooth)
        self.e4.grid(row=4, column=1)
        plot = Button(self.root, text='Plot', command=self.do_plot)
        plot.grid(row=5, column=1)
        qbutton = Button(self.root, text='QUIT', fg='red', command=self.root.destroy)
        qbutton.grid(row=6, column=1)
        nextfiber = Button(self.root, text='>', command=self.next_fiber)
        nextfiber.grid(row=2, column=4)
        prevfiber = Button(self.root, text='<', command=self.prev_fiber)
        prevfiber.grid(row=2, column=3)
        Frame.__init__(self,self.root)
        self.root.mainloop()

    def do_plot(self):
        if self.plate != int(self.e1.get()) or self.mjd != int(self.e2.get()):
            self.plate = int(self.e1.get())
            self.mjd = int(self.e2.get())
            self.fiber = int(self.e3.get())
            self.platepath = join(environ['BOSS_SPECTRO_REDUX'], environ['RUN2D'], '%s' % self.plate, 'spPlate-%s-%s.fits' % (self.plate, self.mjd))
            hdu = fits.open(self.platepath)
            self.specs = hdu[0].data
            self.wave = 10**(hdu[0].header['COEFF0'] + n.arange(hdu[0].header['NAXIS1'])*hdu[0].header['COEFF1'])
            self.models = fits.open(join(environ['REDMONSTER_SPECTRO_REDUX'], environ['RUN2D'], '%s' % self.plate, environ['RUN1D'], 'redmonster-%s-%s.fits' % (self.plate, self.mjd)))[2].data
            self.fiberid = fits.open(join(environ['REDMONSTER_SPECTRO_REDUX'], environ['RUN2D'], '%s' % self.plate, environ['RUN1D'], 'redmonster-%s-%s.fits' % (self.plate, self.mjd)))[1].data.FIBERID
            self.type = fits.open(join(environ['REDMONSTER_SPECTRO_REDUX'], environ['RUN2D'], '%s' % self.plate, environ['RUN1D'], 'redmonster-%s-%s.fits' % (self.plate, self.mjd)))[1].data.CLASS
            self.z = fits.open(join(environ['REDMONSTER_SPECTRO_REDUX'], environ['RUN2D'], '%s' % self.plate, environ['RUN1D'], 'redmonster-%s-%s.fits' % (self.plate, self.mjd)))[1].data.Z1
        else:
            self.fiber = int(self.e3.get())
        f = Figure(figsize=(10,6), dpi=100)
        a = f.add_subplot(111)
        if self.var.get() == 0:
            a.plot(self.wave, self.specs[self.fiber], color='red')
        elif self.var.get() == 1:
            smooth = self.e4.get()
            if smooth is '':
                a.plot(self.wave, self.specs[self.fiber], color='red')
            else:
                a.plot(self.wave, convolve(self.specs[self.fiber], Box1DKernel(int(smooth))), color='red')
            # Overplot model
            loc = n.where(self.fiberid == self.fiber)[0]
            if len(loc) is not 0:
                a.plot(self.wave, self.models[loc[0]], color='black')
                a.set_title('Plate %s Fiber %s: z=%s class=%s' % (self.plate, self.fiber, self.z[loc][0], self.type[loc][0]))
            else:
                print 'Fiber %s is not in redmonster-%s-%s.fits' % (self.fiber, self.plate, self.mjd)
                a.set_title('Plate %s Fiber %s' % (self.plate, self.fiber))

        a.set_xlabel('Wavelength ($\AA$)')
        a.set_ylabel('Flux ($10^{-17} erg\ cm^2 s^{-1} \AA^{-1}$)')
        canvas = FigureCanvasTkAgg(f, master=self.root)
        canvas.get_tk_widget().grid(row=0, column=5, rowspan=20)
        toolbar_frame = Frame(self.root)
        toolbar_frame.grid(row=20,column=5)
        toolbar = NavigationToolbar2TkAgg( canvas, toolbar_frame )
        canvas.show()

    def next_fiber(self):
        self.fiber += 1
        self.e3.delete(0, END)
        self.e3.insert(0, str(self.fiber))
        self.do_plot()

    def prev_fiber(self):
        self.fiber -= 1
        self.e3.delete(0, END)
        self.e3.insert(0, str(self.fiber))
        self.do_plot()

app = Plot_Fit()


'''
    from __future__ import print_function
    import glob
    import os
    os.chdir("/mydir")
    for file in glob.glob("*.txt"):
    print(file)
    '''
