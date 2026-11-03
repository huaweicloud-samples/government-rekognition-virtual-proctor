# ============================================================
# 输出
# ============================================================

output "web_url" {
  description = "前端静态网站访问地址（构建产物上传至 OBS 后打开）"
  value       = "https://${huaweicloud_obs_bucket.web.bucket_domain_name}"
}

output "web_bucket" {
  description = "前端静态网站桶名"
  value       = huaweicloud_obs_bucket.web.bucket
}

output "auth_login_function" {
  description = "登录函数名称（触发器的 API 调用地址请在 FunctionGraph 控制台查看）"
  value       = huaweicloud_fgs_function.auth_login.name
}

output "proctor_function" {
  description = "监考处理函数名称（触发器的 API 调用地址请在 FunctionGraph 控制台查看）"
  value       = huaweicloud_fgs_function.proctor.name
}

output "face_set_name" {
  description = "人脸库名称（部署后执行 src/setup/create_face_set.py 创建）"
  value       = var.face_set_name
}
