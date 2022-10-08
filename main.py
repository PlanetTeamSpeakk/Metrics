import creds
import time
import db
import os
import os.path
import importlib
import traceback
from concurrent.futures import ThreadPoolExecutor, wait
from threading import Lock
from colorama import Fore, Style, init
from util import *
from objects import *

os.chdir(os.path.dirname(os.path.abspath(__file__))) # Set working directory to this script's directory for relative paths to work.
init() # Init Colorama
pool = ThreadPoolExecutor()
modules = {}
container_names = {}

def register_module(path):
    pymodule = importlib.import_module(path)
    module_name = path[len("metrics."):]

    try:
        module = ModuleContainer.get_class(pymodule)()
    except Exception as e:
        log(f"Error trying to load module {module_name}: " + str(e), Fore.RED)
        return

    container = ModuleContainer(module_name, module, path.replace('.', '/') + ".py", pymodule)
    module.init()

    modules[module_name] = container
    container_names[module.name] = module_name

    container.setup()
    log(f"Registered module {module_name} with metrics {join_nicely(module.metrics.keys())}.", Fore.CYAN)

def update_metrics():
    updated = False
    db.check_reconnect()
    cursor = db.db.cursor()
    inserters = []
    tasks = {}
    mtasks = {}
    task_lock = Lock()
    inserter_lock = Lock()

    for module in list(modules.values()):
        if module.check_delete():
            del modules[module.name]
            continue

        module.check_reload()

        def create_updater(metrics):
            def do_update_metrics(measurement):
                def run(metric):
                    value = metric.update(measurement)

                    if value is not None:
                        inserter_lock.acquire()
                        inserters.append((metric.insert, value))
                        inserter_lock.release()

                    return value

                for metric in metrics:
                    if metric.from_measurement:
                        if measurement is None:
                            continue
                    elif not should_update(metric) or measurement is not None:
                        continue

                    task = pool.submit(run, metric)
                    task_lock.acquire()

                    if not metric.from_measurement:
                        tasks[task] = metric
                    else:
                        mtasks[task] = metric

                    task_lock.release()
            return do_update_metrics

        updater = create_updater(list(module.module.metrics.values()))
        if isinstance(module.module, MeasurableModule) and should_update(module.module):
            def measure_and_invoke(updater, module):
                log(f"Taking measurement for module {module.module.name}.")
                measurement = module.module.measure()
                updater(measurement)

                inserter_lock.acquire()
                inserters.append((module.module.insert, measurement))
                inserter_lock.release()

                return measurement

            task = pool.submit(measure_and_invoke, updater, module)
            task_lock.acquire()
            tasks[task] = module.module
            task_lock.release()

        updater(None)

    done, not_done = wait(tasks.keys())
    mdone, mnot_done = wait(mtasks.keys())

    done = [*done, *mdone]
    not_done = [*not_done, *mnot_done]

    if len(not_done) > 0:
        log(f"{len(not_done)} task(s) could not finish.", Fore.YELLOW)

    for task in done:
        measurable = tasks[task] if task in tasks else mtasks[task]

        if task.exception():
            if isinstance(measurable, Metric):
                log(f"Error updating metric {measurable.name} of module {measurable.module}: " + str(task.exception()), Fore.RED)
            else:
                log(f"Error taking measurement {measurable.name}: " + str(task.exception()), Fore.RED)

            measurable.errored = True
            continue

        measurable.errored = False
        value = task.result()

        if value is not None:
            updated = True

            measurable.last_updated = time.time()
            if isinstance(measurable, Metric):
                log(f"Updated metric {measurable.name} from module {measurable.module}, value: {value}")

    if updated:
        for inserter, value in inserters:
            try:
                inserter(cursor, value)
            except Exception as e:
                log(f"Error inserting data for inserter {str(inserter)}: {str(e)}", Fore.RED)
                traceback.print_exc()

        db.db.commit()

def should_update(measurable):
    return isinstance(measurable, Metric) and measurable.from_measurement and should_update(modules[container_names[measurable.module]].module) or time.time() - measurable.last_updated >= ((measurable.interval if not measurable.errored else measurable.error_interval) - 0.5)

def check_new_modules():
    for (dirpath, dirnames, filenames) in os.walk("metrics"):
         if "__pycache__" in dirpath:
             continue

         for f in filter(lambda f: f.endswith(".py"), filenames):
            path = dirpath + ('/' if not len(dirpath) == 0 else '') + f
            for module in modules.values():
                if module.path == path:
                    break
            else:
                register_module(path.replace('/', '.')[:-3])

check_new_modules()

if __name__ == "__main__":
    while True:
        start = time.time()
        check_new_modules()
        update_metrics()
        sleep = 5 - (time.time() - start)
        if sleep > 0:
            time.sleep(sleep)
