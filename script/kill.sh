#! /usr/bin/env bash
parallel-ssh -P -h $1 "pkill -u `whoami` $2"
