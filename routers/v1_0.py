from uuid import uuid4

import rxv
from fastapi import Depends, Body, APIRouter

from auth import User, get_user
from capabilities import (
    get_all_capabilities,
    get_capabilities_with_state,
    get_capability_by_name,
)

router = APIRouter()


@router.get("/user/devices")
async def devices(user: User = Depends(get_user)):
    response_data = {
        "request_id": uuid4(),
        "payload": {"user_id": user.id, "devices": []},
    }
    for device in rxv.find():
        response_data["payload"]["devices"].append(
            {
                "id": device.ctrl_url,
                "name": "{} {}".format(device.friendly_name, device.model_name),
                "description": "AV Receiver",
                "room": "",
                "type": "devices.types.media_device",
                "custom_data": {"base_url": device.ctrl_url},
                "capabilities": get_all_capabilities(),
                "device_info": {
                    "manufacturer": "Yamaha Corporation",
                    "model": device.model_name,
                },
            }
        )
    return response_data


@router.post("/user/devices/query")
async def query(user: User = Depends(get_user)):
    response_data = {
        "request_id": uuid4(),
        "payload": {"user_id": str(user.id), "devices": []},
    }
    for device in rxv.find():
        response_data["payload"]["devices"].append(
            {"id": device.ctrl_url, "capabilities": get_capabilities_with_state(device)}
        )
    return response_data


@router.post("/user/devices/action")
async def action(user: User = Depends(get_user), body=Body(None)):
    data = body
    response_data = {
        "request_id": uuid4(),
        "payload": {"user_id": user.id, "devices": []},
    }
    for device in data["payload"]["devices"]:
        rx_device = rxv.RXV(device["id"])
        response_device = {"id": device["id"], "capabilities": []}
        for capability in device["capabilities"]:
            capability_instance = get_capability_by_name(capability["type"])
            response_device["capabilities"].append(
                capability_instance.change_device_state(rx_device, capability)
            )
        response_data["payload"]["devices"].append(response_device)
    return response_data
