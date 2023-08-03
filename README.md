# Gemini Observation and Analysis of Targets System (GOATS)

[![Run Flake8](https://github.com/gemini-hlsw/goats/actions/workflows/run_flake8.yaml/badge.svg?branch=main&event=push)](https://github.com/gemini-hlsw/goats/actions/workflows/run_flake8.yaml)
[![Run Tests](https://github.com/gemini-hlsw/goats/actions/workflows/run_tests.yaml/badge.svg?branch=main&event=push)](https://github.com/gemini-hlsw/goats/actions/workflows/run_tests.yaml)
[![Run HTMLHint](https://github.com/gemini-hlsw/goats/actions/workflows/run_htmlhint.yaml/badge.svg?branch=main&event=push)](https://github.com/gemini-hlsw/goats/actions/workflows/run_htmlhint.yaml)

This is an end-to-end integrated system for time-domain and multimesseneger astronomy (TDAMM) aimed towards Gemini follow-up observations.

Its objective is to simplify the TDAMM workflow for users by serving as a one-stop shop for all the follow-up needs. To this end, it will integrate the various TDAMM services of Gemini Observatory and the larger NOIRLab organization.

<img
  src="doc/graphics/goats_with_lab.jpg"
  alt="Schematic of GOATS"
  title="Ecosystem of GOATS"
  style="display: inline-block; margin: 0 auto; max-width: 400px">

## Installation

```shell
git clone https://github.com/gemini-hlsw/goats.git
cd goats
pip install .
```

## Command Line Interface

The GOATS Command Line Interface (CLI) allows for easy management of your GOATS.

### Usage

```shell
goats [OPTIONS] COMMAND [ARGS]...
```

### Global Options

`--help`  : Show this message and exit.

### Commands

1. `install`: Creates a new GOATS instance with a specified or default name in a specified or default directory.
2. `run`: Starts the Django development server for a specified GOATS in a specified or default directory.

### Subcommands

#### `install`

Use this command to create a new GOATS instance.

```shell
goats install [OPTIONS]
```

##### Options
- `-p, --project-name TEXT`: Specify a custom GOATS name. Default is 'GOATS'.
- `-d, --directory PATH`: Specify the parent directory where GOATS will be created. Default is the current directory.
- `--overwrite`: Overwrite the existing GOATS, if it exists.
- `--help`: Show this message and exit.

#### `run`

Use this command to start the Django development server for a GOATS instance.

```shell
goats run [OPTIONS]
```

##### Options
- `-p, --project-name TEXT`: Specify a custom project name to look for. Default is 'GOATS'.
- `-d, --directory PATH`: Specify the parent directory where the GOATS instance is. Default is the current directory.
- `--reloader`: Runs Django with reloader for active development.
- `--help`: Show this message and exit.

## References and Documentation

- [GOATS Confluence](https://noirlab.atlassian.net/wiki/spaces/GOATS/overview)
- [GOATS Jira Board](https://noirlab.atlassian.net/jira/software/projects/GOATS/boards/57)
