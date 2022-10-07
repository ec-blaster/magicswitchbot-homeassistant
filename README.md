[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub_Latest_Release](https://img.shields.io/github/release/ec-blaster/magicswitchbot-homeassistant.svg?style=for-the-badge)](https://github.com/ec-blaster/magicswitchbot-homeassistant/releases/latest)


{% if prerelease %}
## **NB!** This is a beta/pre-release version!
{% endif %}

# Magic Switchbot component for Home Assistant
A [Home Assistant](https://home-assistant.io) component for controlling [Magic Switchbot](https://www.interear.com/smart-products/magic-bluetooth-switchbot.html) devices.

Using this component you can control on / off /push states of these little devices that can be used on usually not-smart appliances (coffee makers, air conditioners, radios, washing machines, etc). You can read a review of the device at my [library repository](https://github.com/ec-blaster/pyMagicSwitchbot).

## Special requirements

This component is based on a `bleak` library to communicate with the devices via BLE (Bluetooth Low Energy), so theoretically it should work on Linux, Windows or Mac.

If you are running Home Assistant Core as a non-root user, you must read the section "Notes for Home Assistant Core Installations" at [this integration](https://www.home-assistant.io/integrations/bluetooth_le_tracker/#rootless-setup-on-core-installs) documentation. In fact you should run these commands to get the required permissions for HA to access the bluetooth controller:

``` bash
sudo apt-get install libcap2-bin
sudo setcap 'cap_net_raw,cap_net_admin+eip' $(readlink -f $(which python3))
sudo setcap 'cap_net_raw+ep' $(readlink -f $(which hcitool))
```

## Installation

### Using [HACS](https://hacs.xyz/) (recommended)

This integration can be installed using HACS.
To do it search for `Magic Switchbot` in *Integrations* section.

### Manual

You can also install it manually:

1. Download or clone the repository .
2. Create (if it doesn't exist) a folder named `custom_components` inside your home assistant configuration folder.
3. Copy the magicswitchbot folder from the downloaded copy of the repository inside the `custom_components` folder

This is an example of what you can do to manually install the component:

```bash
$ cd /tmp
$ git clone https://github.com/ec-blaster/magicswitchbot-homeassistant
$ cd ~/.homeassistant
$ mkdir custom_components
$ cd custom_components
$ cp -R /tmp/magicswitchbot-homeassistant/custom_components/magicswitchbot .
$ rm -rf /tmp/magicswitchbot-homeassistant

```

## Configuration

* The component now is now configured from the UI, but before using it you must have the [bluetooth integration](https://www.home-assistant.io/integrations/bluetooth/) installed.
* Once you have your bluetooth interface working, you must click on Setting.
* Next click on "Devices & Services".
* Finally on "+ADD INTEGRATION".
* Type "Magic Switchbot" and a wizard will guide you to add a new MagicSwitchbot device. The device is identified by its MAC address, and you have to enter the name you will give to your device and the PIN you have set with the official Android app (optional).

When you enter the "Devices & Services option", your device may be have been discovered by Home Assistant. If this happens, you don't press "+ADD INTEGRATION", but directly click on it instead.

**BREAKING CHANGE**: If you had previously used an older version of the integration, you must delete your configuration options from your `yaml`file. It will not work this way any more.

## Device and Entities

When you add a MagicSwitchbot device, Home Assistant will create a device and 2 entities in it:

* A **switch**, with the entity_id: `switch.<configured_name>`.

  This is the default entity we used in previous versions of the integration.

  With the switch entity, you can use the Magic Switchbot as a switch, with states "On" and "Off". You must use an add-on that is shipped with the device and is sticked over the real switch you want to activate or deactivate, it works like a "hook" that pulls the switch when its state changes to "Off".

* A **button**, with the entity_id: `button.<configured_name>`. 

  With the button entity, the Magic Switchbot uses another mode that just "pushes" a button and retracts a little after that.

  **Breaking change**: We have no more a `push` service defined in the switch entity.

### Use examples

This is an example of an automation that "pushes the button" of the coffee maker at 6:30AM every working day.

```yaml
automation:
  - alias: Switch on coffee maker
    trigger:
      - platform: time
        at: '06:30:00'
    condition:
      condition: time
      weekday:
        - mon
        - tue
        - wed
        - thu
        - fri
    action:
      - service: button.press
        target:
          entity_id: button.magic_1
      
```

This is another example of how to use the component from lovelace:

```yaml
type: entities
title: Magic Switchbot Example
show_header_toggle: false
state_color: true
entities:
  - type: section
    label: Magic Switchbot 1
  - entity: switch.magic_1
    secondary_info: last-changed
    name: Switch
  - entity: switch.magic_1
    type: attribute
    attribute: battery_level
    name: Battery
    suffix: '%'
    icon: 'mdi:battery'
  - type: button
    name: Push button
    icon: 'mdi:gesture-tap-button'
    tap_action:
      action: call-service
      service: button.press
      target:
        entity_id: button.magic_1
    action_name: Push
  - type: section
    label: Magic Switchbot 2
  - entity: switch.magic_2
    secondary_info: last-changed
    name: Switch
  - entity: switch.magic_2
    type: attribute
    attribute: battery_level
    name: Battery
    suffix: '%'
    icon: 'mdi:battery'
  - type: button
    name: Push button
    icon: 'mdi:gesture-tap-button'
    tap_action:
      action: call-service
      service: button.press
      target:
        entity_id: button.magic_2
    action_name: Push

```

If you like my work, it is useful to you and you want to, you can buy me a coffee. Thanks.

<a href="https://www.buymeacoffee.com/ecblaster" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

