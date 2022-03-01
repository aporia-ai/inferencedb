<p align="center">
    <img src="docs/logo.svg" width="450" />
    
</p>
<p align="center"><b>🔥 Stream ML model inferences to any data storage</b>, based on <a href="https://kafka.apache.org">Apache Kafka</a>.</p>

---

InferenceDB makes it easy to log ML model inferences (inputs & outputs) to AWS S3, Google Cloud Storage, Azure Blob Storage, and other data storages. 

### Quickstart

* [KServe]() 
* [Seldon Core]()
* [FastAPI]()


### Features

* **Cloud Native** - Runs on top of Kubernetes and supports any cloud infrastructure
* **Model Serving Integrations** - Connects to existing model serving tools like [KServe](https://kserve.github.io/website/) and [Seldon Core](https://github.com/SeldonIO/seldon-core)
* **Extensible** - Add your own model serving frameworks and database destinations
* **Horizontally Scalable** - Add more workers to support more models and more traffic 
* **Python Ecosystem** - Written in Python using [Faust](https://faust.readthedocs.io/en/latest/), so you can add your own data transformations using Numpy, Pandas, etc.


<p align="center">Made with :heart: by <a href="https://www.aporia.com?utm_source=github&utm_medium=github&utm_campaign=inferencedb" target="_blank">Aporia</a></p>


## Installation

The only requirement to InferenceDB is a Kafka cluster, with [Schema Registry](https://docs.confluent.io/platform/current/schema-registry/index.html) and [Kafka Connect](https://docs.confluent.io/platform/current/connect/index.html).

To install InferenceDB using Helm, run:

```sh
helm install inferencedb inferencedb/inferencedb -n inferencedb --create-namespace \
  --set kafka.broker=kafka://kafka:9092 \
  --set kafka.schemaRegistryUrl=http://schema-registry:8081 \
  --set kafka.connectUrl=http://kafka-connect:8083
```

## Usage

To start logging your model inferences, create an **InferenceLogger** Kubernetes resource. This is a [Kubernetes Custom Resource](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/) that is defined and controlled by InferenceDB.

**Example:**

```yaml
apiVersion: inferencedb.aporia.com/v1alpha1
kind: InferenceLogger
metadata:
  name: my-model-inference-logger
  namespace: default
spec:
  topic: my-model
  events:
    type: kserve
    config: {}
  destination:
    type: confluent-s3
    config:
      url: s3://my-bucket/inferencedb
      format: parquet
```

This InferenceLogger will watch the `my-model` Kafka topic for events in KServe format, and log them to a Parquet file on S3. See the [KServe quickstart guide]() for more details.

## Development

InferenceDB dev is done using [Skaffold](https://skaffold.dev/).

Make sure you have a Kubernetes cluster with Kafka installed (can be local or remote), and edit [skaffold.yaml](skaffold.yaml) with the correct Kafka URLs and Docker image registry (for local, just use `local/inferencedb`).

To start development, run:

    skaffold dev --trigger=manual
    
This will build the Docker image, push it to the Docker registry you provided, and install the Helm chart on the cluster. Now, you can make changes to the code, click "Enter" on the Skaffold CLI and that would update the cluster.
