from machine import Pin, I2C
from pca9685 import PCA9685, Servo as PCAServo
from machine import Timer

from actors import EspServo, ServoActor, DFPlayerActor
from animation_engine import ActorAnimator, Scene
from light_flipper import LightFlipper

import scene_1_steps
import scene_2_steps 
import scene_3_steps

i2c = I2C(1, sda=Pin(22), scl=Pin(21))
pca = PCA9685(i2c)
pca.frequency = 50
servos = [PCAServo(pca.channels[i], min_pulse=420, max_pulse=2700) for i in range(14)]

## Starting RED/BLUE light flips
lf = LightFlipper(red=pca.channels[14], blue=pca.channels[15], timer=Timer(1))
lf.start()
#lf.stop()

## Using DFPlayer for sound
audio = DFPlayerActor(starting_volume=26)
audio_dictionary = {
    "chirps": 1,
    "abuble": 2,
#    "fox": 3
}
audio.register_songs(audio_dictionary)
######

upper_1 = ServoActor(servos[0], initial_position=0.13, closed_position=0.13, open_position=0.35) 
upper_2 = ServoActor(servos[1], initial_position=0.16, closed_position=0.16, open_position=0.58) 
upper_3 = ServoActor(servos[2], initial_position=0.13, closed_position=0.13, open_position=0.38) 
down1 = ServoActor(servos[4], initial_position=0.54, closed_position=0.54, open_position=0.85) 
down2 = ServoActor(servos[5], initial_position=0.04, closed_position=0.04, open_position=0.40) 

######
# Cena 1
######
scene_1 = Scene([
    ActorAnimator(actuator=upper_1, anim_steps=scene_1_steps.upper_1_animation),
    ActorAnimator(actuator=upper_1, anim_steps=scene_1_steps.upper_1_animation),
    ActorAnimator(actuator=upper_2, anim_steps=scene_1_steps.upper_2_animation),
    ActorAnimator(actuator=upper_3, anim_steps=scene_1_steps.upper_3_animation),
    ActorAnimator(actuator=down1, anim_steps=scene_1_steps.down1_animation),
    ActorAnimator(actuator=down2, anim_steps=scene_1_steps.down2_animation),
    ActorAnimator(actuator=audio, anim_steps=scene_1_steps.audio_animation)
])
### end scene 1

######
# Cena 2
######
scene_2 = Scene([
   ActorAnimator(actuator=upper_1, anim_steps=scene_2_steps.upper_1_animation),
   ActorAnimator(actuator=upper_2, anim_steps=scene_2_steps.upper_2_animation),
   ActorAnimator(actuator=upper_3, anim_steps=scene_2_steps.upper_3_animation),
   ActorAnimator(actuator=down1, anim_steps=scene_2_steps.down1_animation),
   ActorAnimator(actuator=down2, anim_steps=scene_2_steps.down2_animation),
   ActorAnimator(actuator=audio, anim_steps=scene_2_steps.audio_animation)
])
### end scene 2

######
# Cena 3
######
scene_3 = Scene([
   ActorAnimator(actuator=upper_1, anim_steps=scene_3_steps.upper_1_animation),
   ActorAnimator(actuator=upper_2, anim_steps=scene_3_steps.upper_2_animation),
   ActorAnimator(actuator=upper_3, anim_steps=scene_3_steps.upper_3_animation),
   ActorAnimator(actuator=down1, anim_steps=scene_3_steps.down1_animation),
   ActorAnimator(actuator=down2, anim_steps=scene_3_steps.down2_animation),
   ActorAnimator(actuator=audio, anim_steps=scene_3_steps.audio_animation)
])
### end scene 3

#...
scene_1.run()
scene_2.run()
scene_3.run()


