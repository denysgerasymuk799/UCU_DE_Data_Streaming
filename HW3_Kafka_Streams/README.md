# HW 3. Kafka Streams

## How to run it?

Execute the following command in the root of the project:
```shell
./UCU_DE_Data_Streaming/HW3_Kafka_Streams$ docker-compose up --build
```

## Notes

* Note that there is no framework in Python that supports Kafka Streams aggregations. Therefore, to get top 5 root domains, statistics-aggregator finds top 5 records with the greatest numbers of occurrences each time.
For that it reads all records from the RocksDB table using the Faust table feature -- `table.items()`. 
If we look at [the source code](https://github.com/robinhood/faust/blob/master/faust/stores/rocksdb.py#L414) in the Faust repo, we can notice that `table.items()` works as a simple iterator, thus it does not cause any memory overflow.

* Generator service adds 200 messages each 5 seconds to a RootDomainVisitsTopic, while statistics-aggregator recomputes statistics also each 5 seconds and prints it to the terminal.
You can find sample screenshots below:

Log with statistics 1:

![stats-log1](https://github.com/denysgerasymuk799/UCU_DE_Data_Streaming/assets/42843889/398fb614-c8be-4977-9182-76e722ee4cc4)

Log with statistics 2:

![stats-log2](https://github.com/denysgerasymuk799/UCU_DE_Data_Streaming/assets/42843889/a5f29a6f-82a5-406d-837d-24e2746e4662)

Log with statistics 3:

![stats-log3](https://github.com/denysgerasymuk799/UCU_DE_Data_Streaming/assets/42843889/d7466d5e-8442-4715-ab2d-741a84c1b0a5)
