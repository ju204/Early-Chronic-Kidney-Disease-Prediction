# -*- coding: utf-8 -*-

Original file is located at
    https://colab.research.google.com/gist/ju204/10d7eda489cb00438817d54b3d29b6b7/ckd_risk_prediction.ipynb

from google.colab import files
uploaded = files.upload()

!pip install pyreadstat -q

import pandas as pd
import pyreadstat
import os

dataframes = {}
for filename in uploaded.keys():
  if filename.endswith('.xpt'):
    try:
      # Try reading with pandas
      df = pd.read_sas(filename)
      dataframes[filename.replace('.xpt', '')] = df
      print(f"Loaded {filename} into a DataFrame named '{filename.replace('.xpt', '')}' using pandas.read_sas")
    except Exception as e:
      print(f"Error loading {filename}: {e}")

# Display the first few rows of each loaded DataFrame
for name, df in dataframes.items():
    print(f"\nDataFrame: {name}")
    display(df.head())

import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer

processed_dataframes = {}

for name, df in dataframes.items():
    print(f"Preprocessing DataFrame: {name}")

    # Make a copy to avoid modifying the original dataframe
    processed_df = df.copy()

    # Define the target variable 'Kidney_Risk' for the KIQ_U_L dataframe before scaling
    if name == 'KIQ_U_L':
        # Handle potential NaN values in KIQ044 before comparison
        processed_df['Kidney_Risk'] = (processed_df['KIQ044'].fillna(0) == 1).astype(int)
        # Drop the original KIQ044, KIQ046, KIQ048 columns from the KIQ_U_L dataframe before scaling
        columns_to_drop = ['KIQ044']
        if 'KIQ046' in processed_df.columns:
            columns_to_drop.append('KIQ046')
        if 'KIQ048' in processed_df.columns:
            columns_to_drop.append('KIQ048')
        processed_df = processed_df.drop(columns=columns_to_drop)


    # Handle missing values
    # Impute numerical columns with the mean
    numerical_cols = processed_df.select_dtypes(include=np.number).columns
    if len(numerical_cols) > 0:
        numerical_imputer = SimpleImputer(strategy='mean')
        # Impute numerical columns individually to avoid issues with columns with all NaNs
        for col in numerical_cols:
             processed_df[col] = numerical_imputer.fit_transform(processed_df[[col]])


    # Impute categorical columns with the most frequent value
    categorical_cols = processed_df.select_dtypes(include='object').columns
    if len(categorical_cols) > 0:
        categorical_imputer = SimpleImputer(strategy='most_frequent')
        processed_df[categorical_cols] = categorical_imputer.fit_transform(processed_df[categorical_cols])


    # Encode categorical variables
    for col in categorical_cols:
        # Convert to string first to handle potential mixed types
        processed_df[col] = processed_df[col].astype(str)
        le = LabelEncoder()
        processed_df[col] = le.fit_transform(processed_df[col])

    # Scale numerical features (excluding the sequence number 'SEQN' and the newly created Kidney_Risk)
    numerical_cols_to_scale = [col for col in numerical_cols if col != 'SEQN' and col != 'Kidney_Risk']
    if len(numerical_cols_to_scale) > 0:
        scaler = StandardScaler()
        processed_df[numerical_cols_to_scale] = scaler.fit_transform(processed_df[numerical_cols_to_scale])

    processed_dataframes[name] = processed_df
    print(f"Finished preprocessing DataFrame: {name}")

# Display the first few rows of each processed DataFrame
for name, df in processed_dataframes.items():
    print(f"\nProcessed DataFrame: {name}")
    display(df.head())

# Display the value counts for Kidney_Risk in the processed KIQ_U_L dataframe
if 'KIQ_U_L' in processed_dataframes:
    print("\nValue counts for the target variable 'Kidney_Risk' in processed KIQ_U_L:")
    display(processed_dataframes['KIQ_U_L']['Kidney_Risk'].value_counts())

# Merge all dataframes in processed_dataframes on 'SEQN'
# Start with the first dataframe
merged_df = list(processed_dataframes.values())[0]

# Iterate through the rest of the dataframes and merge
for name, df in list(processed_dataframes.items())[1:]:
    merged_df = pd.merge(merged_df, df, on='SEQN', how='outer')

print("Merged DataFrame:")
display(merged_df.head())
print(f"\nShape of the merged DataFrame: {merged_df.shape}")

