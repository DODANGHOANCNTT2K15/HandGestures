import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import Dense, Dropout # type: ignore
from tensorflow.keras.utils import to_categorical # type: ignore
import numpy as np
import joblib 

# --- config ---
csv_file_name = 'gesture_data_auto_record.csv' 
model_save_path = 'gesture_recognition_model.h5'
scaler_save_path = 'scaler.pkl'

# --- load data ---
try:
    df = pd.read_csv(csv_file_name)
    print(f"Đã tải {len(df)} mẫu dữ liệu từ '{csv_file_name}'.")
except FileNotFoundError:
    print(f"Lỗi: Không tìm thấy file '{csv_file_name}'. Vui lòng kiểm tra đường dẫn.")
    exit()

# Analyze label distribution (check data balance)
print("\nSample distribution per gesture:")
print(df['label'].value_counts().sort_index())

# --- Data Preprocessing ---
X = df.iloc[:, :-1].values
y = df.iloc[:, -1].values

scaler = StandardScaler()
X = scaler.fit_transform(X)
joblib.dump(scaler, scaler_save_path) # Save scaler

num_classes = len(np.unique(y)) + 1
y = to_categorical(y, num_classes=num_classes)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"\nTraining set size: {X_train.shape[0]} samples")
print(f"Test set size: {X_test.shape[0]} samples")
print(f"Number of features: {X_train.shape[1]}")
print(f"Number of classes: {num_classes}")

# --- Build and Train Model ---
model = Sequential([
    Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
    Dropout(0.3),
    Dense(64, activation='relu'),
    Dropout(0.3),
    Dense(num_classes, activation='softmax')
])

model.compile(optimizer='adam',
              loss='categorical_crossentropy', 
              metrics=['accuracy'])

print("\nStarting model training...")
history = model.fit(X_train, y_train,
                    epochs=75, 
                    batch_size=32,
                    validation_split=0.1,
                    verbose=1)

# --- Evaluate and Save Model ---
loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
print(f"\nTest set accuracy: {accuracy:.4f}")

model.save(model_save_path)
print(f"Model saved at: {model_save_path}")
print(f"Scaler saved at: {scaler_save_path}")