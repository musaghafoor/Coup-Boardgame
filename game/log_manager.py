"""
Represents the class for LogManager which handles  the action log.
"""
class LogManager:
    def __init__(self):
        """Initialises the action log"""
        self.action_log = []

    def log_action(self, log_entry):
        """Adds a log to the action log"""
        self.action_log.append(log_entry)

    def get_action_log(self):
        """Returns the action log"""
        return self.action_log