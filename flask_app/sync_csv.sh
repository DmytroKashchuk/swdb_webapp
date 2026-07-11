#!/bin/bash

# Cartella locale con i CSV
LOCAL_DIR="$HOME/Documents/swdb_webapp/flask_app/data/"

# Destinazione sul server
REMOTE_USER="dima"
REMOTE_HOST="10.20.5.20"
REMOTE_DIR="/home/dima/swdb_webapp/flask_app/data/"

# Trasferimento
rsync -avh --progress "$LOCAL_DIR" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR"