# ESP32 嵌入式端对接文档

## 📋 文档概述

本文档为 ESP32 开发者提供完整的后端 API 对接指南，包括接口说明、数据格式、错误处理和完整代码示例。

---

## 🌐 服务器信息

### 开发环境
- **服务器地址**: `http://192.168.1.100:8000` （请替换为实际 IP）
- **API 版本**: `v1`
- **Base URL**: `http://192.168.1.100:8000/api/v1`

### 生产环境
- **服务器地址**: `http://your-domain.com` 或 `https://your-domain.com`
- **Base URL**: `http://your-domain.com/api/v1`

---

## 📡 核心接口说明

### 1. 健康检查接口（可选）

**用途**: 测试服务器连接状态

**接口信息**:
- **Method**: `GET`
- **URL**: `/api/v1/health`
- **Content-Type**: 无需设置

**请求示例**:
```
GET http://192.168.1.100:8000/api/v1/health
```

**成功响应** (HTTP 200):
```json
{
  "status": "healthy",
  "database": "connected",
  "app_name": "RFID Cold Chain Monitor",
  "version": "v1"
}
```

**ESP32 代码示例**:
```cpp
bool checkServerHealth() {
  HTTPClient http;
  http.begin("http://192.168.1.100:8000/api/v1/health");
  
  int httpCode = http.GET();
  
  if (httpCode == 200) {
    String payload = http.getString();
    Serial.println("Server is healthy: " + payload);
    http.end();
    return true;
  } else {
    Serial.printf("Health check failed: %d\n", httpCode);
    http.end();
    return false;
  }
}
```

---

### 2. 数据上传接口（核心接口）⭐

**用途**: ESP32 上传 RFID 读取的包裹温度数据

**接口信息**:
- **Method**: `POST`
- **URL**: `/api/v1/upload`
- **Content-Type**: `application/json`

#### 请求参数

| 参数名 | 类型 | 必填 | 范围/格式 | 说明 |
|--------|------|------|-----------|------|
| `package_id` | int | ✅ | > 0 | 包裹ID，必须为正整数 |
| `temperature` | float | ✅ | -50.0 ~ 100.0 | 温度值（摄氏度） |
| `timestamp` | int | ✅ | > 0 | Unix时间戳（秒），不能是未来时间 |

#### 请求示例

```json
{
  "package_id": 1001,
  "temperature": 24.5,
  "timestamp": 1700000000
}
```

#### 成功响应 (HTTP 200)

```json
{
  "status": "success",
  "message": "Data for package 1001 received",
  "record_id": 123
}
```

#### 错误响应

**1. 数据验证失败 (HTTP 422)**

```json
{
  "detail": [
    {
      "type": "greater_than",
      "loc": ["body", "package_id"],
      "msg": "Input should be greater than 0",
      "input": -1
    }
  ]
}
```

**2. 服务器错误 (HTTP 500)**

```json
{
  "detail": "Internal server error message"
}
```

#### ESP32 完整代码示例

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// 服务器配置
const char* serverUrl = "http://192.168.1.100:8000/api/v1/upload";

/**
 * 上传包裹数据到服务器
 * 
 * @param packageId 包裹ID
 * @param temperature 温度值
 * @param timestamp Unix时间戳
 * @return true 上传成功, false 上传失败
 */
bool uploadPackageData(uint32_t packageId, float temperature, uint64_t timestamp) {
  // 检查 WiFi 连接
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ WiFi not connected!");
    return false;
  }
  
  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");
  
  // 构建 JSON 数据
  StaticJsonDocument<200> doc;
  doc["package_id"] = packageId;
  doc["temperature"] = temperature;
  doc["timestamp"] = timestamp;
  
  String requestBody;
  serializeJson(doc, requestBody);
  
  // 打印请求信息（调试用）
  Serial.println("📤 Uploading data:");
  Serial.println(requestBody);
  
  // 发送 POST 请求
  int httpResponseCode = http.POST(requestBody);
  
  // 处理响应
  bool success = false;
  if (httpResponseCode == 200) {
    String response = http.getString();
    Serial.println("✅ Upload successful!");
    Serial.println("Response: " + response);
    success = true;
  } else if (httpResponseCode == 422) {
    String response = http.getString();
    Serial.println("❌ Validation error!");
    Serial.println("Response: " + response);
  } else if (httpResponseCode > 0) {
    Serial.printf("❌ HTTP Error: %d\n", httpResponseCode);
    String response = http.getString();
    Serial.println("Response: " + response);
  } else {
    Serial.printf("❌ Connection failed: %s\n", http.errorToString(httpResponseCode).c_str());
  }
  
  http.end();
  return success;
}

