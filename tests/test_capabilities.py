from mock import patch

from capabilities import CapabilityOnOff, CapabilityRange, CapabilityToggle, CapabilityMode, reverse_dict


def test_capability_on_off(device):
    capability = CapabilityOnOff()
    assert capability.as_dict() == {"type": "devices.capabilities.on_off"}
    device.on = True
    assert capability.get_state(device) == {"instance": "on", "value": True}
    assert capability.as_dict(device) == {"state": {"instance": "on", "value": True},
                                          "type": "devices.capabilities.on_off"}
    change_state_data_to_off = {"type": "devices.capabilities.on_off",
                                "state": {"instance": "on", "value": False}}
    success_result = {
        "type": "devices.capabilities.on_off",
        "state": {
            "instance": "on",
            "action_result": {
                "status": "DONE"
            }
        }
    }
    assert capability.change_device_state(device, change_state_data_to_off) == success_result
    assert device.on is False
    assert capability.get_state(device) == {"instance": "on", "value": False}

    change_state_data_to_on = {"type": "devices.capabilities.on_off",
                               "state": {"instance": "on", "value": True}}

    assert capability.change_device_state(device, change_state_data_to_on) == success_result
    assert capability.get_state(device) == {"instance": "on", "value": True}
    assert device.on is True


def test_capability_range(device):
    capability = CapabilityRange()
    capability_type = "devices.capabilities.range"
    expected_params = {
        "parameters": {
            "instance": "volume",
            "random_access": True,
            "range": {
                "min": -80,
                "max": 16,
                "precision": 1},
        }
    }
    assert capability.get_params() == expected_params
    assert capability.as_dict() == {"type": capability_type, **expected_params}
    device.volume = -50
    assert capability.get_state(device) == {"instance": "volume", "value": -50}
    assert capability.as_dict(device) == {"state": {"instance": "volume", "value": -50},
                                          "type": capability_type}
    new_volume = -30
    change_volume_data = {"type": "devices.capabilities.range",
                          "state": {"instance": "volume", "value": -30}}
    success_result = {
        "type": capability_type,
        "state": {
            "instance": "volume",
            "action_result": {
                "status": "DONE"
            }
        }
    }

    assert capability.change_device_state(device, change_volume_data) == success_result
    assert device.volume == new_volume
    assert capability.get_state(device) == {"instance": "volume", "value": new_volume}


def test_capability_toggle(device):
    capability = CapabilityToggle()
    capability_type = "devices.capabilities.toggle"
    expected_params = {
        "parameters": {
            "instance": "mute"
        }
    }
    assert capability.get_params() == expected_params
    assert capability.as_dict() == {"type": capability_type, **expected_params}
    assert capability.get_state(device) == {"instance": "mute", "value": False}
    assert capability.as_dict(device) == {"state": {"instance": "mute", "value": False},
                                          "type": capability_type}
    change_volume_data = {"type": capability_type,
                          "state": {"instance": "mute", "value": True}}
    success_result = {
        "type": capability_type,
        "state": {
            "instance": "mute",
            "action_result": {
                "status": "DONE"
            }
        }
    }

    assert capability.change_device_state(device, change_volume_data) == success_result
    assert device.mute is True
    assert capability.get_state(device) == {"instance": "mute", "value": True}


@patch('config.YAMAHA_INPUT_MAP', {"one": "HDMI1", "two": "AV1"})
def test_capability_mode(device):
    capability = CapabilityMode()
    capability_type = "devices.capabilities.mode"
    expected_params = {
        "parameters": {
            "instance": "input_source",
            "modes": [{"value": "one"}, {"value": "two"}],
        }
    }
    assert capability.get_params() == expected_params
    assert capability.as_dict() == {"type": capability_type, **expected_params}
    assert capability.get_state(device) == {"instance": "input_source", "value": "one"}
    assert capability.as_dict(device) == {"state": {"instance": "input_source", "value": "one"},
                                          "type": capability_type}
    change_source_data = {"type": capability_type,
                          "state": {"instance": "input_source", "value": "two"}}
    success_result = {
        "type": capability_type,
        "state": {
            "instance": "input_source",
            "action_result": {
                "status": "DONE"
            }
        }
    }

    assert capability.change_device_state(device, change_source_data) == success_result
    assert device.input == 'AV1'
    assert capability.get_state(device) == {"instance": "input_source", "value": "two"}
