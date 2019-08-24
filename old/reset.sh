#!/bin/bash - 
#===============================================================================
#
#          FILE: reset.sh
# 
#         USAGE: ./reset.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: 03.02.2019 16:43
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

rm data/*
rm index/*
