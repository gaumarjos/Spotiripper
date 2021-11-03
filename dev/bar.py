import shutil
import numpy


class SoundBar(object):
    def __init__(self, maxvalue):
        # self.w = shutil.get_terminal_size((80, 20)).columns - 10
        self.w = 100
        self.maxvalue = maxvalue

    def update(self, value):
        xbar = int(value / self.maxvalue * self.w)
        xbar = numpy.clip(xbar, a_min=0, a_max=self.w)
        print('|' + xbar * '\u2588' + (self.w - xbar) * ' ' + '| {:6.2f}'.format(value), end='\r')
