### About

docker-enter is a tool that help you enter your docker containers easily. Find more about `nsenter` and `docker-enter` in [nsenter repository](https://github.com/jpetazzo/nsenter).


### Quick start

Copy executable `nsenter` and `docker-enter` to your path:
```
cp nsenter /usr/local/bin
chmod +x docker-enter
cp docker-enter /usr/local/bin
```

After that, you can enter your container by:
```
sudo docker-enter "container ID"
```

### More about nsenter installation
In case you want to build a newer version by yourself, following commands can be a reference.
```
curl https://www.kernel.org/pub/linux/utils/util-linux/v2.24/util-linux-2.24.tar.gz | tar -zxf-
cd util-linux-2.24
./configure --without-ncurses
make nsenter
```
