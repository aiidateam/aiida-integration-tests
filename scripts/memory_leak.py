import gc
from aiida_sleep.cli import run_calc
from aiida_sleep.sleep_job import SleepCalculation
from pympler import muppy, refbrowser

run_calc(payload=int(5e5), output=int(5e5))

gc.collect()
all_objects = muppy.get_objects()
calcs = [o for o in all_objects if hasattr(o, "__class__") and isinstance(o, SleepCalculation)]
len(calcs)

cb = refbrowser.ConsoleBrowser(calcs[0], maxdepth=3)
tree = cb.get_tree()
cb.print_tree(tree)

import time; time.sleep(10)
