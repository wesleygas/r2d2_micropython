from machine import Pin, PWM, I2S
import uasyncio as aio
import utime

from dfplayer import DFPlayer


## Actors
# All actors must follow the same interface:
# - def act(self, payload):
#   Method that runs every time a new animation step is available
# - async def update
#   Method that runs at every animator step
##

class EspServo():
    """Control servos directly from a GPIO"""
    min_duty = 20
    max_duty = 135
    range = max_duty - min_duty
    def __init__(self, pin):
        self.servo = PWM(Pin(pin),freq=50,duty=50)
    #
    @property
    def fraction(self):
        """Pulse width expressed as fraction between 0.0 (`min_pulse`) and 1.0 (`max_pulse`).
        For conventional servos, corresponds to the servo position as a fraction
        of the actuation range. Is None when servo is diabled (pulsewidth of 0ms).
        """
        return (self.servo.duty() - EspServo.min_duty) / EspServo.range
    #
    @fraction.setter
    def fraction(self, value):
        if not 0.0 <= value <= 1.0:
            raise ValueError("Must be 0.0 to 1.0")
        duty_cycle = int(value*EspServo.range) + EspServo.min_duty
        self.servo.duty(duty_cycle)


class ServoActor:
    """Actor class that enables seamless controll of servos from GPIO or from PCA9685"""
    def __init__(self, servo, speed=0.05, initial_position=0.5, closed_position=0.0, open_position=1.0):
        self.running = False
        # Initiate positions
        servo.fraction = initial_position
        self.curr_pos = initial_position
        self.setp = initial_position
        self.speed = speed
        # Calc bounds
        self.min_pos = closed_position
        max_pos = open_position
        self.range = max_pos - self.min_pos
        # Start hardware
        self.servo = servo
    #
    def calc_pos(self,position):
        return position*self.range+self.min_pos
    #
    def act(self, payload):
        self.setp = payload[0]
        self.speed = payload[1]
    #
    def on_stop(self):
        pass
    #
    async def update(self):
        while self.running:
            # print("While Servo")
            self.curr_pos = (1.0-self.speed)*self.curr_pos + self.speed*self.setp       
            self.servo.fraction = self.calc_pos(self.curr_pos)
            await aio.sleep_ms(10)


class DFPlayerActor:
    """Actor class enabling control of DFPlayer modules"""
    INACTIVE = -1
    READY = 0
    PLAYING = 1
    IDLE = 2
    def __init__(self, tx_pin=17, rx_pin=16, starting_volume=15):
        self.player = DFPlayer(pin_TX=tx_pin, pin_RX=rx_pin)
        self.player.volume(starting_volume)
        #
        self.is_playing = False
        self.stop_time = 0
        self.is_looping = False
    
    def register_songs(self, songs_mapping):
        self.mapping = songs_mapping
    
    def act(self, payload):
        # play X.Y file for Z millisseconds
        filename, ms_to_play, is_loop = payload 
        self.is_looping = bool(is_loop)
        if(ms_to_play == 0):
            self.stop_time = 0
        else:
            self.stop_time = utime.ticks_add(utime.ticks_ms(), ms_to_play)
        if(is_loop):
            self.player.loop_track(self.mapping[filename])
            self.player.loop()
        else:
            self.player.play(self.mapping[filename])
            self.player.loop_disable()
        self.is_playing = True
        
    def on_stop(self):
        self.player.stop()
        
    async def update(self):
        while self.running:
            if(self.is_playing):
                if(self.stop_time != 0 and utime.ticks_diff(self.stop_time, utime.ticks_ms()) <= 0):
                    self.is_playing = False
                    self.player.stop()
                await aio.sleep_ms(10)
            else:
                await aio.sleep_ms(50)


class I2SAudioPlayerActor:
    # Sck = Bit Clock (BCK)
    # ws = Word Select (LCK)
    # sd = Sound Data (DIN)
    INACTIVE = -1
    READY = 0
    PLAYING = 1
    IDLE = 2
    def __init__(self, sck=4, ws=15, sd=2, buffer_length=40000):
        # print("Init AudioPlayer")
        self.running = False
        self.state = I2SAudioPlayerActor.INACTIVE
        #SDCard
        self.wav = None
        # Pin defs
        self.i2s_id = 1
        self.sck = sck
        self.ws = ws
        self.sd = sd
        # I2S config
        self.buffer_length = buffer_length
        self.audio_out = None
        self.WAV_BIT_DEPTH = 16
        self.WAV_FORMAT = I2S.MONO
        self.WAV_SAMPLE_RATE = 16000
        self.i2s_init()
        # Runtime vars
        self.loop = False
        
    #
    def i2s_init(self):
        # print("Init I2S")
        self.audio_out = I2S(
            self.i2s_id,
            sck=Pin(self.sck),
            ws=Pin(self.ws),
            sd=Pin(self.sd),
            mode=I2S.TX,
            bits=self.WAV_BIT_DEPTH,
            format=self.WAV_FORMAT,
            rate=self.WAV_SAMPLE_RATE,
            ibuf=self.buffer_length,
        )
        self.state = I2SAudioPlayerActor.READY
    #
    def i2s_deinit(self):
        # print("i2s_deinit")
        self.running = False
        self.audio_out.deinit()
        self.state = I2SAudioPlayerActor.INACTIVE
    #
    def act(self, payload):
        print("act", payload)
        if(self.state == I2SAudioPlayerActor.PLAYING):
            self.wav.close()
        audio_file = payload[0]
        audio_position = payload[1]*self.WAV_SAMPLE_RATE
        self.loop = bool(payload[2])
        if(audio_file == "SILENCE"):
            self.state = I2SAudioPlayerActor.IDLE 
        else:
            self.wav = open(f"/sd/{audio_file}", 'rb')
            self.wav.seek(audio_position + 44)
            self.state = I2SAudioPlayerActor.PLAYING
    
    def on_stop(self):
        pass
    #
    async def update(self):
        # print("Update Audio", self.state)
        swriter = aio.StreamWriter(self.audio_out)
        wav_samples = bytearray(10000)
        wav_samples_mv = memoryview(wav_samples)
        while self.running:
            # print("while audio", self.state)
            # if(self.state == AudioPlayerActor.READY):
            #     pass
            if(self.state == I2SAudioPlayerActor.PLAYING):
                num_read = self.wav.readinto(wav_samples_mv)
                # end of WAV file?
                if num_read == 0:
                    # end-of-file, advance to first byte of Data section
                    _ = self.wav.seek(44)
                    if(not self.loop):
                        self.wav.close()
                        self.state = I2SAudioPlayerActor.IDLE
                    else:
                        swriter.out_buf = wav_samples_mv[:num_read]
                        await swriter.drain()
                else:
                    swriter.out_buf = wav_samples_mv[:num_read]
                    await swriter.drain()
            elif(self.state == I2SAudioPlayerActor.IDLE or self.state == I2SAudioPlayerActor.READY):
                # await aio.sleep_ms(10) # test to see if there's still noise
                for x in range(256):  # Neccessary for silence
                    wav_samples[x] = 0
                swriter.out_buf = wav_samples_mv[:num_read]
                await swriter.drain()
                await aio.sleep_ms(100)
            elif(self.state == I2SAudioPlayerActor.INACTIVE):
                raise RuntimeError("Tried to update an inactive AudioPlayer")
        else:
            self.wav.close()

    