// 使用示例
void loop() {
  // 假设从 RFID 读取到的数据
  uint32_t packageId = 1001;
  float temperature = 24.5;
  uint64_t timestamp = 1700000000; // 实际应使用 NTP 获取的时间戳
  
  // 上传数据
  if (uploadPackageData(packageId, temperature, timestamp)) {
    Serial.println("Data uploaded successfully!");
  } else {
    Serial.println("Failed to upload data!");
  }
  
  delay(5000); // 5秒后再次上传
}
```

---

## ⚠️ 重要注意事项

### 1. 数据验证规则

#### package_id（包裹ID）
- ✅ **必须**: 正整数（> 0）
- ❌ **不允许**: 0、负数、小数

```cpp
// ✅ 正确
uint32_t packageId = 1001;

// ❌ 错误
int packageId = -1;    // 负数
int packageId = 0;     // 零
```

#### temperature（温度）
- ✅ **范围**: -50.0°C ~ 100.0°C
- ✅ **类型**: 浮点数
- ⚠️ **告警**: 超过 30°C 或低于 -10°C 会触发后端告警日志

```cpp
// ✅ 正确
float temp = 24.5;
float temp = -15.0;  // 会触发低温告警
float temp = 35.0;   // 会触发高温告警

// ❌ 错误
float temp = 150.0;  // 超出范围，验证失败
float temp = -60.0;  // 超出范围，验证失败
```

#### timestamp（时间戳）
- ✅ **格式**: Unix 时间戳（秒）
- ✅ **类型**: 正整数
- ❌ **不允许**: 未来时间（允许1小时误差）

```cpp
// ✅ 正确 - 使用当前时间
uint64_t timestamp = (uint64_t)time(nullptr);

// ✅ 正确 - 使用 NTP 时间
time_t now;
time(&now);
uint64_t timestamp = (uint64_t)now;

// ❌ 错误 - 未来时间
uint64_t timestamp = 9999999999;
```

---

### 2. 时间同步（重要！）

ESP32 必须通过 NTP 同步时间，否则时间戳会不准确。

#### NTP 时间同步代码

```cpp
#include <WiFi.h>
#include <time.h>

// NTP 服务器配置
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = 8 * 3600;  // GMT+8 (中国时区)
const int daylightOffset_sec = 0;

/**
 * 初始化 NTP 时间同步
 */
void initNTP() {
  Serial.println("🕐 Initializing NTP...");
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  
  // 等待时间同步
  struct tm timeinfo;
  int retry = 0;
  while (!getLocalTime(&timeinfo) && retry < 10) {
    Serial.println("Waiting for NTP sync...");
    delay(1000);
    retry++;
  }
  
  if (retry < 10) {
    Serial.println("✅ NTP synchronized!");
    Serial.println(&timeinfo, "Current time: %Y-%m-%d %H:%M:%S");
  } else {
    Serial.println("❌ NTP sync failed!");
  }
}

/**
 * 获取当前 Unix 时间戳
 */
uint64_t getCurrentTimestamp() {
  time_t now;
  time(&now);
  return (uint64_t)now;
}

// 在 setup() 中调用
void setup() {
  Serial.begin(115200);
  
  // 连接 WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  // 初始化 NTP
  initNTP();
}
```

---

### 3. WiFi 连接管理

#### 连接检查和重连

```cpp
/**
 * 检查并维护 WiFi 连接
 */
void ensureWiFiConnected() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠️ WiFi disconnected, reconnecting...");
    WiFi.disconnect();
    WiFi.begin(ssid, password);
    
    int retry = 0;
    while (WiFi.status() != WL_CONNECTED && retry < 20) {
      delay(500);
      Serial.print(".");
      retry++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("\n✅ WiFi reconnected!");
      Serial.print("IP: ");
      Serial.println(WiFi.localIP());
    } else {
      Serial.println("\n❌ WiFi reconnection failed!");
    }
  }
}
```

---

### 4. 错误处理和重试机制

#### 带重试的上传函数

```cpp
/**
 * 带重试机制的数据上传
 * 
 * @param packageId 包裹ID
 * @param temperature 温度值
 * @param timestamp Unix时间戳
 * @param maxRetries 最大重试次数
 * @return true 上传成功, false 上传失败
 */
