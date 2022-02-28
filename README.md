<p align="center"><img src="docs/logo.svg" width="450" /></p>

Stream ML model inputs and outputs to any data storage, based on [Apache Kafka](https://kafka.apache.org/).

### Features

* **Cloud Native** - Runs on top of Kubernetes and supports any cloud infrastructure
* **Model Serving Integrations** - Connect to existing model serving tools such as [KServe](https://kserve.github.io/website/), [Seldon Core](https://github.com/SeldonIO/seldon-core), and others
* **Extensible** - Add your own model serving frameworks, database destinations
* **Horizontally Scalable** - Add more workers to support more models & traffic 
* **Python Ecosystem** - Written in Python using [Faust](https://faust.readthedocs.io/en/latest/), so you can add your own data transformation using Numpy, Pandas, etc.

### Quickstart

To install InferenceDB, run:

    helm install inferencedb ./charts/inferencedb \
      -n inferencedb --create-namespace \
      --set kafka.broker=kafka://kafka:9092 \
      --set kafka.schemaRegistryUrl=http://schema-registry:8081 \
      --set kafka.connectUrl=http://kafka-connect:8083

Next, create a file called inferencelogger.yaml and copy-paste:


### Why?

from various model serving tools to S3 and other databases, based on Apache Kafka.
