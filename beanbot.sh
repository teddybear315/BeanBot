#!/bin/bash

function help_message {
    echo "# BeanBot

Welcome to BeanBot, you should be reading this via the BeanBot script.
The point of this script is to provide useful and easy ways to access commonly used terminal commands.

This script was created by Luke Whrit <me@lukewhrit.xyz> (https://lukewhrit.xyz)

# Available Commands

\"help\" (./beanbot help) - Print's help information to STDOUT
\"start\" (./beanbot start) - Initiate's the main python process for BeanBot
\"lint\" (./beanbot lint) - Begin's linting BeanBot's source code using black
\"install\" (./beanbot install) - Install's all python modules in requirements.txt"
}

case $1 in
    "help")
        help_message
    ;;

    "start")
        python src/beanbot.py
    ;;

    "lint")
        black --check -t py37 src/
    ;;

    "fix")
        black -t py37 src/
    ;;

    "install")
        pip3.7 install -r C:\\Users\\lukew\\Documents\\Projects\\Python\\BeanBot\\requirements.txt
    ;;

    *)
        help_message
    ;;
esac