bool uploadWithRetry(uint32_t packageId, float temperature, uint64_t timestamp, int maxRetries = 3) {
  for (int attempt = 1; attempt <= maxRetries; attempt++) {
    Serial.printf("📤 Upload attempt %d/%d\n", attempt, maxRetries);
    
    // 确保 WiFi 连接
    ensureWiFiConnected();
    
    // 尝试上传
    if (uploadPackageData(packageId, temperature, timestamp)) {
      return true;  // 成功
    }
    
    // 失败后等待再重试
    if (attempt < maxRetries) {
      Serial.printf("⏳ Retrying in 2 seconds...\n");
      delay(2000);
    }
  }
  
  Serial.println("❌ All upload attempts failed!");
  return false;
}
```

---

### 5. 数据缓存（离线场景）

当网络不可用时，可以将数据缓存到本地，待网络恢复后再上传。

#### 简单的缓存实现

```cpp
#include <vector>

// 数据结构
struct CachedData {
  uint32_t packageId;
  float temperature;
  uint64_t timestamp;
};

// 缓存队列
std::vector<CachedData> dataCache;
const int MAX_CACHE_SIZE = 100;

/**
 * 添加数据到缓存
 */
void cacheData(uint32_t packageId, float temperature, uint64_t timestamp) {
  if (dataCache.size() >= MAX_CACHE_SIZE) {
    Serial.println("⚠️ Cache full, removing oldest data");
    dataCache.erase(dataCache.begin());
  }
  
  CachedData data = {packageId, temperature, timestamp};
  dataCache.push_back(data);
  Serial.printf("💾 Data cached (total: %d)\n", dataCache.size());
}

/**
 * 上传所有缓存的数据
 */
void uploadCachedData() {
  if (dataCache.empty()) {
    return;
  }
  
  Serial.printf("📤 Uploading %d cached records...\n", dataCache.size());
  
  auto it = dataCache.begin();
  while (it != dataCache.end()) {
    if (uploadPackageData(it->packageId, it->temperature, it->timestamp)) {
      Serial.println("✅ Cached data uploaded");
      it = dataCache.erase(it);  // 删除已上传的数据
    } else {
      Serial.println("❌ Failed to upload cached data");
      break;  // 停止上传，等待下次重试
    }
    delay(100);  // 避免请求过快
  }
  
  Serial.printf("💾 Remaining cached records: %d\n", dataCache.size());
}

/**
 * 智能上传（优先上传缓存数据）
 */
void smartUpload(uint32_t packageId, float temperature, uint64_t timestamp) {
  // 先尝试上传缓存的数据
  if (!dataCache.empty()) {
    uploadCachedData();
  }
  
  // 上传当前数据
  if (!uploadPackageData(packageId, temperature, timestamp)) {
    // 失败则缓存
    cacheData(packageId, temperature, timestamp);
  }
}
```

---

## 📝 完整的 ESP32 主程序示例

```cpp
#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <time.h>

// ==================== 配置区 ====================

// WiFi 配置
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// 服务器配置
const char* serverUrl = "http://192.168.1.100:8000/api/v1/upload";

// NTP 配置
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = 8 * 3600;  // GMT+8
const int daylightOffset_sec = 0;

// RC522 引脚配置
#define RST_PIN  4
#define SS_PIN   10

// ==================== 全局变量 ====================

MFRC522 mfrc522(SS_PIN, RST_PIN);

// RFID 数据结构（与写入端保持一致）
struct PackageData {
  uint32_t packageId;
  float temperature;
  uint64_t timestamp;
};

// ==================== 函数声明 ====================

void initWiFi();
void initNTP();
void ensureWiFiConnected();
uint64_t getCurrentTimestamp();
bool uploadPackageData(uint32_t packageId, float temperature, uint64_t timestamp);
bool uploadWithRetry(uint32_t packageId, float temperature, uint64_t timestamp, int maxRetries = 3);

