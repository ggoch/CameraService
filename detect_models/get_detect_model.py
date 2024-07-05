from detect_models.predict_base import ModelDetect
from detect_models.predict_thing import PredictThing


MODELS = {
    'PredictThing': PredictThing,
}

def get_model(model_name) -> ModelDetect:
    model_cls = MODELS.get(model_name)
    if not model_cls:
        raise ValueError(f"Model {model_name} not found")
    return model_cls()