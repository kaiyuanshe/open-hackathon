#!/usr/bin/env bash
pre_setup() {
    #for ubuntu 14
    #this requires root access
    export username=$(whoami)
    if ! $(id | grep -q "root"); then
        echo "switch to root user to run shell script pre_setup.sh"
    fi
    if $(lsb_release -d | grep -q "14"); then
        echo "deb https://apt.dockerproject.org/repo ubuntu-trusty main" > /etc/apt/sources.list.d/docker.list
    fi

    # for ubuntu 15
    if $(lsb_release -d | grep -q "15"); then
        echo "deb https://apt.dockerproject.org/repo ubuntu-wily main" > /etc/apt/sources.list.d/docker.list
    fi

    # for linux mint
    if $(lsb_release -d | grep -q "Mint"); then
        echo "deb https://apt.dockerproject.org/repo ubuntu-trusty main" > /etc/apt/sources.list.d/docker.list
    fi

    apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
    echo "switch to $username"
    su $username
}

pre_setup