"""Code Timing Class by RealPython

This is based on https://realpython.com/python-timer/ with
minor modifiactions.
"""


import time
from contextlib import ContextDecorator
from dataclasses import dataclass, field
from typing import Any, Callable, ClassVar, Dict, Optional


class TimerError(Exception):
    """A custom exception used to report errors using the Timer class."""


@dataclass
class Timer(ContextDecorator):
    """Times your code using a class, context manager, or decorator."""

    timers: ClassVar[Dict[str, float]] = {}
    name: Optional[str] = None
    text: str = "Elapsed time: {:0.4f} seconds"
    logger: Optional[Callable[[str], None]] = None
    _start_time: Optional[float] = field(default=None, init=False, repr=False)


    def __post_init__(self) -> None:
        """Initialization: add timer to dict of timers"""
        if self.name:
            self.timers.setdefault(self.name, 0)


    def start(self) -> None:
        """Starts a new timer."""
        if self._start_time is not None:
            raise TimerError(f"Timer is running. Use .stop() to stop it.")

        self._start_time = time.perf_counter()


    def stop(self) -> float:
        """Stops the timer, and report the elapsed time."""
        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start() to start it.")

        # Calculate elapsed time
        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None

        # Report elapsed time
        if self.logger:
            self.logger(self.text.format(elapsed_time))

        if self.name:
            self.timers[self.name] += elapsed_time

        return elapsed_time

    def elapsed_str(self) -> str:
        """Returns elapsed time as a formatted string without stopping the timer."""
        if self._start_time is None:
            elapsed = self.timers.get(self.name, 0)
        else:
            elapsed = time.perf_counter() - self._start_time
        minutes = int(elapsed // 60)
        seconds = elapsed % 60
        return f"{minutes}m {seconds:.1f}s" if minutes else f"{seconds:.1f}s"

    def __enter__(self) -> "Timer":
        """Starts a new timer as a context manager."""
        self.start()
        return self


    def __exit__(self, *exc_info: Any) -> None:
        """Stops the context manager timer."""
        self.stop()
