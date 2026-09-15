# Build environment for the reduced Virtual-On MAME target.
#
# Build and tag it as `von-mame-build:ubuntu26.04` (the tag `vonctl build
# remote` and `vonctl build docker` expect). Build locally with
# `vonctl build image`, or on a remote host with `vonctl build image-remote`.
FROM ubuntu:26.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        python3 \
        pkg-config \
        libsdl2-dev \
        libsdl2-ttf-dev \
        libfontconfig1-dev \
        libasound2-dev \
        libx11-dev \
        libxext-dev \
        libxinerama-dev \
        libxi-dev \
        libxrandr-dev \
        libxcursor-dev \
        libgl1-mesa-dev \
        libglu1-mesa-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
