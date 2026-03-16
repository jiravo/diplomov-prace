import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
import matplotlib.pyplot as plt

# ===============================
# LOAD DATA
# ===============================

df = pd.read_csv("data/ML/Predictive_Dataset.csv", parse_dates=["timestamp"])

# ===============================
# BASIC CLEAN
# ===============================

df = df.dropna()

# ===============================
# FEATURES / TARGET
# ===============================

target = "target_failure_72h"

features = [
    "temperature",
    "vibration",
    "pressure",
    "load",
    "ambient_temperature",
    "operating_hours_since_maintenance",
    "machine_age_hours",
    "health_index",
    "health_delta_24h",
    "rolling_temp_mean_24h",
    "rolling_temp_std_24h",
    "rolling_vibration_mean_24h",
    "rolling_vibration_std_24h",
    "rolling_pressure_mean_24h",
    "rolling_pressure_std_24h",
    "running_ratio_24h",
    "hours_since_last_failure",
    "failure_count_last_7d",
    "failure_count_last_30d",
]

X = df[features]
y = df[target]

# ===============================
# TRAIN TEST SPLIT
# ===============================

df = df.sort_values("timestamp")

split_time = df["timestamp"].quantile(0.8)

train = df[df["timestamp"] < split_time]
test = df[df["timestamp"] >= split_time]

X_train = train[features]
y_train = train[target]

X_test = test[features]
y_test = test[target]

# ===============================
# MODEL
# ===============================

model = RandomForestClassifier(
    n_estimators=200, max_depth=12, n_jobs=-1, random_state=42
)

model.fit(X_train, y_train)

# ===============================
# PREDICTIONS
# ===============================

pred = model.predict(X_test)
proba = model.predict_proba(X_test)[:, 1]

# ===============================
# METRICS
# ===============================

print("\nClassification report:")
print(classification_report(y_test, pred))

roc = roc_auc_score(y_test, proba)
print("\nROC AUC:", roc)

# ===============================
# FEATURE IMPORTANCE
# ===============================

importances = pd.Series(model.feature_importances_, index=features)
importances = importances.sort_values(ascending=False)

print("\nFeature importance:")
print(importances)

# ===============================
# PLOT
# ===============================

plt.figure(figsize=(8, 5))
importances.head(10).plot(kind="bar")
plt.title("Top 10 Feature Importances")
plt.show()

print(
    "DRUHÝ MODEL!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
)

######################################################################################################################################################################################
# DRUHÝ MODEL BEZ URČITÝCH FEATURES
# ===============================
# LOAD DATA
# ===============================

df = pd.read_csv("data/ML/Predictive_Dataset.csv", parse_dates=["timestamp"])

# ===============================
# BASIC CLEAN
# ===============================

df = df.dropna()

# ===============================
# FEATURES / TARGET
# ===============================

target = "target_failure_72h"

features = [
    "temperature",
    "vibration",
    "pressure",
    "load",
    "ambient_temperature",
    "operating_hours_since_maintenance",
    "machine_age_hours",
    "health_index",
    "health_delta_24h",
    "rolling_temp_mean_24h",
    "rolling_temp_std_24h",
    "rolling_vibration_mean_24h",
    "rolling_vibration_std_24h",
    "rolling_pressure_mean_24h",
    "rolling_pressure_std_24h",
    "running_ratio_24h",
    "hours_since_last_failure",
    "failure_count_last_7d",
    "failure_count_last_30d",
]

features.remove("health_index")
features.remove("machine_age_hours")

X = df[features]
y = df[target]

# ===============================
# TRAIN TEST SPLIT
# ===============================

df = df.sort_values("timestamp")

split_time = df["timestamp"].quantile(0.8)

train = df[df["timestamp"] < split_time]
test = df[df["timestamp"] >= split_time]

X_train = train[features]
y_train = train[target]

X_test = test[features]
y_test = test[target]

# ===============================
# MODEL
# ===============================

model = RandomForestClassifier(
    n_estimators=200, max_depth=12, n_jobs=-1, random_state=42
)

model.fit(X_train, y_train)

# ===============================
# PREDICTIONS
# ===============================

pred = model.predict(X_test)
proba = model.predict_proba(X_test)[:, 1]

# ===============================
# METRICS
# ===============================

print("\nClassification report:")
print(classification_report(y_test, pred))

roc = roc_auc_score(y_test, proba)
print("\nROC AUC:", roc)

# ===============================
# FEATURE IMPORTANCE
# ===============================

importances = pd.Series(model.feature_importances_, index=features)
importances = importances.sort_values(ascending=False)

print("\nFeature importance:")
print(importances)

# ===============================
# PLOT
# ===============================

plt.figure(figsize=(8, 5))
importances.head(10).plot(kind="bar")
plt.title("Top 10 Feature Importances")
plt.show()
