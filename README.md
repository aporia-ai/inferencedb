# InferenceDB

*Assuming a clean Kubernetes*

Install KServe using their quickstart (includes KServe, Istio, KNative): 

```
curl -s "https://raw.githubusercontent.com/kserve/kserve/release-0.7/hack/quick_install.sh" | bash
```

Install KNative Eventing

```
kubectl apply -f https://github.com/knative/eventing/releases/download/knative-v1.2.0/eventing-crds.yaml
kubectl apply -f https://github.com/knative/eventing/releases/download/knative-v1.2.0/eventing-core.yaml
```

Install Kafka Broker

```
kubectl apply -f https://github.com/knative-sandbox/eventing-kafka-broker/releases/download/knative-v1.2.1/eventing-kafka-controller.yaml
kubectl apply -f https://github.com/knative-sandbox/eventing-kafka-broker/releases/download/knative-v1.2.1/eventing-kafka-broker.yaml
kubectl apply -f https://github.com/knative-sandbox/eventing-kafka-broker/releases/download/knative-v1.2.1/eventing-kafka-sink.yaml
```

Prepare Helm chart values for Kafka

```
cp-kafka:
  persistence:
    enabled: true
    # storageClass: ""
    size: 256Gi
    disksPerBroker: 1

cp-kafka-connect:
  image: aporiadocker/kafka-connect-s3
  imageTag: latest

  customEnv:
    AWS_ACCESS_KEY_ID: <LESS_SECRET!>
    AWS_SECRET_ACCESS_KEY: <SECRET!>
    AWS_DEFAULT_REGION: <REGION>
```

This is the Dockerfile for aporiadocker/kafka-connect-s3:

```
FROM confluentinc/cp-kafka-connect-base:7.0.1
RUN confluent-hub install --no-prompt confluentinc/kafka-connect-s3:latest
```

Install Kafka + Kafka UI

```
helm install kafka confluentinc/cp-helm-charts -f cp-values.yaml
helm install kafka-ui kafka-ui/kafka-ui --set envs.config.KAFKA_CLUSTERS_0_NAME=kafka --set envs.config.KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS=kafka-cp-kafka:9092 
```

Run [examples/my-model](examples/my-model) using KServe, and create a Kafka broker:

```
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: my-model
  namespace: default
spec:
  predictor:
    logger:
      mode: all
      url: http://kafka-broker-ingress.knative-eventing.svc.cluster.local/default/my-model-kafka-broker
    containers:
      - name: my-model
        image: aporiadocker/my-model
        env:
          - name: PROTOCOL
            value: v2
        ports:
          - containerPort: 9081
            protocol: TCP
---
apiVersion: eventing.knative.dev/v1
kind: Broker
metadata:
  name: my-model-kafka-broker
  namespace: default
  annotations:
    eventing.knative.dev/broker.class: Kafka
spec:
  config:
    apiVersion: v1
    kind: ConfigMap
    name: kafka-broker-config
    namespace: knative-eventing
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: kafka-broker-config
  namespace: knative-eventing
data:
  # Number of topic partitions
  default.topic.partitions: "10"
  # Replication factor of topic messages.
  default.topic.replication.factor: "1"
  # A comma separated list of bootstrap servers. (It can be in or out the k8s cluster)
  bootstrap.servers: "kafka-cp-kafka.default.svc.cluster.local:9092"
```


Now, you can port forward:

```
kubectl port-forward --namespace istio-system svc/istio-ingressgateway 8080:80
kubectl port-forward svc/kafka-ui 8081:80  # Optional
```

And send a prediction request:

```
http://localhost:8080/v2/models/my-model/infer
{
  "inputs": [
    {
      "name": "sepal.length",
      "shape": [],
      "datatype": "FP32",
      "data":  [0.2, 1, 0.2]
    },
    {
      "name": "sepal.width",
      "shape": [],
      "datatype": "FP32",
      "data":  [0.3, 2, 0.3]
    },
    {
      "name": "petal.length",
      "shape": [],
      "datatype": "FP32",
      "data":  [0.25, 3, 0.25]
    },
    {
      "name": "petal.width",
      "shape": [],
      "datatype": "FP32",
      "data":  [0.26, 4, 0.26]
    }
  ]
}
```

Do this multiple times and you should see it in the S3 bucket.

**Not working?**
 * Open Kafka UI, search for "my-model", go to the broker and make sure you see messages.
   If not - there's a problem with the Kafka broker configuration above! Not related to InferenceDB.

 * Open Kafka UI, search for "avro", make sure you see messages.
   If not - this is a problem with InferenceDB, check for errors in our pod.

 * Logs on Kafka Connect - there might be an issue with the S3 sink.


**TODO:**
 * Fix all the TODOs in the code.
 * Add support for Kubernetes CRDs
 * Consider adding support for an endpoint to publish messages to the topic instead KNative Eventing, brokers, etc?
 * Performance test (see KServe quickstart, they have automatic stress test)
 * For OSS: Seldon Core, FastAPI support
 * Remove "core" package"
 * Docs, CI/CD, GitHub container registry (for my-model and kafka s3 connector as well!), etc.