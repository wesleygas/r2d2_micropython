import uasyncio as aio

class ActorAnimator:
    def __init__(self, actuator, anim_steps: list[list[2], int]):
        self.anim_steps = anim_steps
        self.actuator = actuator
    async def animate(self):
        self.actuator.running = True
        act_task = aio.create_task(self.actuator.update())
        for payload, duration in self.anim_steps:
            self.actuator.act(payload)
            await aio.sleep_ms(duration)
        self.actuator.running = False
        self.actuator.on_stop()
        act_task.cancel()


class Scene:
    def __init__(self, actors: list):
        self.actors = actors
    async def _run(self):
        await aio.gather(*[actor.animate() for actor in self.actors])
        # await aio.gather([aio.create_task(actuator.animate()) for actuator in self.animated_actuators])
    def run(self):
        aio.run(self._run())

