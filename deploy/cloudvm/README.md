OSSLAB UI

# manual
the manual steps to deploy cloudvm service

## install packages

```
sudo apt-get update
sudo apt-get install apache2 git python-pip libapache2-mod-wsgi
```

## clone source code

```
mkdir -p ~/github
cd ~/github
git clone https://github.com/msopentechcn/LABOSS.git
```

## install python libs

```
cd LABOSS
sudo pip install -r osslab/requirement.txt
```

## configure logs

```
sudo mkdir /var/log/osslab
sudo chown www-data:www-data /var/log/osslab
```

## configure apache2
update `<src_root>/cloudvm/cloudvm.conf` and `<src_root>/cloudvm/src/app.wsgi` if you clone your code in a different directory other than
the default one(`/home/opentech/github/laboss`)

```
sudo cp ./cloudvm.conf /etc/apache2/sites-available
cd /etc/apache2/sites-enabled
sudo ln -s ../sites-available/cloudvm.conf cloudvm.conf
sudo service apache2 restart
```

_Note: if the target directory is changed, update `<src_root>/cloudvm/src/app.wsgi` and `/etc/apache2/sites-available/cloudvm.conf` too._