# kasa-control
## Overview

This works with all the initial features I intended:

- Runs as a low-impact service
- Scheduling for daily jobs
- Fully customizable routines, colors, transition times, etc. See `config.yaml`
- Full parallelism - both of routines and API calls. It can all execute simultaneously.
- One time jobs: power on, off, change brightness, customizable transitions
- Continuous jobs can rotate/siren through colors until a certain time

I made this originally because the TPLink app does not support a number of things I wanted to do. And to learn some stuff.

Originally I thought about making it a container that runs as a continuous service, running scheduled routines and jobs.

## Configuration

See [config.yaml](./config.yaml) for more information about setting up routines and lights.
