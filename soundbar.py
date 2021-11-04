import numpy


class SoundBar(object):
    def __init__(self, limitx, graceperiod=20, terminal_width=80):
        self.limitx = limitx
        self.maxx = 0.0
        self.i = 0
        self.graceperiod = graceperiod
        self.w = terminal_width - 20

    def update(self, x):
        self.i = self.i + 1
        if self.i > self.graceperiod:
            if x > self.maxx:
                self.maxx = x

            xbar = int(x / self.limitx * self.w)
            xbar = numpy.clip(xbar, a_min=0, a_max=self.w)

            maxxbar = int(self.maxx / self.limitx * self.w)
            maxxbar = numpy.clip(maxxbar, a_min=0, a_max=self.w)

            # print('|' + xbar * '\u2588' + (self.w - xbar) * ' ' + '| {:6.2f} {:6.2f}'.format(x, self.maxx), end='\r')
            print('|' + xbar * '\u2588' + \
                  (maxxbar - xbar) * ' ' + \
                  '|' + (self.w - maxxbar - 1) * ' ' + \
                  '| {:6.2f} {:6.2f}'.format(x, self.maxx), end='\r')
