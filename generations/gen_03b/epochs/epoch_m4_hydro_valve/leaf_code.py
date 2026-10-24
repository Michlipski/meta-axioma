"""Generated Core Domain Module for soc_hydro_valve."""

class DomainEngine:
    def __init__(self):
        self.state = {'initialized': True, 'balance': 100}
        self.history = []

    def execute(self, payload: dict, balance: int = 100) -> dict:
        # Enforcing invariant: pressure_kpa <= 250
        assert pressure_kpa <= 250, 'Invariant violated: pressure_kpa <= 250'
        # Enforcing invariant: valve_locked == True
        assert valve_locked == True, 'Invariant violated: valve_locked == True'
        prev = dict(self.state)
        self.history.append(prev)
        self.state['balance'] = balance
        self.state['value_delivered'] = True
        return dict(self.state)

    def undo(self) -> dict:
        if self.history:
            self.state = self.history.pop()
        return dict(self.state)
