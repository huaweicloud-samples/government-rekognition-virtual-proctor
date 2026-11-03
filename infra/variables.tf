# ============================================================
# 全局变量
# ============================================================

variable "region" {
  description = "目标区域，例如 cn-north-4"
  type        = string
  default     = "cn-north-4"
}

variable "name_prefix" {
  description = "资源名称前缀（函数名、人脸库名等）"
  type        = string
  default     = "virtual-proctor"
}

variable "web_bucket_name" {
  description = "前端静态网站桶名（OBS 桶名全局唯一，必须自定义）"
  type        = string
}

variable "admin_users" {
  description = "管理员账号列表，格式 user1:sha256(password1),user2:sha256(password2)"
  type        = string
  sensitive   = true
}

variable "jwt_secret" {
  description = "JWT 签名密钥（部署前替换为强随机串）"
  type        = string
  sensitive   = true
}

variable "min_confidence" {
  description = "视觉检测最小置信度（0-100）"
  type        = number
  default     = 85
}

variable "objects_of_interest_labels" {
  description = "需检测的目标物体标签，逗号分隔"
  type        = string
  default     = "Mobile Phone,Cell Phone"
}

variable "face_set_name" {
  description = "人脸库名称"
  type        = string
  default     = "virtual-proctor-face-set"
}

variable "api_group_id" {
  description = "共享版 API 分组 ID（在 API 网关-共享版控制台创建分组后填入；留空则由触发器按需创建）"
  type        = string
  default     = ""
}

variable "auth_login_zip_url" {
  description = "登录函数代码包（zip）的 OBS 地址，格式 obs://bucket/key.zip；部署前先将 src/functions/auth_login 打包上传"
  type        = string
}

variable "proctor_zip_url" {
  description = "监考处理函数代码包（zip）的 OBS 地址，格式 obs://bucket/key.zip；部署前先将 src/functions/proctor 打包上传"
  type        = string
}

variable "access_key" {
  description = "用于调用视觉服务与 OBS 的访问密钥（从环境变量 HW_ACCESS_KEY 注入，勿硬编码）"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "与 access_key 配对的私有密钥（从环境变量 HW_SECRET_KEY 注入，勿硬编码）"
  type        = string
  sensitive   = true
}
