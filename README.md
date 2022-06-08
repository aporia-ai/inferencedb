<p align="center">
    <img src="logo.svg" width="400" />
</p>

---

**InferenceDB** makes it easy to stream inferences of real-time ML models in production to a data lake, based on Kafka.

This data is important for retraining purposes, data drift monitoring, performance degradation detection, AI incident investigation and more.

### Quickstart

* [Flask](https://github.com/aporia-ai/inferencedb/wiki/Flask-Quickstart) 
* [FastAPI](https://github.com/aporia-ai/inferencedb/wiki/FastAPI-Quickstart) 
* [KServe](https://github.com/aporia-ai/inferencedb/wiki/KServe-Quickstart) 


### Features

* **Cloud Native** - Runs on top of Kubernetes and supports any cloud infrastructure
* **Model Serving Integrations** - Connects to ML model serving tools like [KServe](https://kserve.github.io/website/)
* **Extensible** - Add your own model serving frameworks and database destinations
* **Horizontally Scalable** - Add more workers to support more models and more traffic 
* **Python Ecosystem** - Written in Python using [Faust](https://faust.readthedocs.io/en/latest/), so you can add your own data transformations using Numpy, Pandas, etc.

<p align="center">Made with :heart: by <a href="https://www.aporia.com?utm_source=github&utm_medium=github&utm_campaign=inferencedb" target="_blank">Aporia</a></p>

**WARNING:** InferenceDB is still experimental, use at your own risk! 💀

## Installation

The only requirement to InferenceDB is a Kafka cluster, with [Schema Registry](https://docs.confluent.io/platform/current/schema-registry/index.html) and [Kafka Connect](https://docs.confluent.io/platform/current/connect/index.html).

To install InferenceDB using Helm, run:

```sh
helm install inferencedb inferencedb/inferencedb -n inferencedb --create-namespace \
  --set kafka.broker=kafka:9092 \
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
      awsRegion: us-east-2
```

This InferenceLogger will watch the `my-model` Kafka topic for events in KServe format, and log them to a Parquet file on S3. See the [KServe quickstart guide](https://github.com/aporia-ai/inferencedb/wiki/KServe-Quickstart) for more details.

## Development

InferenceDB dev is done using [Skaffold](https://skaffold.dev/).

Make sure you have a Kubernetes cluster with Kafka installed (can be local or remote), and edit [skaffold.yaml](skaffold.yaml) with the correct Kafka URLs and Docker image registry (for local, just use `local/inferencedb`).

To start development, run:

    skaffold dev --trigger=manual
    
This will build the Docker image, push it to the Docker registry you provided, and install the Helm chart on the cluster. Now, you can make changes to the code, click "Enter" on the Skaffold CLI and that would update the cluster.

## Roadmap

### Core

* [ ] Add support for Spark Streaming in addition to Faust
* [ ] Add more input validations on the Kafka URLs

### Event Processors 

* [x] JSON
* [x] KServe
* [ ] Seldon Core
* [ ] BentoML
* [ ] MLFlow Deployments

### Destinations

* [x] Parquet on S3
* [ ] HDF5 on S3
* [ ] Azure Blob Storage
* [ ] Google Cloud Storage
* [ ] ADLS Gen2
* [ ] AWS Glue
* [ ] Delta Lake
* [ ] PostgreSQL
* [ ] Snowflake
* [ ] Iceberg

### Documentation

* [ ] How to set up Kafka using AWS / Azure / GCP managed services
* [ ] API Reference for the CRDs
