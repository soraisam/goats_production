# Gemini Observation and Analysis of Targets System (GOATS)

[![Run Flake8](https://github.com/gemini-hlsw/goats/actions/workflows/run_flake8.yaml/badge.svg?branch=main&event=push)](https://github.com/gemini-hlsw/goats/actions/workflows/run_flake8.yaml)
[![Run Tests](https://github.com/gemini-hlsw/goats/actions/workflows/run_tests.yaml/badge.svg?branch=main&event=push)](https://github.com/gemini-hlsw/goats/actions/workflows/run_tests.yaml)
[![Run HTMLHint](https://github.com/gemini-hlsw/goats/actions/workflows/run_htmlhint.yaml/badge.svg?branch=main&event=push)](https://github.com/gemini-hlsw/goats/actions/workflows/run_htmlhint.yaml)
[![Run StyleLint](https://github.com/gemini-hlsw/goats/actions/workflows/run_stylelint.yaml/badge.svg?branch=main&event=push)](https://github.com/gemini-hlsw/goats/actions/workflows/run_stylelint.yaml)
[![Run JS Tests](https://github.com/gemini-hlsw/goats/actions/workflows/run_js_tests.yaml/badge.svg?branch=main&event=push)](https://github.com/gemini-hlsw/goats/actions/workflows/run_js_tests.yaml)

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

# GOATS CLI Guide

The **Gemini Observation and Analysis of Targets System (GOATS)** CLI provides an efficient way to install and manage the GOATS project along with the antares2goats browser extension. You can get detailed help on each command using the `--help` option. Below, find the breakdown of the primary commands and options:

## Getting Started

Use the following command to get an overview of available options and commands:

`goats --help`

### Available Commands

1. `install`: Installs GOATS along with the optional antares2goats browser extension.

   `goats install [OPTIONS]`

   #### Options
   - `-p, --project-name TEXT`: Specify a custom project name (default: 'GOATS').
   - `-d, --directory PATH`: Specify the parent directory where GOATS will be installed (default: current directory).
   - `--overwrite`: Overwrite the existing project, if it exists (default: False).
   - `--browser [chrome|safari|firefox]`: Specify the browser for which to install the extension.

   Get more information with:

   `goats install --help`

2. `install-extension`: Installs the antares2goats browser extension for a specified browser.

   `goats install-extension [OPTIONS] {chrome|safari|firefox}`

   #### Options
   - `--help`: Show the help message and exit.

   Get more information with:

   `goats install-extension --help`

3. `run`: Starts the server for the GOATS project.

   `goats run [OPTIONS]`

   #### Options
   - `-p, --project-name TEXT`: Specify a custom project name (default: 'GOATS').
   - `-d, --directory PATH`: Specify the parent directory where GOATS is installed (default: current directory).
   - `--reloader`: Runs the server with a reloader for active development.

   Get more information with:

   `goats run --help`

## References and Documentation

- [GOATS Confluence](https://noirlab.atlassian.net/wiki/spaces/GOATS/overview)
- [GOATS Jira Board](https://noirlab.atlassian.net/jira/software/projects/GOATS/boards/57)
