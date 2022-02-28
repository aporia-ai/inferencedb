<p align="center"><img src="docs/logo.svg" width="450" /></p>

InferenceDB is a Cloud Native service to **stream ML Model inputs and outputs to any database**, based on [Apache Kafka](https://kafka.apache.org/).

---

### Features

* **Scalable** - Built on top of [Faust](https://faust.readthedocs.io/en/latest/)
* **Extensible** - Add your own model serving framework or database destination

### Installation

    helm install inferencedb ./charts/inferencedb \
      -n inferencedb --create-namespace \
      --set kafka.broker=kafka://kafka:9092 \
      --set kafka.schemaRegistryUrl=http://schema-registry:8081 \
      --set kafka.connectUrl=http://kafka-connect:8083
      
### Why?

from various model serving tools to S3 and other databases, based on Apache Kafka.
