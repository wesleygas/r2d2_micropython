from machine import Timer

class LightFlipper():
    def __init__(self, red, blue, timer):
        self.red = red
        self.blue = blue
        self.timer = timer
    
    def flip_redblue_light(self, x):
        try:
            if(self.red.duty_cycle > 0):
                self.red.duty_cycle=0
                self.blue.duty_cycle=0xffff
            else:
                self.red.duty_cycle=0xffff
                self.blue.duty_cycle=0
        except Exception:
            pass
        
    def start(self):
        self.timer.init(period=500, mode=Timer.PERIODIC, callback=self.flip_redblue_light)
    
    def stop(self):
        self.timer.deinit()
        self.blue.duty_cycle = 0
        self.red.duty_cycle = 0