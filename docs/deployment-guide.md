# 部署指南

本文档描述如何在华为云（以 `cn-north-4` 为例）从零部署本监考系统。

## 1. 前置准备

1. 华为云账号，开通以下服务：**函数工作流 FunctionGraph**、**对象存储服务 OBS**、**API 网关（共享版）**、**人脸识别服务 FRS**、**图像识别服务**、**内容审核服务**。
2. 获取访问密钥 AK/SK（访问密钥管理页面创建）。
3. 本地安装：Terraform ≥ 1.3、华为云 Terraform Provider ≥ 1.97、Python 3.9+、Node.js 16+。
4. 命令行安装所需 SDK：

   ```bash
   pip install huaweicloudsdkcore huaweicloudsdkfrs huaweicloudsdkimage huaweicloudsdkmoderation
   ```

## 2. 准备函数代码包

```bash
cd src/functions/auth_login
zip -r auth_login.zip index.py

cd ../proctor
zip -r proctor.zip index.py
```

> 函数依赖仅用 Python 标准库（JWT 为自实现），无需打包第三方依赖。

将两个 zip 上传到 OBS（可用任意可访问的桶），记录 `obs://<bucket>/<key>.zip` 地址。

## 3. 构建前端并上传

```bash
cd src/frontend
npm install
npm run build
```

构建产物在 `src/frontend/build/`。将 `build/` 内所有文件上传到步骤 4 创建的 OBS 静态桶（`web_bucket_name`），并在桶根目录写入 `settings.js`（可复制仓库根目录的 `settings.js.example` 作为模板，填入真实 `apiEndpoint` 后上传；文件须定义全局变量 `window.proctorSettings`）：

```js
window.proctorSettings = {
  apiEndpoint: "https://<APIG-域名>/<分组路径>",
};
```

> 函数触发器创建后，在 FunctionGraph 控制台可查到对应 APIG 调用地址；`apiEndpoint` 填 `/proctor` 与 `/auth/login` 的公共前缀。

## 4. 创建 API 分组（可选）

共享版 API 需要分组。可在控制台"API 网关 → 共享版 → 分组"创建分组，把分组 ID 填入 `api_group_id` 变量；留空时触发器会按需创建分组（默认分组）。

## 5. 部署基础设施

```bash
cd infra
export TF_VAR_web_bucket_name="<全局唯一桶名>"
export TF_VAR_admin_users="admin:$(echo -n 'ChangeMe123' | shasum -a 256 | cut -d' ' -f1)"
export TF_VAR_jwt_secret="$(openssl rand -hex 32)"
export TF_VAR_auth_login_zip_url="obs://<bucket>/auth_login.zip"
export TF_VAR_proctor_zip_url="obs://<bucket>/proctor.zip"
export TF_VAR_access_key="$HW_ACCESS_KEY"
export TF_VAR_secret_key="$HW_SECRET_KEY"

terraform init
terraform plan
terraform apply -auto-approve
```

预期输出包含：`web_url`、`web_bucket`、`auth_login_function`、`proctor_function`、`face_set_name`。

## 6. 创建人脸库

```bash
export HW_ACCESS_KEY=... HW_SECRET_KEY=... HW_REGION=cn-north-4
python src/setup/create_face_set.py
```

预期输出：`Face set created: {...}`（若已存在则提示跳过）。

## 7. 上传前端构建产物

将 `src/frontend/build/` 全部文件（含 `settings.js`）上传到 `web_bucket` 桶。

## 8. 验证

1. 浏览器打开 `web_url` 输出地址。
2. 使用 `TF_VAR_admin_users` 中配置的账号（如 `admin` / `ChangeMe123`）登录。
3. 点击 **Add a new user**，上传一张人脸照片并填写姓名，确认提示添加成功。
4. 点击 **Start Virtual Proctor**，允许摄像头权限，画面中将实时展示四类检测结果。

## 9. 清理资源

```bash
cd infra
terraform destroy -auto-approve
```

> 人脸库为独立服务资源，Terraform 不管理；如需删除：
> `python src/samples/...` 或控制台人脸库管理页删除 `face_set_name` 对应人脸库。
> OBS 桶若 `force_destroy=true`，销毁时连同桶内对象一并删除，请确认无需要保留的数据。

## 10. 故障排查

| 现象 | 排查 |
| --- | --- |
| 前端提示"issue with your settings configuration" | `settings.js` 未上传或 `apiEndpoint` 不正确 |
| 登录返回 401 | `admin_users` 的 sha256 值格式不对（应为 `user:sha256(pass)`） |
| 函数执行超时 | 确认函数超时/内存满足变量定义（30 s / 60 s） |
| 人脸搜索无结果 | 先执行 Add User 注册；检查阈值 `MIN_CONFIDENCE` 是否过高 |
| API 404 | 触发器路径与 `settings.js` 中 `apiEndpoint` 前缀不一致 |
