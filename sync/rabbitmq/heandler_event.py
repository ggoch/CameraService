from works.rabbitmq_channel import get_rabbitmq_channel
import json
from sync.manager.thing_predict_log import ThingPredictLogManager
from sync.manager.car_no_predict_log import CarNoPredictLogManager

thingPredictLogManager = ThingPredictLogManager()
carNoPredictLogManager = CarNoPredictLogManager()

def create_thing_predict_log(ch, method, properties, body):
    try:
        event_data = json.loads(body)
        occur_time = event_data.get('occur_time')
        line_name = event_data.get('line_name')
        camera_name = event_data.get('camera_name')
        no = event_data.get('no')
        position = event_data.get('position')
        thing_data = event_data.get('thing_data')

        thingPredictLogManager.create(
            occur_time = occur_time,
            thing_data = thing_data,
            position = position,
            lane_name = line_name,
            camera_name = camera_name,
            no = no
            )
    except Exception as e:
        print(f"Failed to process message: {e}")

def create_car_no_predict_log(ch, method, properties, body):
    try:
        event_data = json.loads(body)
        occur_time = event_data.get('occur_time')
        line_name = event_data.get('line_name')
        camera_name = event_data.get('camera_name')
        no = event_data.get('no')
        position = event_data.get('position')
        car_no = event_data.get('car_no')

        carNoPredictLogManager.create(
            occur_time = occur_time,
            car_no = car_no,
            position = "車牌" if position is None else "前" if position == "1" else "後",
            lane_name = line_name,
            camera_name = camera_name,
            no = no
            )
    except Exception as e:
        print(f"Failed to process message: {e}")

def start_consuming(queue_name, callback):
    channel = get_rabbitmq_channel()

    # 设置消费回调函数
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback,
        auto_ack=True
    )

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()