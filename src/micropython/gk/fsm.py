from gk.logging import INFO, log


class StateMachine:
    def __init__(self, **globals):
        self.state = None
        self.globals = globals

    def __getattr__(self, key):
        return self.globals[key]

    async def change(self, next_state):
        if self.state is not None:
            log(INFO, f"Exiting state {self.state}")
            await self.state.exit()

        next_state.init(self)
        self.state = next_state
        log(INFO, f"Entering state {self.state}")
        await self.state.enter()

    async def tick(self):
        next = await self.state.tick()
        if next is not None:
            await self.change(next)


class State:
    def init(self, machine: StateMachine) -> None:
        self.machine = machine

    def __repr__(self):
        return self.__class__.__name__

    async def enter(self):
        pass

    async def exit(self):
        pass

    async def tick(self):
        pass
