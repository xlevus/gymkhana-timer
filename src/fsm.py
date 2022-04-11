

class StateMachine:
    def __init__(self, start_cls: "State", **globals):
        self.state = None
        self.globals = globals

    def __getattr__(self, key):
        return self.globals[key]

    def change(self, next_state_cls, *args):
        if self.state is not None:
            self.state.exit()

        self.state = next_state_cls(self, *args)
        self.state.enter()

    def tick(self):
        self.state.tick()


class State:
    def __init__(self, machine: StateMachine, *args):
        self.macine = machine

    def enter(self):
        pass

    def exit(self):
        pass

    def tick(self):
        pass