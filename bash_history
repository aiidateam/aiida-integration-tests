verdi process list -a
aiida-sleep workchain -nw 10 -nc 10 -t 10 --submit
aiida-sleep calc -n 10 -t 10 --submit
verdi shell
verdi daemon status
verdi status
verdi daemon start 2
aiida_config/run_all.sh
