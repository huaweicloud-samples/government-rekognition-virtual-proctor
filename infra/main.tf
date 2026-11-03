# ============================================================
# Provider
# ============================================================
provider "huaweicloud" {
  region     = var.region
  access_key = var.access_key
  secret_key = var.secret_key
}

# ============================================================
# 前端静态网站（OBS）
# ============================================================
resource "huaweicloud_obs_bucket" "web" {
  bucket        = var.web_bucket_name
  acl           = "public-read"
  force_destroy = true
  website {
    index_document = "index.html"
  }
  cors_rule {
    allowed_origins = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_headers = ["*"]
    max_age_seconds = 3600
  }
}

# ============================================================
# 登录函数（签发 JWT）
# ============================================================
resource "huaweicloud_fgs_function" "auth_login" {
  name        = "${var.name_prefix}-auth-login"
  app         = "default"
  description = "登录认证：校验账号并签发 JWT"
  handler     = "index.handler"
  memory_size = 128
  runtime     = "Python3.9"
  timeout     = 30
  code_type   = "obs"
  code_url    = var.auth_login_zip_url

  # 敏感配置走加密环境变量（KMS 加密存储），不落盘、不入代码仓
  encrypted_user_data = jsonencode({
    JWT_SECRET  = var.jwt_secret
    ADMIN_USERS = var.admin_users
  })
}

resource "huaweicloud_fgs_trigger" "auth_login" {
  function_urn = huaweicloud_fgs_function.auth_login.urn
  type         = "APIG"

  apig {
    api_name                = "auth-login"
    env_name                = "RELEASE"
    group_id                = var.api_group_id
    request_protocol        = "HTTPS"
    security_authentication = "NONE"
    timeout                 = 30
  }
}

# ============================================================
# 监考处理函数（人脸索引 / 检测 / 搜索 / 内容审核）
# ============================================================
resource "huaweicloud_fgs_function" "proctor" {
  name        = "${var.name_prefix}-proctor"
  app         = "default"
  description = "考试监考：人脸注册与四项实时检测"
  handler     = "index.handler"
  memory_size = 256
  runtime     = "Python3.9"
  timeout     = 60
  code_type   = "obs"
  code_url    = var.proctor_zip_url

  # 非敏感配置
  user_data = jsonencode({
    FACE_SET_NAME              = var.face_set_name
    MIN_CONFIDENCE             = tostring(var.min_confidence)
    OBJECTS_OF_INTEREST_LABELS = var.objects_of_interest_labels
    REGION                     = var.region
  })

  # 敏感配置（JWT 密钥与调用视觉服务的 AK/SK）走加密环境变量
  encrypted_user_data = jsonencode({
    JWT_SECRET    = var.jwt_secret
    HW_ACCESS_KEY = var.access_key
    HW_SECRET_KEY = var.secret_key
  })
}

resource "huaweicloud_fgs_trigger" "proctor" {
  function_urn = huaweicloud_fgs_function.proctor.urn
  type         = "APIG"

  apig {
    api_name                = "proctor"
    env_name                = "RELEASE"
    group_id                = var.api_group_id
    request_protocol        = "HTTPS"
    security_authentication = "NONE"
    timeout                 = 30
  }
}