# Define the target variable 'Kidney_Risk'
# 1 = at risk / self-reported CKD (KIQ044 == 1)
# 0 = not at risk (KIQ044 != 1)

# Check unique values and value counts of KIQ044 before dropping
print("Unique values of KIQ044 before dropping:")
print(merged_df['KIQ044'].unique())
print("\nValue counts for KIQ044 before dropping:")
display(merged_df['KIQ044'].value_counts(dropna=False))


merged_df['Kidney_Risk'] = (merged_df['KIQ044'] == 1).astype(int)

# Drop the specified columns
columns_to_drop = ['KIQ044'] # Start with KIQ044

# Check if KIQ046 and KIQ048 exist in the dataframe before dropping
if 'KIQ046' in merged_df.columns:
    columns_to_drop.append('KIQ046')
if 'KIQ048' in merged_df.columns:
    columns_to_drop.append('KIQ048')

merged_df = merged_df.drop(columns=columns_to_drop)

print("\nMerged DataFrame with 'Kidney_Risk' target variable:")
display(merged_df.head())
print(f"\nValue counts for the target variable 'Kidney_Risk':")
display(merged_df['Kidney_Risk'].value_counts())

print(merged_df['KIQ044'].unique())

# Merge all dataframes in processed_dataframes on 'SEQN'
# Start with the first dataframe
merged_df = list(processed_dataframes.values())[0]

# Iterate through the rest of the dataframes and merge
for name, df in list(processed_dataframes.items())[1:]:
    merged_df = pd.merge(merged_df, df, on='SEQN', how='outer')

print("Merged DataFrame:")
display(merged_df.head())
print(f"\nShape of the merged DataFrame: {merged_df.shape}")

# Merge all dataframes in processed_dataframes on 'SEQN'
# Start with the first dataframe
merged_df = list(processed_dataframes.values())[0]

# Iterate through the rest of the dataframes and merge
for name, df in list(processed_dataframes.items())[1:]:
    merged_df = pd.merge(merged_df, df, on='SEQN', how='outer')

print("Merged DataFrame:")
display(merged_df.head())
print(f"\nShape of the merged DataFrame: {merged_df.shape}")

print(f"\nValue counts for the target variable 'Kidney_Risk' in the merged DataFrame:")
if 'Kidney_Risk' in merged_df.columns:
    display(merged_df['Kidney_Risk'].value_counts())
else:
    print("'Kidney_Risk' column not found in the merged DataFrame.")

# Create age groups
# Assuming 'RIDAGEYR' is the age column in years from the DEMO_L1 dataframe
if 'RIDAGEYR' in merged_df.columns and 'DEMO_L1' in dataframes:
    # Use the maximum age from the original DEMO_L1 dataframe before scaling
    original_max_age = dataframes['DEMO_L1']['RIDAGEYR'].max()
    bins = [0, 18, 35, 55, 65, 75, 85, original_max_age + 1] # Add 1 to include the max age
    labels = ['0-18', '19-35', '36-55', '56-65', '66-75', '76-85', '85+']
    merged_df['Age_Group'] = pd.cut(merged_df['RIDAGEYR'], bins=bins, labels=labels, right=False)

    # Display value counts for the new Age_Group feature
    print("Value counts for 'Age_Group':")
    display(merged_df['Age_Group'].value_counts(dropna=False))
else:
    print("'RIDAGEYR' column not found or original DEMO_L1 dataframe not available. Skipping Age Group feature engineering.")

# You can add more feature engineering steps here if needed

print("\nDataFrame after Feature Engineering:")
display(merged_df.head())

from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
import numpy as np

# Define features (X) and target (y)
# Drop 'SEQN' as it's an identifier and not a feature
# Drop 'Age_Group' as it's a categorical feature created from 'RIDAGEYR' and needs one-hot encoding later if used directly
X = merged_df.drop(['SEQN', 'Kidney_Risk', 'Age_Group'], axis=1, errors='ignore')
y = merged_df['Kidney_Risk']

# Drop rows where the target variable 'Kidney_Risk' is NaN
combined_df = pd.concat([X, y], axis=1)
combined_df.dropna(subset=['Kidney_Risk'], inplace=True)
X = combined_df.drop('Kidney_Risk', axis=1)
y = combined_df['Kidney_Risk']

