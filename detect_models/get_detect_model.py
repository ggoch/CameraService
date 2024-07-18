from detect_models.predict_thing import PredictThing
from detect_models.predict_car_no import PredictCarNo


MODELS = {
    'PredictThing': PredictThing,
    'PredictCarNo': PredictCarNo
}

def get_model(model_name):
    model_cls = MODELS.get(model_name)
    if not model_cls:
        raise ValueError(f"Model {model_name} not found")
    return model_cls()