// ==================== Setup ====================

void setup() {
  Serial.begin(115200);
  Serial.println("\n\n=================================");
  Serial.println("ESP32 RFID Data Uploader");
  Serial.println("=================================\n");
  
  // 1. 初始化 SPI 和 RC522
  SPI.begin();
  mfrc522.PCD_Init();
  Serial.println("✅ RC522 initialized");
  
  // 2. 连接 WiFi
  initWiFi();
  
  // 3. 同步 NTP 时间
  initNTP();
  
  Serial.println("\n🚀 System ready!\n");
}

// ==================== Loop ====================

void loop() {
  // 确保 WiFi 连接
  ensureWiFiConnected();
  
  // 检测新卡片
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
    return;
  }
  
  Serial.println("\n📇 Card detected!");
  
  // 验证扇区
  MFRC522::MIFARE_Key key;
  for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;
  
  byte sector = 1;
  byte blockAddr = 4;
  MFRC522::StatusCode status;
  
  status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, blockAddr, &key, &(mfrc522.uid));
  if (status != MFRC522::STATUS_OK) {
    Serial.print("❌ Auth failed: ");
    Serial.println(mfrc522.GetStatusCodeName(status));
    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();
    return;
  }
  
  // 读取数据
  byte buffer[18];
  byte size = sizeof(buffer);
  status = mfrc522.MIFARE_Read(blockAddr, buffer, &size);
  
  if (status == MFRC522::STATUS_OK) {
    // 解析数据
    PackageData data;
    memcpy(&data, buffer, sizeof(data));
    
    Serial.println("📊 Data read from card:");
    Serial.printf("  Package ID: %u\n", data.packageId);
    Serial.printf("  Temperature: %.2f°C\n", data.temperature);
    Serial.printf("  Timestamp: %llu\n", data.timestamp);
    
    // 上传数据（带重试）
    if (uploadWithRetry(data.packageId, data.temperature, data.timestamp, 3)) {
      Serial.println("✅ Data uploaded successfully!\n");
    } else {
      Serial.println("❌ Failed to upload data after retries!\n");
    }
    
  } else {
    Serial.print("❌ Read failed: ");
    Serial.println(mfrc522.GetStatusCodeName(status));
  }
  
  // 停止卡片操作
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
  
  delay(2000);  // 防止重复读取
}

// ==================== WiFi 函数 ====================

void initWiFi() {
  Serial.print("📶 Connecting to WiFi");
  WiFi.begin(ssid, password);
  
  int retry = 0;
  while (WiFi.status() != WL_CONNECTED && retry < 40) {
    delay(500);
    Serial.print(".");
    retry++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n❌ WiFi connection failed!");
  }
}

void ensureWiFiConnected() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠️ WiFi disconnected, reconnecting...");
    WiFi.disconnect();
    WiFi.begin(ssid, password);
    
    int retry = 0;
    while (WiFi.status() != WL_CONNECTED && retry < 20) {
      delay(500);
      Serial.print(".");
      retry++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("\n✅ WiFi reconnected!");
    }
  }
}

// ==================== NTP 函数 ====================

void initNTP() {
  Serial.println("🕐 Synchronizing time with NTP...");
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  
  struct tm timeinfo;
  int retry = 0;
  while (!getLocalTime(&timeinfo) && retry < 10) {
    Serial.print(".");
    delay(1000);
    retry++;
  }
  
  if (retry < 10) {
    Serial.println("\n✅ Time synchronized!");
    Serial.println(&timeinfo, "Current time: %Y-%m-%d %H:%M:%S");
  } else {
    Serial.println("\n❌ Time sync failed!");
  }
}

uint64_t getCurrentTimestamp() {
  time_t now;
  time(&now);
  return (uint64_t)now;
}

// ==================== HTTP 上传函数 ====================

