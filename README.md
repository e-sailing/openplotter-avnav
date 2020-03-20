## openplotter-avnav

OpenPlotter app to manage Avnav. 

### Installing

#### For development

Install

```
sudo apt-get install -y --no-install-recommends apt-transport-https ca-certificates curl software-properties-common
sudo wget -qO - https://open-mind.space/repo/open-mind.space.gpg.key | sudo apt-key add -
echo 'deb https://open-mind.space/repo buster-stable avnav avnavtouch misc' | sudo tee -a /etc/apt/sources.list.d/open-mind.list
```

[openplotter-settings](https://github.com/openplotter/openplotter-settings) for **development**.

Clone the repository:

`git clone https://github.com/e-sailing/openplotter-avnav.git`

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
