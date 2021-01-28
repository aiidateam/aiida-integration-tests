# -*- coding: utf-8 -*-
import gc

from pympler import muppy, refbrowser

from aiida_sleep.cli import run_calc
from aiida_sleep.sleep_job import SleepCalculation

run_calc(
    code="sleep@local", payload=int(5e5), output_dict=int(5e5), output_array=int(5e5)
)

gc.collect()
all_objects = muppy.get_objects()
calcs = [
    o
    for o in all_objects
    if hasattr(o, "__class__") and isinstance(o, SleepCalculation)
]
len(calcs)

cb = refbrowser.ConsoleBrowser(calcs[0], maxdepth=3)
tree = cb.get_tree()
cb.print_tree(tree)