bool uploadPackageData(uint32_t packageId, float temperature, uint64_t timestamp) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ WiFi not connected!");
    return false;
  }
  
  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(5000);  // 5秒超时
  
  // 构建 JSON
  StaticJsonDocument<200> doc;
  doc["package_id"] = packageId;
  doc["temperature"] = temperature;
  doc["timestamp"] = timestamp;
  
  String requestBody;
  serializeJson(doc, requestBody);
  
  Serial.println("📤 Uploading: " + requestBody);
  
  // 发送请求
  int httpCode = http.POST(requestBody);
  bool success = false;
  
  if (httpCode == 200) {
    String response = http.getString();
    Serial.println("✅ Response: " + response);
    success = true;
  } else if (httpCode > 0) {
    Serial.printf("❌ HTTP Error %d: %s\n", httpCode, http.getString().c_str());
  } else {
    Serial.printf("❌ Connection error: %s\n", http.errorToString(httpCode).c_str());
  }
  
  http.end();
  return success;
}

bool uploadWithRetry(uint32_t packageId, float temperature, uint64_t timestamp, int maxRetries) {
  for (int attempt = 1; attempt <= maxRetries; attempt++) {
    Serial.printf("📤 Attempt %d/%d\n", attempt, maxRetries);
    
    ensureWiFiConnected();
    
    if (uploadPackageData(packageId, temperature, timestamp)) {
      return true;
    }
    
    if (attempt < maxRetries) {
      Serial.println("⏳ Retrying in 2 seconds...");
      delay(2000);
    }
  }
  
  return false;
}
```

---

## 🔍 调试技巧

### 1. 串口监视器输出

建议在关键位置添加日志输出：

```cpp
Serial.println("📇 Card detected!");
Serial.printf("Package ID: %u\n", packageId);
Serial.printf("Temperature: %.2f°C\n", temperature);
Serial.println("📤 Uploading data...");
Serial.println("✅ Upload successful!");
```

### 2. 使用 Postman 测试后端

在 ESP32 开发前，先用 Postman 测试后端接口是否正常：

```
POST http://192.168.1.100:8000/api/v1/upload
Content-Type: application/json

{
  "package_id": 1001,
  "temperature": 24.5,
  "timestamp": 1700000000
}
```

### 3. 检查网络连通性

```cpp
// Ping 测试
void testConnection() {
  HTTPClient http;
  http.begin("http://192.168.1.100:8000/api/v1/health");
  int httpCode = http.GET();
  Serial.printf("Health check: %d\n", httpCode);
  http.end();
}
```

---

## 📊 性能优化建议

### 1. 减少不必要的请求

```cpp
// ❌ 不好：每次循环都上传
void loop() {
  uploadData(...);
  delay(100);
}

// ✅ 好：只在检测到新卡片时上传
void loop() {
  if (mfrc522.PICC_IsNewCardPresent()) {
    uploadData(...);
  }
}
```

### 2. 设置合理的超时时间

```cpp
http.setTimeout(5000);  // 5秒超时，避免长时间等待
```

### 3. 批量上传（可选）

如果数据量大，可以考虑批量上传：

```cpp
// 收集多条数据后一次性上传
std::vector<PackageData> batch;
if (batch.size() >= 10) {
  uploadBatch(batch);
  batch.clear();
}
```

---

## ❓ 常见问题

### Q1: 上传失败，返回 422 错误

**原因**: 数据验证失败

**解决方案**:
- 检查 `package_id` 是否为正整数
- 检查 `temperature` 是否在 -50 ~ 100 范围内
- 检查 `timestamp` 是否为有效时间戳（不能是未来时间）

### Q2: 上传失败，返回 500 错误

**原因**: 服务器内部错误

**解决方案**:
- 检查后端服务是否正常运行
- 检查数据库连接是否正常
- 查看后端日志获取详细错误信息

### Q3: 连接超时

**原因**: 网络问题或服务器地址错误

**解决方案**:
- 确认 ESP32 和服务器在同一网络
- 使用 `ping` 命令测试服务器连通性
- 检查防火墙设置

### Q4: 时间戳不准确

**原因**: NTP 未同步

**解决方案**:
- 确保 WiFi 连接后再初始化 NTP
- 检查 NTP 服务器是否可访问
- 使用国内 NTP 服务器（如 `cn.pool.ntp.org`）

---

## 📞 技术支持

如有问题，请提供以下信息：

1. ESP32 串口监视器完整输出
2. 后端服务日志
3. 网络配置信息
4. 具体的错误代码和错误信息

---

## 📝 更新记录

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 1.0.0 | 2024-11-26 | 初始版本 |

---

**文档维护**: 后端开发团队  
**最后更新**: 2024-11-26
