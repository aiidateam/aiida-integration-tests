import gc
from aiida_sleep.cli import run_calc
from aiida_sleep.sleep_job import SleepCalculation
from pympler import muppy, refbrowser

run_calc(payload=int(1e6), output=int(1e6))

gc.collect()
all_objects = muppy.get_objects()
calcs = [o for o in all_objects if hasattr(o, "__class__") and isinstance(o, SleepCalculation)]
calcs

cb = refbrowser.ConsoleBrowser(calcs[0], maxdepth=3)
cb.print_tree()
