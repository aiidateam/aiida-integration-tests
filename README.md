# aiida-integration-tests

 A repository for creating reproducible integration tests.

Using:

```console
$ docker-compose up --build -d
```

Will start-up a network with four containers will be created:

- `aiida-int-postgres`: The database server (PostgreSQL)
- `aiida-int-rmq`: The message broker client (RabbitMQ)
- `aiida-int-slurm`: An example compute server, with SLURM job scheduler
- `aiida-int-core`: The AiiDA control node

Logging into the `aiida-int-core` container, you can then run the configuration to create a profile, connected to the postgres and rabbitmq servers, and a computer connected to the slurm server:

```console
$ docker exec -it aiida-int-core /bin/bash
root@684f7f913384:~# aiida_config/run_all.sh
```

Finally to tear down the network:

```console
$ docker-compose down -v
```
