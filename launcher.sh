#!/bin/bash
source /reg/g/pcds/pyps/conda/dev_conda
pushd /reg/neh/home/slepicka/sandbox/git-pcdshub/pmps-ui
PYTHONPATH=/reg/neh/home/slepicka/sandbox/git-slaclab/pydm-git:$PYTHONPATH pydm --hide-nav-bar --hide-menu-bar --hide-status-bar pmps.py
popd