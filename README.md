# Bin Canary

Dockerised python script that can notify NTFY and Discord channels when a bin is due to be collected in the next 24 hours

## Supported Council Websites
- South Ribble

# How to Use
- Make use of the docker compose example below or the example in the repo
- Set the following env vars
    - COUNCIL=South-Ribble
    - ADDRESS=1
    - POSTCODE=AA123ZZ
    - NTFY-https://<ntfy webhook> (optional)
    - DISCORD=<discord webhook> (optional)
    - INTERVAL=24 (optional) - This is the checking interval, the notifier only fires if the bin is collected tomorrow.
    - DELAY=False (optional) Delay notification to 7pm. (default: true)

## Docker Compose Example

```
version: "3.3"

services:
  bin-canary:
    image: ghcr.io/josephrpalmer/bin-canary:latest
    container_name: bin-canary
    restart: always
    environment:
      - COUNCIL=South-Ribble
      - ADDRESS=1
      - POSTCODE=AA123ZZ


```
