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

## Docker

This is really meant to be run as a Docker container, but really can run on the CLI or in the background on any platform with Python3.

Get the image with `docker pull pww217/kasa-control`

## Docker Compose

Here's an example docker-compose file. Very simple with all storage internal and no real need for fancy networking.

```yaml
kasa-control:
      environment:
            - TZ=America/Chicago
      container_name: kasa-control
      restart: unless-stopped
      image: pww217/kasa-control:latest
```

Then `docker-compose up -d` to run it as a service.
