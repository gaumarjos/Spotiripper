import numpy


class SoundBar(object):
    def __init__(self, limitx, graceperiod=20, terminal_width=80, gui_soundbar=None):
        self.limitx = limitx
        self.maxx = 0.0
        self.i = 0
        self.graceperiod = graceperiod
        self.w = terminal_width - 20
        self.gui_soundbar = gui_soundbar

    def update(self, x):
        self.i = self.i + 1
        if self.i > self.graceperiod:
            if x > self.maxx:
                self.maxx = x

            xbar = int(x / self.limitx * self.w)
            xbar = numpy.clip(xbar, a_min=0, a_max=self.w)

            maxxbar = int(self.maxx / self.limitx * self.w)
            maxxbar = numpy.clip(maxxbar, a_min=0, a_max=self.w)

            # Writing on terminal if no GUI is used or on GUI soundbar is GUI is used
            if self.gui_soundbar is None:
                # print('|' + xbar * '\u2588' + (self.w - xbar) * ' ' + '| {:6.2f} {:6.2f}'.format(x, self.maxx), end='\r')
                print('|' + xbar * '\u2588' + \
                      (maxxbar - xbar) * ' ' + \
                      '|' + (self.w - maxxbar - 1) * ' ' + \
                      '| {:6.2f} {:6.2f}'.format(x, self.maxx), end='\r')
            else:
                # In range 0-100
                self.gui_soundbar.setValue(x / self.limitx * 100.0)
