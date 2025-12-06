# API 使用示例

## 📡 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **Content-Type**: `application/json`

## 1. 健康检查

### 请求

```bash
curl -X GET http://localhost:8000/api/v1/health
```

### 响应

```json
{
  "status": "healthy",
  "database": "connected",
  "app_name": "RFID Cold Chain Monitor",
  "version": "v1"
}
```

## 2. 上传包裹数据（ESP32 调用）

### 请求

```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -H "Content-Type: application/json" \
  -d '{
    "package_id": 1001,
    "temperature": 24.5,
    "timestamp": 1700000000
  }'
```

### 响应（成功）

```json
{
  "status": "success",
  "message": "Data for package 1001 received",
  "record_id": 123
}
```

### 响应（失败 - 验证错误）

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

## 3. 查询包裹历史记录

### 请求（基础查询）

```bash
curl -X GET http://localhost:8000/api/v1/packages/1001/records
```

### 请求（分页查询）

```bash
curl -X GET "http://localhost:8000/api/v1/packages/1001/records?limit=50&offset=0"
```

### 响应

```json
{
  "package_id": 1001,
  "total_records": 150,
  "records": [
    {
      "id": 1,
      "package_id": 1001,
      "temperature": 24.5,
      "timestamp": 1700000000,
      "created_at": "2024-11-26T14:30:00"
    },
    {
      "id": 2,
      "package_id": 1001,
      "temperature": 25.2,
      "timestamp": 1700003600,
      "created_at": "2024-11-26T15:30:00"
    }
  ]
}
```

## 4. 获取最新记录

### 请求

```bash
curl -X GET http://localhost:8000/api/v1/packages/1001/latest
```

### 响应（成功）

```json
{
  "id": 150,
  "package_id": 1001,
  "temperature": 26.8,
  "timestamp": 1700500000,
  "created_at": "2024-11-27T10:30:00"
}
```

### 响应（未找到）

```json
{
  "detail": "No records found for package 1001"
}
```

## 🔧 Python 示例

### 上传数据

```python
import requests
import time

url = "http://localhost:8000/api/v1/upload"
data = {
    "package_id": 1001,
    "temperature": 24.5,
    "timestamp": int(time.time())
}

response = requests.post(url, json=data)
print(response.json())
```

### 查询历史

```python
import requests

package_id = 1001
url = f"http://localhost:8000/api/v1/packages/{package_id}/records"
params = {"limit": 100, "offset": 0}

response = requests.get(url, params=params)
data = response.json()

print(f"Total records: {data['total_records']}")
for record in data['records']:
    print(f"Temp: {record['temperature']}°C at {record['created_at']}")
```

## 🔌 JavaScript/Node.js 示例

### 上传数据

```javascript
const axios = require('axios');

const uploadData = async () => {
  const url = 'http://localhost:8000/api/v1/upload';
  const data = {
    package_id: 1001,
    temperature: 24.5,
    timestamp: Math.floor(Date.now() / 1000)
  };

  try {
    const response = await axios.post(url, data);
    console.log(response.data);
  } catch (error) {
    console.error('Error:', error.response.data);
  }
};

uploadData();
```

### 查询历史

```javascript
const axios = require('axios');

const getHistory = async (packageId) => {
  const url = `http://localhost:8000/api/v1/packages/${packageId}/records`;
  
  try {
    const response = await axios.get(url, {
      params: { limit: 100, offset: 0 }
    });
    
    console.log(`Total records: ${response.data.total_records}`);
    response.data.records.forEach(record => {
      console.log(`Temp: ${record.temperature}°C at ${record.created_at}`);
    });
  } catch (error) {
    console.error('Error:', error.response.data);
  }
};

getHistory(1001);
```

## 🤖 ESP32 示例（C++）

```cpp
#include <HTTPClient.h>
#include <ArduinoJson.h>

void uploadToServer(int packageId, float temperature, uint64_t timestamp) {
  HTTPClient http;
  http.begin("http://192.168.1.100:8000/api/v1/upload");
  http.addHeader("Content-Type", "application/json");
  
  // 构建 JSON
  StaticJsonDocument<200> doc;
  doc["package_id"] = packageId;
  doc["temperature"] = temperature;
  doc["timestamp"] = timestamp;
  
  String requestBody;
  serializeJson(doc, requestBody);
  
  // 发送请求
  int httpResponseCode = http.POST(requestBody);
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("Response: " + response);
  } else {
    Serial.printf("Error code: %d\n", httpResponseCode);
  }
  
  http.end();
}
```

## 📊 Postman Collection

可以导入以下 JSON 到 Postman：

```json
{
  "info": {
    "name": "RFID Backend API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/health"
      }
    },
    {
      "name": "Upload Package Data",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/upload",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"package_id\": 1001,\n  \"temperature\": 24.5,\n  \"timestamp\": 1700000000\n}"
        }
      }
    },
    {
      "name": "Get Package History",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/packages/1001/records"
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000/api/v1"
    }
  ]
}
```
