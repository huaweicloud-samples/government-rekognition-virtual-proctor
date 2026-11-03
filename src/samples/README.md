# 调用样例

本目录提供基于华为云 SDK 的 Python 调用样例，覆盖监考系统用到的四类检测能力：

| 文件 | 能力 | 对应服务 |
| --- | --- | --- |
| `add_face.py` | 向人脸库添加人脸 | 人脸识别服务 FRS |
| `search_face.py` | 在人脸库中检索相似人脸 | 人脸识别服务 FRS |
| `detect_faces.py` | 检测图片中的人脸 | 人脸识别服务 FRS |
| `compare_faces.py` | 比较两张图片是否为同一人 | 人脸识别服务 FRS |
| `detect_labels.py` | 图片标签识别（违规物品检测） | 图像识别服务 |
| `detect_moderation.py` | 图片内容审核（违规内容检测） | 内容审核服务 |

## 前置条件

1. 已开通所需服务（人脸识别 FRS / 图像识别 Image / 内容审核 Moderation），获取访问密钥 AK/SK。
2. 安装依赖：

   ```bash
   pip install huaweicloudsdkcore huaweicloudsdkfrs huaweicloudsdkimage huaweicloudsdkmoderation
   ```

3. 配置环境变量：

   ```bash
   export HW_ACCESS_KEY=your-ak
   export HW_SECRET_KEY=your-sk
   export HW_REGION=cn-north-4
   ```

## 使用示例

```bash
# 1. 创建人脸库（部署后只需执行一次）
python ../setup/create_face_set.py

# 2. 添加人脸
python add_face.py media/face-index.jpeg "Zhang San"

# 3. 检索人脸
python search_face.py media/face-search.jpeg

# 4. 检测人脸
python detect_faces.py media/face.png

# 5. 人脸比对
python compare_faces.py media/image1.png media/image2.png

# 6. 标签识别（可指定关注物品）
python detect_labels.py media/face.png "Mobile Phone"

# 7. 内容审核
python detect_moderation.py media/image1.png
```

## 说明

- `media/` 目录内的图片为验证用样例图片，实际使用请替换为自己的图片。
- 各脚本的请求/响应字段均以华为云 SDK 实际暴露的模型为准，未做字段猜测。
