"""A progress bar for the command line.

This class allows you to display a simple progress bar for long-running tasks.

The progress bar displays:
- Percentage completed
- Elapsed time
- A graphical progress bar using '#' and '.'

Note: This class writes directly to sys.stdout.
"""

import sys
import time

class Progress:
    """Command-line progress bar class"""

    def __init__(self, total, title="Progress", width=80):
        """
        Parameters:
        - total (int): Total number of steps
        - title (str): Title displayed before the bar
        - width (int): Total width of the output line
        """
        self.counter = 0
        self.total = total
        self.title = title
        self.width = width
        self.start_time = time.time()

    def __iadd__(self, value):
        """Increments the counter by the given value"""
        self.counter += value
        return self

    def show(self):
        """Displays the current state of the progress bar"""
        sec = time.time() - self.start_time
        percent = 100 * self.counter / self.total
        title = f'{self.title} ({percent:.0f}% {int(sec) // 60:02}:{int(sec) % 60:02}) '

        if len(title) >= self.width:
            raise ValueError("Progress bar does not fit width. Shorten title or increase width.")

        bar_width = self.width - len(title) - 3
        full_width = int(bar_width * self.counter / self.total)
        empty_width = bar_width - full_width

        # We don’t return anything (doctest expects None)
        sys.stdout.write('\r' + title + '[' + '#' * full_width + '.' * empty_width + ']')
        sys.stdout.flush()

    def finish(self):
        """Clears the progress bar line"""
        sys.stdout.write('\r' + ' ' * self.width + '\r')
        sys.stdout.flush()
