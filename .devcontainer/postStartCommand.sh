#!/bin/bash
# Post start command


# <Write your commands here>
echo "Post start command"
echo "Current directory: $(pwd)"
cd .. && make reinstall
