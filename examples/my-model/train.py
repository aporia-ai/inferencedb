from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, log_loss
import pandas as pd
import lightgbm as lgb
import joblib

# Prepare training data
df = pd.read_csv('iris.csv')
flower_names = {'Setosa': 0, 'Versicolor': 1, 'Virginica': 2}


X = df[['sepal.length', 'sepal.width', 'petal.length', 'petal.width']]
y = df['variety'].map(flower_names)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

train_data = lgb.Dataset(X_train, label=y_train)

def main():
    # Train model
    params = {
      "objective": "multiclass",
      "num_class": 3, 
      "learning_rate": 0.2,
      "metric": "multi_logloss",
      "feature_fraction": 0.8,
      "bagging_fraction": 0.9,
      "seed": 42,
    }
    
    model = lgb.train(params, train_data, valid_sets=[train_data])
    joblib.dump(model, "my-model.lgb")


if __name__ == "__main__":
    main()
