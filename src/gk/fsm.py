from gk.logging import log, INFO


class StateMachine:
    def __init__(self, **globals):
        self.state = None
        self.globals = globals

    def __getattr__(self, key):
        return self.globals[key]

    async def change(self, next_state_cls, *args):
        if self.state is not None:
            log(INFO, f"Exiting state {self.state.__class__}")
            await self.state.exit()

        self.state = next_state_cls(self, *args)
        log(INFO, f"Entering state {self.state.__class__}")
        await self.state.enter()

    async def tick(self):
        await self.state.tick()


class State:
    def __init__(self, machine: StateMachine, *args):
        self.machine = machine

    async def enter(self):
        pass

    async def exit(self):
        pass

    async def tick(self):
        pass