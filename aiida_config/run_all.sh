#!/bin/bash
set -ex

cd "$(dirname "$0")"

# profile
verdi quicksetup -n --config quicksetup.yml
verdi status

# computers
verdi computer setup -n --config computer-local.yml
verdi computer configure local local -n --config computer-local.yml
verdi computer test local
verdi computer setup -n --config computer-slurm.yml
verdi computer configure ssh slurm -n --config computer-slurm.yml
verdi computer test slurm

# codes
verdi code setup -n --config code-local-sleep.yml
verdi code setup -n --config code-slurm-sleep.yml

# daemon
verdi daemon start 1