class AudioPlayerActorV2:
    # Sck = Bit Clock (BCK)
    # ws = Word Select (LCK)
    # sd = Sound Data (DIN)
    INACTIVE = -1
    READY = 0
    PLAYING = 1
    IDLE = 2
    def __init__(self, sck=4, ws=15, sd=2, buffer_length=40000):
        # print("Init AudioPlayer")
        self.running = False
        self.state = I2SAudioPlayerActor.INACTIVE
        #SDCard
        self.wav = None
        # Pin defs
        self.i2s_id = 1
        self.sck = sck
        self.ws = ws
        self.sd = sd
        # I2S config
        self.buffer_length = buffer_length
        self.audio_out = None
        self.WAV_BIT_DEPTH = 16
        self.WAV_FORMAT = I2S.MONO
        self.WAV_SAMPLE_RATE = 16000
        self.i2s_init()
        # Runtime vars
        self.loop = False
        
    #
    def i2s_init(self):
        # print("Init I2S")
        self.audio_out = I2S(
            self.i2s_id,
            sck=Pin(self.sck),
            ws=Pin(self.ws),
            sd=Pin(self.sd),
            mode=I2S.TX,
            bits=self.WAV_BIT_DEPTH,
            format=self.WAV_FORMAT,
            rate=self.WAV_SAMPLE_RATE,
            ibuf=self.buffer_length,
        )
        self.state = I2SAudioPlayerActor.READY
    #
    def i2s_deinit(self):
        # print("i2s_deinit")
        self.running = False
        self.audio_out.deinit()
        self.state = I2SAudioPlayerActor.INACTIVE
    #
    def act(self, payload):
        print("act", payload)
        if(self.state == I2SAudioPlayerActor.PLAYING):
            self.wav.close()
        audio_file = payload[0]
        audio_position = payload[1]*self.WAV_SAMPLE_RATE
        self.loop = bool(payload[2])
        if(audio_file == "SILENCE"):
            self.state = I2SAudioPlayerActor.IDLE 
        else:
            self.wav = open(f"/sd/{audio_file}", 'rb')
            self.wav.seek(audio_position + 44)
            self.state = I2SAudioPlayerActor.PLAYING

    def on_stop(self):
        pass
    #
    async def update(self):
        # print("Update Audio", self.state)
        swriter = aio.StreamWriter(self.audio_out)
        wav_samples = bytearray(10000)
        wav_samples_mv = memoryview(wav_samples)
        while self.running:
            # print("while audio", self.state)
            # if(self.state == AudioPlayerActor.READY):
            #     pass
            if(self.state == I2SAudioPlayerActor.PLAYING):
                num_read = self.wav.readinto(wav_samples_mv)
                # end of WAV file?
                if num_read == 0:
                    # end-of-file, advance to first byte of Data section
                    _ = self.wav.seek(44)
                    if(not self.loop):
                        self.wav.close()
                        self.state = I2SAudioPlayerActor.IDLE
                    else:
                        swriter.out_buf = wav_samples_mv[:num_read]
                        await swriter.drain()
                else:
                    swriter.out_buf = wav_samples_mv[:num_read]
                    await swriter.drain()
            elif(self.state == I2SAudioPlayerActor.IDLE or self.state == I2SAudioPlayerActor.READY):
                # await aio.sleep_ms(10) # test to see if there's still noise
                for x in range(256):  # Neccessary for silence
                    wav_samples[x] = 0
                swriter.out_buf = wav_samples_mv[:num_read]
                await swriter.drain()
                await aio.sleep_ms(100)
            elif(self.state == I2SAudioPlayerActor.INACTIVE):
                raise RuntimeError("Tried to update an inactive AudioPlayer")
        else:
            self.wav.close()

        
    