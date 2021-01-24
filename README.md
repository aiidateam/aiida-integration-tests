# aiida-integration-tests

A repository for creating a reproducible AiiDA system, primarily for testing integration and performance.

Using:

```console
$ docker-compose up --build -d
```

Will start-up a network with four containers:

- `aiida-int-postgres`: The database server (PostgreSQL)
- `aiida-int-rmq`: The message broker client (RabbitMQ)
- `aiida-int-slurm`: An example compute server, with SLURM job scheduler
- `aiida-int-core`: The AiiDA control node

You can monitor the resources used by each container using:

```console
$ docker stats
CONTAINER ID   NAME                 CPU %     MEM USAGE / LIMIT     MEM %     NET I/O           BLOCK I/O         PIDS
f5b693b71c51   aiida-int-core       3.33%     388.3MiB / 1.942GiB   19.53%    10MB / 5.67MB     20.1MB / 11.1MB   30
ceda3a229762   aiida-int-postgres   0.10%     55.55MiB / 1.942GiB   2.79%     5.09MB / 9.54MB   23.7MB / 82.7MB   11
ef718edadb6e   aiida-int-rmq        56.18%    98.17MiB / 1.942GiB   4.94%     160kB / 157kB     25.5MB / 946kB    92
b6840be9fb97   aiida-int-slurm      6.25%     20.26MiB / 1.942GiB   1.02%     414kB / 319kB     5.05MB / 815kB    20
```

You can also access the RabbitMQ management console via http://localhost:15673 (user: guest, password: guest).

Logging into the `aiida-int-core` container, you can then run the configurations to create a profile, connected to the postgres and rabbitmq servers, and computers connected locally and to the slurm server:

```console
$ docker exec -it aiida-int-core /bin/bash
root@xxx:~# aiida_config/run_all.sh
```

This will also create codes (local/slurm) for the included `aiida-sleep` plugin, providing a `SleepCalcJob`,
that simply runs the Unix `sleep` command, and a `SleepWorkChain` that calls `n` `SleepCalcJob` children.

```console
root@xxx:~# aiida-sleep calc -n 1 -t 10
uuid: 631e4bb9-748c-4f0e-bc50-e2e791012859 (pk: 119) (aiida.calculations:sleep)
root@xxx:~# aiida-sleep workchain -nw 1 -nc 10 -t 10
uuid: 6ba78b23-8069-459e-a2eb-8e867972044b (pk: 124) (aiida.workflows:sleep)
```

You can also call them from an ipython shell:

```python
root@xxx:~# verdi shell
In [1]: from aiida_plugin.cli import run_calc, run_workchain
In [2]: run_workchain()
Out[2]: <WorkChainNode: uuid: 122b158c-0408-406f-8a7b-33fa9ba30bf1 (pk: 134) (aiida.workflows:sleep)>
```

Finally to tear down the network:

```console
$ docker-compose down -v
```
