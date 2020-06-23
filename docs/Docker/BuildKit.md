
# Docker buildx

## Install

Install with one-liner.

```
mkdir -p  ~/.docker/cli-plugins && \
docker run --rm alpine:latest sh -c "\
    apk add --no-cache curl jq sed > /dev/null \
 && curl -sSL https://api.github.com/repos/docker/buildx/releases/latest | \
    jq '.assets[].browser_download_url' | grep linux-amd64 | sed -e 's/^\"//' -e 's/\"$//' | xargs curl -sSL \
" > ~/.docker/cli-plugins/docker-buildx \
 && chmod a+x ~/.docker/cli-plugins/docker-buildx
```

[]: https://docs.docker.com/buildx/working-with-buildx/
[]: https://github.com/marketplace/actions/docker-buildx