# Handle potential non-numeric columns in X before splitting if any remain
# This might happen if new categorical features were added during feature engineering
X = pd.get_dummies(X, drop_first=True)


# Split data into training (60%), validation (20%), and test (20%) sets
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.4, random_state=42, stratify=y)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)

# Impute missing values in the feature sets after splitting
# Use the mean imputation strategy
imputer = SimpleImputer(strategy='mean')

# Fit on the training data and transform training, validation, and test data
X_train = imputer.fit_transform(X_train)
X_val = imputer.transform(X_val)
X_test = imputer.transform(X_test)


print("Data Splitting and Imputation complete.")
print(f"Shape of X_train: {X_train.shape}")
print(f"Shape of X_val: {X_val.shape}")
print(f"Shape of X_test: {X_test.shape}")
print(f"Shape of y_train: {y_train.shape}")
print(f"Shape of y_val: {y_val.shape}")
print(f"Shape of y_test: {y_test.shape}")

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

# 1. Logistic Regression
print("Training Logistic Regression Model...")
logreg = LogisticRegression(max_iter=1000, random_state=42)
logreg.fit(X_train, y_train)
print("Logistic Regression Model Trained.")

# 2. RandomForestClassifier
print("\nTraining RandomForestClassifier Model...")
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
print("RandomForestClassifier Model Trained.")

from sklearn.metrics import classification_report, roc_auc_score, roc_curve, auc
import matplotlib.pyplot as plt

# Evaluate Logistic Regression
print("--- Logistic Regression Model Evaluation ---")
y_val_pred_logreg = logreg.predict(X_val)
y_val_prob_logreg = logreg.predict_proba(X_val)[:, 1]

print("Classification Report:")
print(classification_report(y_val, y_val_pred_logreg))
print(f"AUC: {roc_auc_score(y_val, y_val_prob_logreg):.4f}")

# Plot ROC curve for Logistic Regression
fpr_logreg, tpr_logreg, _ = roc_curve(y_val, y_val_prob_logreg)
roc_auc_logreg = auc(fpr_logreg, tpr_logreg)

plt.figure(figsize=(10, 8))
plt.plot(fpr_logreg, tpr_logreg, color='darkorange', lw=2, label=f'Logistic Regression (AUC = {roc_auc_logreg:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend(loc="lower right")
plt.show()


print("\n--- RandomForestClassifier Model Evaluation ---")
y_val_pred_rf = rf.predict(X_val)
y_val_prob_rf = rf.predict_proba(X_val)[:, 1]

print("Classification Report:")
print(classification_report(y_val, y_val_pred_rf))
print(f"AUC: {roc_auc_score(y_val, y_val_prob_rf):.4f}")

# Plot ROC curve for RandomForestClassifier
fpr_rf, tpr_rf, _ = roc_curve(y_val, y_val_prob_rf)
roc_auc_rf = auc(fpr_rf, tpr_rf)

plt.figure(figsize=(10, 8))
plt.plot(fpr_rf, tpr_rf, color='darkorange', lw=2, label=f'RandomForestClassifier (AUC = {roc_auc_rf:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend(loc="lower right")
plt.show()

from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [None, 5, 10, 20],
    'min_samples_split': [2, 5],
    'min_samples_leaf': [1, 2],
    'max_features': ['sqrt', 'log2']
}

grid_search = GridSearchCV(
    estimator=RandomForestClassifier(random_state=42),
    param_grid=param_grid,
    cv=5,
    scoring='roc_auc',
    n_jobs=-1,
    verbose=1
)

grid_search.fit(X_train, y_train)
print("Best hyperparameters:", grid_search.best_params_)

# Final model using best parameters
best_rf = grid_search.best_estimator_

# Evaluate on test set
from sklearn.metrics import classification_report, roc_auc_score

y_pred_test = best_rf.predict(X_test)
y_proba_test = best_rf.predict_proba(X_test)[:, 1]

print("Test Set Performance:")
print(classification_report(y_test, y_pred_test))
print("ROC AUC:", roc_auc_score(y_test, y_proba_test))

import matplotlib.pyplot as plt
import pandas as pd

importances = pd.Series(best_rf.feature_importances_, index=X.columns) # Use X.columns for original feature names
top_features = importances.sort_values(ascending=False).head(15)

top_features.plot(kind='barh')
plt.title('Top 15 Feature Importances')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()
