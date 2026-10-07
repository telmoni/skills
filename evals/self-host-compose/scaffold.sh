#!/usr/bin/env bash
# The starting workspace: a fresh clone of the open-source platform, as the prompt describes.
set -euo pipefail
git clone --quiet --depth 1 https://github.com/telmoni/telmoni.git telmoni
