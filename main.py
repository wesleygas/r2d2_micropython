from machine import Pin, I2C
from pca9685 import PCA9685, Servo as PCAServo

from actors import EspServo, ServoActor, DFPlayerActor
from animation_engine import ActorAnimator, Scene

import scene_1_steps
import scene_2_steps

i2c = I2C(1, sda=Pin(22), scl=Pin(21))  # Correct I2C pins for RP2040
pca = PCA9685(i2c)
pca.frequency = 50
servos = [PCAServo(pca.channels[i], min_pulse=420, max_pulse=2700) for i in range(16)]


upper_1 = ServoActor(servos[0], initial_position=0.13, closed_position=0.13, open_position=0.35) 
upper_2 = ServoActor(servos[1], initial_position=0.16, closed_position=0.16, open_position=0.58) 
upper_3 = ServoActor(servos[2], initial_position=0.13, closed_position=0.13, open_position=0.38) 
down1 = ServoActor(servos[3], initial_position=0.54, closed_position=0.54, open_position=0.85) 
down2 = ServoActor(servos[4], initial_position=0.04, closed_position=0.04, open_position=0.44) 

### USING I2S for sound 
# Init sdcard
# sd = SDCard(slot=2,freq=15000000)  # sck=18, mosi=23, miso=19, cs=5
# os.mount(sd, "/sd")
# audio = I2SAudioPlayerActor(sck=4, ws=15, sd=2, buffer_length=10000)

## Using DFPlayer for sound

audio = DFPlayerActor()
audio.register_songs(scene_1_steps.audio_dictionary)
######
# Cena 1
######
scene_1 = Scene([
    ActorAnimator(actuator=upper_1, anim_steps=scene_1_steps.upper_1_animation),
    # ActorAnimator(actuator=upper_2, anim_steps=scene_1_steps.upper_2_animation),
    ActorAnimator(actuator=audio, anim_steps=scene_1_steps.audio_animation)
])
### end scene 1

######
# Cena 2
######
scene_2 = Scene([
    ActorAnimator(actuator=upper_1, anim_steps=scene_2_steps.upper_1_animation),
    ActorAnimator(actuator=upper_2, anim_steps=scene_2_steps.upper_2_animation)
])
### end scene 2

#...

scene_1.run()

