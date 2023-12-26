import time
from abc import ABC, abstractmethod
from util import *
import os
import os.path
import inspect
import importlib
from colorama import Fore

class Measurable(ABC):
    def __init__(self, name, interval, error_interval=None):
        self.name = name
        self.interval = interval
        self.error_interval = error_interval if error_interval is not None else interval
        self.last_updated = 0
        self.errored = False

    def should_update(self):
        return time.time() - self.last_updated >= (self.interval if not self.errored else self.error_interval)

    @abstractmethod
    def update(self, measurement=None):
        pass

    def set(self, value):
        pass

class Metric(Measurable):
    def __init__(self, name, module, interval, error_interval, function, inserter, from_measurement):
        super().__init__(name, interval, error_interval)
        self.module = module
        self.function = function
        self.inserter = inserter
        self.from_measurement = from_measurement

    def update(self, measurement=None):
        return self.function(*([measurement] if self.from_measurement else []))

    def set(self, value):
        if self.inserter:
            self.inserter(value)

class ModuleContainer:
    def __init__(self, name, module, path, pymodule):
        self.name = name
        self.module = module
        self.path = path
        self.pymodule = pymodule
        self.last_reload = time.time()

    def update(self, pool):
        tasks = []
        for metric in self.metrics.values():
            tasks.append(metric.update)

    def check_delete(self):
        if os.path.exists(self.path):
            return False

        log(f"Module {self.name} was deleted, unloading...", Fore.RED)
        return True

    def check_reload(self):
        if os.path.getmtime(self.path) <= self.last_reload:
            return

        log(f"Module {self.module.name} changed, attempting reload!", Fore.YELLOW)

        update_times = {metric: self.module.metrics[metric].last_updated for metric in self.module.metrics}

        self.last_reload = time.time()
        if not self.reload():
            return

        for metric, updated in update_times.items():
            if metric in self.module.metrics.values():
                metric.last_updated = updated

        log(f"Reloaded module {self.name}, metrics: {join_nicely(self.module.metrics.keys())}.", Fore.CYAN);

    def reload(self):
        self.module.on_reload()

        try:
            importlib.reload(self.pymodule)
            self.module = ModuleContainer.get_class(self.pymodule)()
        except RuntimeError as e:
            log(f"Error while reloading module {self.name}:" + str(e), Fore.RED)
            return False

        self.module.metrics = {}

        try:
            self.setup()
        except Exception as e:
            log(f"Could not setup module {self.name} after reload: " + str(e), Fore.RED)
            return False

        return True

    @staticmethod
    def get_class(module):
        classes = [c[1] for c in inspect.getmembers(module, lambda m: inspect.isclass(m) and issubclass(m, Module)) if c[1].__module__ == module.__name__]

        if len(classes) > 1:
            raise RuntimeError(f"Module {module.__name__} has multiple Module classes.")
        if len(classes) == 0:
            raise RuntimeError(f"Module {module.__name__} has no Module class.")

        return classes[0]

    def setup(self):
        self.module.setup()

class Module(ABC):
    def __init__(self, name):
        self.name = name
        self.metrics = {}

    def on_reload(self):
        pass

    def init(self):
        pass

    @abstractmethod
    def setup(self, db):
        pass

    def register(self, name, interval, error_interval, function, inserter):
        self.metrics[name] = Metric(name, self.name, interval, error_interval, function, inserter, False)

class MeasurableModule(Module, Measurable): # For modules that measure multiple metrics in one go (like humitemp and weather)
    def __init__(self, name, interval, error_interval):
        Module.__init__(self, name)
        Measurable.__init__(self, name, interval, error_interval)
        self.measurement = None

    def update(self):
        measure()

    @abstractmethod
    def measure(self):
        pass

    @abstractmethod
    def set(self, measurement):
        pass

    def mregister(self, name, function, inserter=None):
        self.metrics[name] = Metric(name, self.name, 0, 0, function, inserter, True)
