from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

import uuid

class ThingPredictLogBase(BaseModel):
    id:uuid.UUID
    occur_time: datetime
    thing_data: str
    position: str
    lane_name: str
    camera_name: str
    no: str
    create_time: datetime

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "occur_time": "2021-09-06 15:00:00",
                    "thing_data": "E006",
                    "position": "前",
                    "lane_name": "車道1",
                    "camera_name": "攝影機1",
                    "no": "1.1",
                    "create_time": "2021-09-06 15:00:00"
                }
            ]
        }
    }

class ThingPredictLogRead(ThingPredictLogBase):
    pass

class ThingPredictLogCreate():
    occur_time: datetime = Field()
    thing_data: str = Field()
    position: str = Field()
    lane_name: str = Field()
    camera_id: str = Field()
    no: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "occur_time": "2021-09-06 15:00:00",
                    "thing_data": "E006",
                    "position": "前",
                    "lane_name": "車道1",
                    "camera_name": "攝影機1",
                    "no": "1.1",
                }
            ]
        }
    }

class ThingPredictLogCreateResponse(ThingPredictLogBase):
    pass

class ThingPredictLogUpdate(ThingPredictLogCreate):
    pass

class ThingPredictLogUpdateResponse(ThingPredictLogBase):
    pass