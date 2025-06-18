import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import Dense, Dropout # type: ignore
from tensorflow.keras.utils import to_categorical # type: ignore
import numpy as np
import joblib # Để lưu scaler

# --- Cấu hình ---
csv_file_name = 'gesture_data_auto_record.csv' # Đảm bảo đúng tên file CSV của bạn
model_save_path = 'gesture_recognition_model.h5'
scaler_save_path = 'scaler.pkl'

# --- Tải dữ liệu ---
try:
    df = pd.read_csv(csv_file_name)
    print(f"Đã tải {len(df)} mẫu dữ liệu từ '{csv_file_name}'.")
except FileNotFoundError:
    print(f"Lỗi: Không tìm thấy file '{csv_file_name}'. Vui lòng kiểm tra đường dẫn.")
    exit()

# Phân tích phân bố nhãn (kiểm tra cân bằng dữ liệu)
print("\nPhân bố mẫu theo từng cử chỉ:")
print(df['label'].value_counts().sort_index())

# --- Tiền xử lý dữ liệu ---
X = df.iloc[:, :-1].values
y = df.iloc[:, -1].values

scaler = StandardScaler()
X = scaler.fit_transform(X)
joblib.dump(scaler, scaler_save_path) # Lưu scaler

num_classes = len(np.unique(y)) + 1
y = to_categorical(y, num_classes=num_classes)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"\nKích thước tập huấn luyện: {X_train.shape[0]} mẫu")
print(f"Kích thước tập kiểm tra: {X_test.shape[0]} mẫu")
print(f"Số lượng đặc trưng (features): {X_train.shape[1]}")
print(f"Số lượng lớp: {num_classes}")

# --- Xây dựng và Huấn luyện mô hình ---
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

print("\nBắt đầu huấn luyện mô hình...")
history = model.fit(X_train, y_train,
                    epochs=75, # Có thể tăng từ 50 lên 75 hoặc 100 với nhiều dữ liệu hơn
                    batch_size=32,
                    validation_split=0.1,
                    verbose=1)

# --- Đánh giá và Lưu mô hình ---
loss, accuracy = model.evaluate(X_test, y_test, verbose=0)
print(f"\nĐộ chính xác trên tập kiểm tra: {accuracy:.4f}")

model.save(model_save_path)
print(f"Mô hình đã được lưu tại: {model_save_path}")
print(f"Scaler đã được lưu tại: {scaler_save_path}")