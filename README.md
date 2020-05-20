## openplotter-avnav

Avnav is a fast, web-based chart plotter that is optimized for touch screens

#### Dependencies

Download latest release of https://github.com/openplotter/openplotter-settings/releases and change to the directory where your download file is.

```
sudo apt install ./openplotter-settings_2.xxxxx-stable_all.deb
```

From openplotter-settings you should install [openplotter-signalk-installer].

### Install

Clone the repository:

```
cd ~
git clone https://github.com/openplotter/openplotter-avnav.git
```

(Make your changes and) create the package:

```
cd openplotter-avnav
dpkg-buildpackage -b
```

Install the package:

```
cd ..
sudo apt install ./openplotter-avnav_x.x.x-xxx_all.deb
```

### Run

`openplotter-avnav`

Or start Avnav from the menu (same place as openplotter-settings).