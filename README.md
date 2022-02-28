<p align="center">
    <img src="docs/logo.svg" width="450" />
    
</p>
<p align="center"><b>Stream ML model inputs and outputs to any data storage</b>, based on <a href="https://kafka.apache.org">Apache Kafka</a>.</p>

---

### Features

* **Cloud Native** - Runs on top of Kubernetes and supports any cloud infrastructure
* **Model Serving Integrations** - Connect to existing model serving tools such as [KServe](https://kserve.github.io/website/), [Seldon Core](https://github.com/SeldonIO/seldon-core), and others
* **Extensible** - Add your own model serving frameworks, database destinations
* **Horizontally Scalable** - Add more workers to support more models & traffic 
* **Python Ecosystem** - Written in Python using [Faust](https://faust.readthedocs.io/en/latest/), so you can add your own data transformation using Numpy, Pandas, etc.

<p align="center">Made with :heart: by <a href="https://www.aporia.com?utm_source=github&utm_medium=github&utm_campaign=mlnotify" target="_blank">Aporia</a></p>


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
