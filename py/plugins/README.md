# AetherOnePy Plugins
Welcome to AetherOnePy Plugins!

## Overview
Plugins enhance the functionality of AetherOnePy by allowing users to add custom features or modify existing ones. This modular approach enables a wide range of applications.

### Flagship Plugin AetherOnePySocial
Davor's vision for AetherOnePy is to create a social network for the AetherOnePy, which allows users to share their session analysis and compare results with others. The flagship plugin, AetherOnePySocial, is the first step towards this goal.

#### Installation:
````bash
# Clone the AetherOnePySocialPlugin repository into the plugins directory
cd py/plugins
git clone https://github.com/emolionl/AetherOnePySocialPlugin.git
````

This secondary step is only necessary temporarily, until AetherOnePy is able to automatically download and install plugins from the plugin repository.
````bash
# Install the plugin's dependencies
cd py
setup.py
````
Now you can start the AetherOnePy and use the social plugin.

## How to develop a plugin
Begin with a new fresh python project inside the `py/plugins` directory. The plugin should have a unique name and contain a `README.md` file that describes its functionality and how to use it.

Also add a `plugin.json` file that contains metadata about the plugin, such as its name, author, repository URL, UI name, image URL, and description. This file is used by AetherOnePy to recognize and manage the plugin.

````json
{
    "name":"AetherOnePySocial",
    "author":"emolionl",
    "repository":"https://github.com/emolionl/AetherOnePySocialPlugin",
    "ui":"aetheronepysocialplugin",
    "image":"https://raw.githubusercontent.com/emolionl/AetherOnePySocialPlugin/refs/heads/master/plugin.png",
    "description":"Share your sessions and analysis with other users using a unique token for identification"
}
````
Add an image to the plugin repository that will be used in the AetherOnePy UI. The image should have a ratio of 2:1. And please don't make it too big, in order to preserve loading performance.

Regarding the UI which is for now opened in a new tab, you can use AetherOnePySocial as an example or create your onw UI using whatever framework you like. The only requirement is that the UI should be able to communicate with the AetherOnePy and your own backend via API.