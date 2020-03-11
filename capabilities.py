from copy import deepcopy
from typing import List

from rxv import RXV

import config
from exceptions import ActionError


class Capability:
    """Базовый класс для описания возможностей устройства.
     К примеру, возможность переключения источника сигнала или увеличение громкости"""

    name: str

    def get_state(self, device: RXV) -> dict:
        """Текущее состояние устройства применительно к данной возможности"""
        return {}

    def get_params(self) -> dict:
        """Параметры, необходимые Алисе для корректной работы возможности. Формируются в соответствии с требованиями
         по разработке навыков для Алисы."""
        return {}

    def get_common_info(self) -> dict:
        return {"type": self.name}

    def as_dict(self, device: RXV = None) -> dict:
        data = self.get_common_info()
        if device:
            data.update({"state": self.get_state(device=device)})
        else:
            data.update(self.get_params())
        return data

    def _run_rx_device_action(self, device: RXV, data: dict):
        """Изменение состояния устройства в соответствии с параметрами, полученными от Алисы."""
        pass

    def get_action_success_response(self, data: dict) -> dict:
        """Формирование ответа в случае успешного изменения состояния устройства."""
        response = deepcopy(data)
        response["state"].pop("value")
        response["state"]["action_result"] = {"status": "DONE"}
        return response

    def get_action_error_response(self, data: dict, error_message: str = None) -> dict:
        """Формирование ответа при возникновении ошибки при изменении состояния устройства."""
        response = deepcopy(data)
        response["state"].pop("value")
        response["state"]["action_result"] = {
            "status": "ERROR",
            "error_code": "INVALID_ACTION",
            "error_message": error_message,
        }
        return response

    def change_device_state(self, device: RXV, data: dict) -> dict:
        try:
            self._run_rx_device_action(device, data)
        except ActionError as e:
            return self.get_action_error_response(data, error_message=str(e))
        else:
            return self.get_action_success_response(data)


class CapabilityOnOff(Capability):

    name = "devices.capabilities.on_off"

    def get_state(self, device: RXV = None) -> dict:
        return {"instance": "on", "value": device.basic_status.on == "On"}

    def _run_rx_device_action(self, device: RXV, data: dict):
        device.on = data["state"]["value"]


class CapabilityRange(Capability):

    name = "devices.capabilities.range"

    def get_params(self) -> dict:
        return {
            "parameters": {
                "instance": "volume",
                "random_access": True,
                "range": {
                    "min": config.VOLUME_LIMIT["min"],
                    "max": config.VOLUME_LIMIT["max"],
                    "precision": 1},
            }
        }

    def get_state(self, device: RXV) -> dict:
        return {"instance": "volume", "value": device.volume}

    def _run_rx_device_action(self, device: RXV, data: dict):
        device.volume = data["state"]["value"]


class CapabilityToggle(Capability):

    name = "devices.capabilities.toggle"

    def get_params(self) -> dict:
        return {"parameters": {"instance": "mute"}}

    def get_state(self, device: RXV) -> dict:
        return {"instance": "mute", "value": device.mute}

    def _run_rx_device_action(self, device: RXV, data: dict):
        device.mute = data["state"]["value"]


class CapabilityMode(Capability):

    name = "devices.capabilities.mode"

    def get_params(self) -> dict:
        return {
            "parameters": {
                "instance": "input_source",
                "modes": [{"value": i} for i in config.YAMAHA_INPUT_MAP.keys()],
            }
        }

    def get_state(self, device: RXV) -> dict:
        return {
            "instance": "input_source",
            "value": reverse_dict(config.YAMAHA_INPUT_MAP).get(device.input),
        }

    def _run_rx_device_action(self, device: RXV, data: dict):
        if data["state"]["value"] not in config.YAMAHA_INPUT_MAP:
            raise ActionError(
                f'Источник {data["state"]["value"]} не сконфигурирован, проверьте настройки.'
            )
        if data["state"]["instance"] == "input_source":
            device.input = config.YAMAHA_INPUT_MAP[data["state"]["value"]]
        else:
            raise ActionError("Некорректный запрос")


def reverse_dict(d):
    return dict([(v, k) for k, v in d.items()])


def get_capability_by_name(name):
    for cls in Capability.__subclasses__():
        if cls.name == name:
            return cls()


def get_capabilities_with_state(device: RXV) -> List[dict]:
    return [c().as_dict(device) for c in Capability.__subclasses__()]


def get_all_capabilities() -> List[dict]:
    return [c().as_dict() for c in Capability.__subclasses__()]
