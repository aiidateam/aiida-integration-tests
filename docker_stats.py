#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""CLI to log docker stats to a CSV file."""
import argparse
import datetime
import os
import re
import subprocess
import time

HEADER = "name,cpu_percent,mem,mem_percent,netio,blockio,pids,datetime"
REGEX_SIZE = re.compile(r"(\d+(?:\.\d+)?)([a-zA-Z]+)")
CONVERT_MAP = {
    "b": 1000000,
    "kib": 1000,
    "kb": 1000,
    "mib": 1,
    "mb": 1,
    "gib": 1 / 1000,
    "gb": 1 / 1000,
}
LABEL_MAP = {
    "cpu_percent": "CPU (%)",
    "mem": "Memory (Mb)",
    "mem_percent": "Memory (%)",
    "netio": "Network I/O (Mb)",
    "blockio": "Block I/O (Mb)",
    "pids": "Subprocesses",
}


def get_stats(quiet=False, handle=None):
    current_time = datetime.datetime.now()
    data = subprocess.check_output(
        [
            "docker",
            "stats",
            "--no-stream",
            "--format",
            "{{.Name}},{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}},{{.NetIO}},{{.BlockIO}},{{.PIDs}}",
        ],
        encoding="utf8",
    )
    lines = [f"{line.rstrip()},{current_time}" for line in data.rstrip().splitlines()]
    text = "\n".join(lines)
    if not quiet:
        print(text)
    if handle:
        handle.write(text + "\n")
        handle.flush()


def cli():
    parser = argparse.ArgumentParser(description="Record docker stats to CSV.")
    parser.add_argument(
        "-o", "--output", metavar="PATH", type=str, default="", help="Output to file"
    )
    parser.add_argument(
        "-i", "--interval", type=float, default=1, help="Polling interval (seconds)"
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Do not print output"
    )
    parser.add_argument(
        "-p",
        "--plot",
        metavar="COLUMN",
        type=str,
        help="Plot a column from an existing output CSV.",
    )
    parser.add_argument(
        "-e",
        "--plot-ext",
        metavar="EXT",
        type=str,
        default="pdf",
        help="Extension of output plot.",
    )
    args = parser.parse_args()
    if args.plot:
        plot_column(
            args.output,
            args.plot,
            os.path.splitext(args.output)[0] + f"-{args.plot}.{args.plot_ext}",
        )
        return
    if args.output and os.path.exists(args.output):
        raise IOError("output path exists, delete first")
    if not args.quiet:
        print(HEADER)
    if args.output:
        with open(args.output, "w", encoding="utf8") as handle:
            handle.write(HEADER + "\n")
            while True:
                get_stats(quiet=args.quiet, handle=handle)
                time.sleep(args.interval)
    else:
        while True:
            get_stats(quiet=args.quiet)
            time.sleep(args.interval)


def convert_size(text: str) -> float:
    """Convert memory size to megabytes float."""
    match = REGEX_SIZE.match(text)
    assert match, f"did not match regex: {text}"
    return float(match[1]) * CONVERT_MAP[match[2].lower()]


def to_df(path: str):
    """Convert a saved CSV to a pandas DataFrame (memory in megabytes)."""
    import pandas as pd

    # read
    df = pd.read_csv(path, index_col=False)
    # format columns
    df.mem_percent = df.mem_percent.str.rstrip("%").astype("float")
    df.cpu_percent = df.cpu_percent.str.rstrip("%").astype("float")
    df.mem = df.mem.apply(lambda x: convert_size(x.split("/")[0]))
    df.netio = df.netio.apply(lambda x: convert_size(x.split("/")[0]))
    df.blockio = df.blockio.apply(lambda x: convert_size(x.split("/")[0]))
    df.pids = df.pids.astype("int")
    df.datetime = pd.to_datetime(df.datetime)
    return df


def plot_column(path: str, column: str, outpath: str = ""):
    """Plot a single column and save to file."""
    df = to_df(path)
    col_df = df.set_index(["name", "datetime"])[column].unstack("name")
    ax = col_df.plot(grid=True)
    ax.set_xlabel("Time")
    ax.set_ylabel(LABEL_MAP[column])
    if outpath:
        ax.get_figure().savefig(outpath, bbox_inches="tight")
    return ax


if __name__ == "__main__":
    cli()
