class VacuumAgent:
    def __init__(self):
        self.location = 'A'
        self.environment = {'A': 1, 'B': 1}

    def perceive(self):
        return self.environment[self.location]

    def act(self):
        if self.perceive() == 1:
            self.environment[self.location] = 0
            return 'Suck'
        elif self.location == 'A':
            self.location = 'B'
            return 'Right'
        elif self.location == 'B':
            self.location = 'A'
            return 'Left'

agent = VacuumAgent()

for _ in range(6):
    action = agent.act()
    print(f"Location: {agent.location}, Action: {action}, Environment: {agent.environment}")
