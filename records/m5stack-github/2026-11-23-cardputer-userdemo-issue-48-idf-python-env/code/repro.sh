#!/bin/bash
# Reproduce the two lines reported in m5stack/M5Cardputer-UserDemo#48 with
# ESP-IDF v6.1's own tools/check_python_dependencies.py.
#
# Requirements: a Python 3.13 interpreter, network access to PyPI, and an
# ESP-IDF v6.1 checkout (IDF_PATH). Everything is created under /tmp; the
# script never touches ~/.espressif or an existing IDF environment.
#
# Usage: IDF_PATH=/path/to/esp-idf-6.1 PYTHON=/path/to/python3.13 ./repro.sh
set -eu

IDF_PATH=${IDF_PATH:?set IDF_PATH to an ESP-IDF v6.1 checkout}
PYTHON=${PYTHON:?set PYTHON to a python3.13 interpreter}
CHECK="$IDF_PATH/tools/check_python_dependencies.py"
CORE="$IDF_PATH/tools/requirements/requirements.core.txt"
CONSTR=${CONSTR:-$HOME/.espressif/espidf.constraints.v6.1.txt}   # or download:
# curl -sfL https://dl.espressif.com/dl/esp-idf/espidf.constraints.v6.1.txt -o "$CONSTR"

echo "== A. clean v6.1 env passes"
rm -rf /tmp/idf61-repro-a && "$PYTHON" -m venv /tmp/idf61-repro-a
/tmp/idf61-repro-a/bin/pip -q install -r "$CORE" -c "$CONSTR"
IDF_PYTHON_ENV_PATH=/tmp/idf61-repro-a /tmp/idf61-repro-a/bin/python "$CHECK" -r "$CORE" -c "$CONSTR"

echo "== B. downgrade rich-click -> 'Requirement rich-click~=1.9.0 was not met. Installed version: 1.8.9'"
/tmp/idf61-repro-a/bin/pip -q install "rich-click==1.8.9"
IDF_PYTHON_ENV_PATH=/tmp/idf61-repro-a /tmp/idf61-repro-a/bin/python "$CHECK" -r "$CORE" -c "$CONSTR" || true

echo "== C. break bitarray metadata -> misleading 'Error while checking requirement ... No package metadata was found for bitarray'"
rm -rf /tmp/idf61-repro-c && "$PYTHON" -m venv /tmp/idf61-repro-c
/tmp/idf61-repro-c/bin/pip -q install packaging "rich-click==1.8.9" "bitstring==4.4.0"
SP=$(/tmp/idf61-repro-c/bin/python -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")
rm -rf /tmp/bitarray-dist-info-quarantine
mv "$SP"/bitarray-*.dist-info /tmp/bitarray-dist-info-quarantine
printf 'packaging\nrich-click\nbitstring\n' > /tmp/repro-req.txt
printf 'rich-click~=1.9.0\n' > /tmp/repro-constraints.txt
for i in 1 2 3 4 5 6; do
  echo "---- run $i"
  /tmp/idf61-repro-c/bin/python "$CHECK" -r /tmp/repro-req.txt -c /tmp/repro-constraints.txt || true
done
# The requirement name printed before "Package was not found" comes from a stale
# loop variable and changes between runs; the package after the colon is always bitarray.
