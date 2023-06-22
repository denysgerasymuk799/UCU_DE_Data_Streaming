import json
import faust
import logging

from config import *


logging.basicConfig(level=logging.INFO)


# Initialize Faust app along with Kafka topic objects.
app = faust.App('statistics-aggregator',
                broker=KAFKA_BROKER,
                value_deserializer=lambda x: json.loads(x).encode('utf-8'),
                web_host=FAUST_HOST,
                web_port=FAUST_PORT)
root_domain_visits_topic = app.topic(ROOT_DOMAIN_VISITS_TOPIC, partitions=3)
root_domain_visits_table = app.Table("visits-count", key_type=str, value_type=int, partitions=3, default=int)


def get_top_rows(table, top_n: int):
    top_n_vals = []
    # Note that table.items() uses buffer to get all records from the RocksDB table.
    # So it does not cause memory overflow.
    for k, v in table.items():
        if len(top_n_vals) < top_n:
            top_n_vals.append((k, v))
            if len(top_n_vals) == top_n:
                top_n_vals = sorted(top_n_vals, key=lambda x: x[1], reverse=True)
        else:
            if v > top_n_vals[-1][1]:
                top_n_vals[-1] = (k, v)
                top_n_vals = sorted(top_n_vals, key=lambda x: x[1], reverse=True)

    return top_n_vals


@app.timer(interval=5.0)
async def print_stats_periodically():
    top_n_vals = get_top_rows(root_domain_visits_table, top_n=5)
    final_str = ''
    for keyword, num_occurrences in top_n_vals:
        final_str += f'{keyword}: {num_occurrences}\n'
    final_str += '\n\n\n'
    logging.info(f"\n{'=' * 20} Top 5 root domains {'=' * 20}\n"
                 f"{final_str}")


@app.agent(root_domain_visits_topic)
async def process_visits(records):
    async for message in records:
        url = message['url']
        if url[:4] != 'http':
            continue

        root_domain = url.split('/')[2].split('.')[-1]
        root_domain_visits_table[root_domain] += 1
