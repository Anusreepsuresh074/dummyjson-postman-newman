# Environments

Environment files with **non-secret values only** (`baseUrl`, limits). Credentials are passed at run time by `scripts/run-newman.sh` (`--env-var`), and tokens are set by test scripts during a run; neither is ever saved here.
