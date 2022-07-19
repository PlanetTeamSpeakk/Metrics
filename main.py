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
    metrics[module_name] = {"name": module_name, "module": module, "path": path.replace('.', '/') + ".py", "last_reload": time.time(), "register": register_metric, "metrics": {}}

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
    db.check_reconnect()
    cursor = db.db.cursor()

    for module in metrics.values():
        if os.path.exists(module["path"]) and os.path.getmtime(module["path"]) > module["last_reload"]:
            print(f"Module {module['name']} changed, attempting reload!")

            update_times = {metric: module["metrics"][metric]["last_updated"] for metric in module["metrics"]}
            reload_module(module["name"])

            for metric, updated in update_times.items():
                if metric in module["metrics"]:
                    module["metrics"][metric]["last_updated"] = updated

            module["last_reload"] = time.time()

            print(f"Reloaded module {module['name']}, metrics: {', '.join([metric for metric in module['metrics']])}.")

        for metric in module["metrics"].values():
            if time.time() - metric["last_updated"] < ((metric["interval"] if not metric["errored"] else metric["error_interval"]) - 0.5):
                continue

            value = None

            try:
                value = metric["function"](cursor)
            except Exception as e:
                print(f"Error updating metric {metric['name']} of module {module['name']}: " + str(e))
                metric["errored"] = True
                continue
            metric["errored"] = False

            if value is None:
                continue

            updated = True
            metric["last_updated"] = time.time()
            print(f"{time.ctime()} Updated metric {metric['name']}, value: {value}")

    if updated:
        db.db.commit()

for (dirpath, dirnames, filenames) in os.walk("metrics"):
     if "__pycache__" in dirpath:
         continue

     for f in filter(lambda f: f.endswith(".py"), filenames):
        register_module(dirpath.replace('/', '.') + ('.' if not len(dirpath) == 0 else '') + f[:-3])

if __name__ == "__main__":
    while True:
        start = time.time()
        update_metrics()
        sleep = 5 - (time.time() - start)
        if sleep > 0:
            time.sleep(sleep)
