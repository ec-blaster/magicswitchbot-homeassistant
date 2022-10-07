[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

# Magic Switchbot component for Home Assistant
A [Home Assistant](https://home-assistant.io) component for controlling [Magic Switchbot](https://www.interear.com/smart-products/magic-bluetooth-switchbot.html) devices.

Using this component you can control on / off /push states of these little devices that can be used on usually not-smart appliances (coffee makers, air conditioners, radios, washing machines, etc). You can read a review of the device at my [library repository](https://github.com/ec-blaster/pyMagicSwitchbot).

## Special requirements

This component is based on a library that uses `bluepy` to communicate with the devices via BLE (Bluetooth Low Energy), and only works on Linux.

Depending on your system configuration, Python will try to install or compile `bluepy` on the first use. If you get a compile error when starting Home Assistant, you may have some Linux libraries missing. Try to install them:

```bash
$ sudo apt-get install build-essential
$ sudo apt-get install libglib2.0-dev
```

and then restart Home Assistant.

Additionally, if you are running Home Assistant Core as a non-root user, you must read the section "Notes for Home Assistant Core Installations" at [this integration](https://www.home-assistant.io/integrations/bluetooth_le_tracker/#rootless-setup-on-core-installs) documentation. In fact you should run these commands to get the required permissions for HA to access the bluetooth controller:

``` bash
sudo apt-get install libcap2-bin
sudo setcap 'cap_net_raw,cap_net_admin+eip' $(readlink -f $(which python3))
sudo setcap 'cap_net_raw+ep' $(readlink -f $(which hcitool))
```

## Installation

You can install this component with [HACS](https://github.com/hacs/integration). Add `https://github.com/ec-blaster/magicswitchbot-homeassistant` as an integration "custom repository" and install it.

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

To use the component, you must define a switch with platform `magicswitchbot` for each device you want to connect:

```yaml
# Example configuration.yaml entries
switch:
  - platform: magicswitchbot
    name: "Magic 1"
    mac: "00:11:22:33:44:55"
    device_id: 1

  - platform: magicswitchbot
    name: "Magic 2"
    mac: "aa:bb:cc:dd:ee:ff"
    device_id: 1
    
    ...
```

### Configuration Variables

**`mac`** string (Required)

The bluetooth MAC address of the Magic Switchbot device. You can get the MAC just using the [official app](https://play.google.com/store/apps/details?id=com.runChina.moLiKaiGuan&hl=es&gl=US) and scanning for the device.

**`device_id`** number (Optional, default: 0)

This is the device number of the bluetooth controller. Usually, you'll have only a bluetooth controller, whose id would be `hci0`, so that you don't need to specify this variable. If you have more than one controller, you can look for its id typing:

```bash
$ sudo hciconfig
```

Then you get the list of bluetooth controllers present in your system:

```bash
hci1:   Type: Primary  Bus: UART
        BD Address: AA:AA:AA:AA:AA:AA  ACL MTU: 1021:8  SCO MTU: 64:1
        UP RUNNING 
        RX bytes:623829 acl:22548 sco:0 events:2557 errors:0
        TX bytes:64463 acl:2186 sco:0 commands:289 errors:0

hci0:   Type: Primary  Bus: SDIO
        BD Address: 00:00:00:00:00:00  ACL MTU: 0:0  SCO MTU: 0:0
        DOWN 
        RX bytes:0 acl:0 sco:0 events:0 errors:0
        TX bytes:0 acl:0 sco:0 commands:0 errors:0
```

If you are using the device `hci1`, you must specify `device_id: 1` in your `configuration.yaml`.

**`password`** string (Optional, default: empty)

This is the password you use to connect to the Magic Switchbot. You can set it with the [official app](https://play.google.com/store/apps/details?id=com.runChina.moLiKaiGuan&hl=es&gl=US), and it's empty by default.

## Services

With the default configuration, you can use the Magic Switchbot as a switch, with states "On" and "Off". You must use an add-on that is shipped with the device and is sticked over the real switch you want to activate or deactivate, it works like a "hook" that pulls the switch when its state changes to "Off".

But the Magic Switchbot has another mode that just "pushes" a button and retracts a little after that. To use this characteristic (that has no On-Off states), the component provides a service whose name is `push` that you can use in your automations or from your lovelace cards.

### Service parameters

The service has an only parameter:

**`entity_id`** string (Required)

The entity id of the switch you previously configured.

### Service call examples

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
      - service: magicswitchbot.push
        service_data:
          entity_id: switch.magic_1
      
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
      service: magicswitchbot.push
      service_data:
        entity_id: switch.magic_1
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
      service: magicswitchbot.push
      service_data:
        entity_id: switch.magic_2
    action_name: Push

```

If you like my work, it is useful to you and you want to, you can buy me a coffee. Thanks.

<a href="https://www.buymeacoffee.com/ecblaster" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

