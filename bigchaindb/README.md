# Overview

A high-level description of the files and subdirectories of BigchainDB.

## Files

### `config_utils.py`

Methods for managing the configuration, including loading configuration files, automatically generating the configuration, and keeping the configuration consistent across BigchainDB instances.

### `consensus.py`

Base class for consensus methods (verification of votes, blocks, and transactions).  The actual logic is mostly found in `transaction` and `block` models, defined in `models.py`.

### `core.py`

The `Bigchain` class is defined here.  Most operations outlined in the whitepaper as well as database interactions are found in this file.  This is the place to start if you are interested in implementing a server API, since many of these class methods concern BigchainDB interacting with the outside world.

### `models.py`

`Block` and `Transaction` classes are defined here.  The classes mirror the block and transaction structure from the documentation, but also include methods for validation and signing.

### `monitor.py`

Code for monitoring speed of various processes in BigchainDB via `statsd` and Grafana.  See documentation.

### `processes.py`

Entry point for the BigchainDB process, after initialization.  All subprocesses are started here: processes to handle new blocks, votes, etc.

### `util.py`

Description

## Folders

### `commands`

Contains code for the CLI for BigchainDB.

### `db`

Code for building the database connection, creating indexes, and other database setup tasks.

### `pipelines`

Structure and implementation of various subprocesses started in `processes.py`.

### `web`

Description


