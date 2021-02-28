from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path


class State(ABC):

    def __init__(self):
        self._context = None

    @property
    def context(self) -> FileManager:
        return self._context

    @context.setter
    def context(self, context: FileManager) -> None:
        self._context = context

    @abstractmethod
    def action(self):
        pass

    def previous(self):
        self._context.previous()


class FileManager:
    prev_state = None
    curr_state = None

    def __init__(self, state: State, url):
        self.storage_path = Path("/files/")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.server_url = url
        self.next(state)

    def next(self, state: State):
        state.context = self
        if state.__class__.__name__ != "PreviousState":
            self.prev_state = self.curr_state
        self.curr_state = state

    def previous(self):
        self.prev_state, self.curr_state = self.curr_state, self.prev_state,

    def execute(self):
        self.curr_state.action()
