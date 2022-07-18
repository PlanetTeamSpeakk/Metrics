import creds
import time
import db
import os
import os.path
import importlib
import traceback

metrics = {}

def register_module(path):
    module = importlib.import_module(path)
    if not hasattr(module, "setup"):
        print(f"Module {path} has no setup function.")
        return

    def register_metric(name, interval, error_interval, function, *args, **kwargs):
        metrics[module_name]["metrics"][name] = {"name": name, "interval": interval, "error_interval": error_interval, "function": function, "last_updated": 0, "errored": False}

    module_name = path[len("metrics."):]
    metrics[module_name] = {"name": module_name, "module": module, "register": register_metric, "metrics": {}}

    module.setup(register=register_metric, db=db.db)
    print(f"Registered module {module_name} with metrics {', '.join([metric for metric in metrics[module_name]['metrics']])}.")

def reload_module(module):
    module = metrics[module]

    if hasattr(module["module"], "on_reload"):
        module["module"].on_reload()

    importlib.reload(module["module"])

    module["metrics"] = {}
    module["module"].setup(register=module["register"], db=db.db)

def update_metrics():
    updated = False
    cursor = db.db.cursor()

    for module in metrics.values():
        for metric in module["metrics"].values():
            if time.time() - metric["last_updated"] < ((metric["interval"] if not metric["errored"] else metric["error_interval"]) - 0.5):
                continue

            value = None

            try:
                value = metric["function"](c=cursor)
            except Exception as e:
                print(f"Error updating metric {metric['name']} of module {module['name']}: " + str(e))
                metric["errored"] = True
                continue
            metric["errored"] = False

            if value is None:
                continue

            updated = True
            metric["last_updated"] = time.time()
            print(f"{time.ctime()} Updated metric {metric['name']}, value: {value}.")

    if updated:
        db.check_reconnect()
        db.db.commit()

for (dirpath, dirnames, filenames) in os.walk("metrics"):
     if "__pycache__" in dirpath:
         continue

     for file in [dirpath.replace('/', '.') + ('.' if not len(dirpath) == 0 else '') + f[:-3] for f in filter(lambda f: f.endswith(".py"), filenames)]:
        register_module(file)

if __name__ == "__main__":
    while True:
        start = time.time()
        update_metrics()
        sleep = 5 - (time.time() - start)
        if sleep > 0:
            time.sleep(sleep)
