"""Toy task list (fixture)."""


class TaskList:
    def __init__(self):
        self.tasks = {}

    def add(self, title, done=False):
        self.tasks[title] = done

    def mark_done(self, title):
        pass
