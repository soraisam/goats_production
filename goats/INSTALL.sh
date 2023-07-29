#!/bin/bash
# If any command fails, the script will immediately exit.
set -e

# Initialize variables.
PROJECT_NAME="GOATS"
# Define a usage/help function.
usage() {
  echo "This script sets up a Django project named GOATS with TOMToolkit and other plugins."
  echo "Usage: $0 [-n <project-name>] [-h for help]"
  exit 1
}

# Parse command-line arguments.
while getopts "n:h" OPTION; do
  case "${OPTION}" in
    n)
      PROJECT_NAME="${OPTARG}"
      ;;
    h)
      usage
      ;;
    *)
      usage
      ;;
  esac
done

# Ensure directory has been provided.
if [[ -z "${PROJECT_NAME}" ]]; then
  echo "You must specify a project name with the -n option."
  usage
fi

# Check if directory/goats exists.
if [[ -d "${PROJECT_NAME}" ]]; then
  read -p "The ${PROJECT_NAME} already exists. Do you want to remove it? [y/N] " confirm
  if [[ "${confirm}" == "y" ]]; then
    echo "Removing ${PROJECT_NAME}..."
    rm -r "${PROJECT_NAME}"
  else
    echo "Must delete existing GOATS instance, exiting."
    exit 1
  fi
fi

# Run the commands.
django-admin startproject $PROJECT_NAME
python modify_settings.py $PROJECT_NAME --add-tom-toolkit
python $PROJECT_NAME/manage.py tom_setup
python modify_settings.py $PROJECT_NAME --add-gemini --add-antares
python $PROJECT_NAME/manage.py migrate
python $PROJECT_NAME/manage.py runserver