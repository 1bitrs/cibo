#!/bin/bash

# exit when any command fails
set -e

G='\033[0;32m' # green color
Y='\033[1;33m' # yellow color
N='\033[0m'    # No Color

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
ROOT="$DIR/.."

# black 和 isort 的配置都在 pyproject.toml 中
echo -e "${Y}Runnning black...${N}"
black -v $ROOT/cibo
black -v $ROOT/scripts
black -v $ROOT/demo


echo -e "${Y}Runnning isort...${N}"
isort "$ROOT/cibo/" "$ROOT/scripts/" "$ROOT/demo/"