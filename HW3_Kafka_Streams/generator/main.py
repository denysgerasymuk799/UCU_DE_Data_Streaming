import json
import time
import logging
import pandas as pd
from kafka import KafkaProducer

from config import *


logging.basicConfig(level=logging.INFO)


def on_send_error(exc_info):
    print(f'ERROR Producer: Got errback -- {exc_info}')


class KafkaDataProducer:
    def __init__(self, bootstrap_servers):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            api_version=(0, 10, 1),
            acks='all',
            retries=3,
            max_in_flight_requests_per_connection=1,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )

    def send_data(self, topic_name, df):
        for index, row in df.iterrows():
            message = {
                'order': row['order'],
                'id': row['id'],
                'date': row['date'],
                'time': row['time'],
                'url': row['url'],
                'visitCount': row['visitCount'],
                'typedCount': row['typedCount'],
                'transition': row['transition'],
            }
            self.producer.send(topic_name, value=message).add_errback(on_send_error)
            self.producer.flush()
            logging.info(f'Sent record #{index + 1} to Kafka')

            # Periodically add messages to a topic to check statistics
            if (index + 1) % 200 == 0:
                time.sleep(5)


if __name__ == "__main__":
    # Read the dataset
    history_df = pd.read_csv(DATASET_LOCATION)
    # Partition it on messages and send to a topic
    data_producer = KafkaDataProducer(KAFKA_SERVER)
    data_producer.send_data(TOPIC_NAME, history_df)
