import creds
import time
import db
import os
import os.path
import importlib
import traceback
from concurrent.futures import ThreadPoolExecutor, wait
from colorama import Fore, Style, init

os.chdir(os.path.dirname(os.path.abspath(__file__))) # Set working directory to this script's directory for relative paths to work.
init() # Init Colorama
pool = ThreadPoolExecutor()
metrics = {}

def register_module(path):
    module = importlib.import_module(path)
    has_setup = True

    if not hasattr(module, "setup"):
        log(f"Module {path} has no setup function.", Fore.RED)
        has_setup = False

    if hasattr(module, "init"):
        module.init()

    def register_metric(name, interval, error_interval, function, *args, **kwargs):
        metrics[module_name]["metrics"][name] = {"name": name, "module": module_name, "interval": interval, "error_interval": error_interval, "function": function, "last_updated": 0, "errored": False}

    module_name = path[len("metrics."):]
    metrics[module_name] = {"name": module_name, "module": module, "path": path.replace('.', '/') + ".py", "last_reload": time.time(), "register": register_metric, "metrics": {}}

    if not has_setup:
        return # Module might be being worked on right now, we'll just leave it in in case it changes.

    module.setup(register=register_metric, db=db.db)
    log(f"Registered module {module_name} with metrics {', '.join([metric for metric in metrics[module_name]['metrics']])}.", Fore.CYAN)

def reload_module(module):
    module = metrics[module]

    if hasattr(module["module"], "on_reload"):
        module["module"].on_reload()

    importlib.reload(module["module"])

    if hasattr(module["module"], "init"):
        module["module"].init()

    if not hasattr(module["module"], "setup"):
        log(f"Setup function of module {module['name']} disappeared after reload! Not resetting its metrics.", Fore.RED)
        return

    module["metrics"] = {}
    module["module"].setup(register=module["register"], db=db.db)

def update_metrics():
    updated = False
    db.check_reconnect()
    cursor = db.db.cursor()
    tasks = {}

    for module in list(metrics.values()):
        if check_delete(module):
            continue

        check_reload(module)

        for metric in module["metrics"].values():
            if time.time() - metric["last_updated"] < ((metric["interval"] if not metric["errored"] else metric["error_interval"]) - 0.5):
                continue

            task = pool.submit(metric["function"], cursor)
            tasks[task] = metric

    done, not_done = wait(tasks.keys())
    if len(not_done) > 0:
        log(f"{len(not_done)} task(s) could not finish.", Fore.YELLOW)

    for task in done:
        metric = tasks[task]
        if task.exception():
            log(f"Error updating metric {metric['name']} of module {metric['module']}: " + str(task.exception()), Fore.RED)
            metric["errored"] = True
            continue

        metric["errored"] = False
        value = inserter = None
        result = task.result()

        if isinstance(result, tuple):
            value, inserter = result
        else:
            value = result

        if value:
            updated = True

            if inserter:
                inserter()

            metric["last_updated"] = time.time()
            log(f"Updated metric {metric['name']}, value: {value}")

    if updated:
        db.db.commit()

def check_new_modules():
    for (dirpath, dirnames, filenames) in os.walk("metrics"):
         if "__pycache__" in dirpath:
             continue

         for f in filter(lambda f: f.endswith(".py"), filenames):
            path = dirpath + ('/' if not len(dirpath) == 0 else '') + f
            for module in metrics.values():
                if module["path"] == path:
                    break
            else:
                register_module(path.replace('/', '.')[:-3])

def check_delete(module):
    if os.path.exists(module["path"]):
        return False

    log(f"Module {module['name']} was deleted, unloading...", Fore.RED)
    del metrics[module["name"]]
    return True

def check_reload(module):
    if os.path.getmtime(module["path"]) <= module["last_reload"]:
        return

    log(f"Module {module['name']} changed, attempting reload!", Fore.YELLOW)

    update_times = {metric: module["metrics"][metric]["last_updated"] for metric in module["metrics"]}
    reload_module(module["name"])

    for metric, updated in update_times.items():
        if metric in module["metrics"]:
            module["metrics"][metric]["last_updated"] = updated

    module["last_reload"] = time.time()
    log(f"Reloaded module {module['name']}, metrics: {', '.join([metric for metric in module['metrics']])}.", Fore.CYAN)

def log(msg, colour=None):
    print(f"{colour if colour else ''}{time.ctime()} {msg}{Style.RESET_ALL if colour else ''}")

check_new_modules()

if __name__ == "__main__":
    while True:
        start = time.time()
        check_new_modules()
        update_metrics()
        sleep = 5 - (time.time() - start)
        if sleep > 0:
            time.sleep(sleep)
