## openplotter-avnav

OpenPltter app to manage dashboards. 

### Installing

#### For production

Install

```
sudo apt-get install -y --no-install-recommends apt-transport-https ca-certificates curl software-properties-common
sudo wget -qO - https://open-mind.space/repo/open-mind.space.gpg.key | sudo apt-key add -
echo 'deb https://open-mind.space/repo buster-stable avnav avnavtouch misc' | sudo tee -a /etc/apt/sources.list.d/open-mind.list
```

[openplotter-settings](https://github.com/openplotter/openplotter-settings) for **production** and just install this app from *OpenPlotter Apps* tab.

#### For development

Install

```
sudo apt-get install -y --no-install-recommends apt-transport-https ca-certificates curl software-properties-common
sudo wget -qO - https://open-mind.space/repo/open-mind.space.gpg.key | sudo apt-key add -
echo 'deb https://open-mind.space/repo buster-stable avnav avnavtouch misc' | sudo tee -a /etc/apt/sources.list.d/open-mind.list
```

[openplotter-settings](https://github.com/openplotter/openplotter-settings) for **development**.

Clone the repository:

`git clone https://github.com/openplotter/openplotter-avnav`

Make your changes and create the package:

```
cd openplotter-avnav
dpkg-buildpackage -b
```

Install the package:

```
cd ..
sudo dpkg -i openplotter-avnav_x.x.x-xxx_all.deb
```

Run:

`openplotter-avnav`

Make your changes and repeat package and installation steps to test. Pull request your changes to github and we will check and add them to the next version of the [Debian package](https://launchpad.net/~openplotter/+archive/ubuntu/openplotter).

### Documentation

https://openplotter.readthedocs.io

### Support

http://forum.openmarine.net/forumdisplay.php?fid=1
