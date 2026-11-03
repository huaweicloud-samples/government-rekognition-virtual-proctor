# -*- coding: utf-8 -*-
"""
考试监考处理函数：人脸注册与四项实时检测。

环境变量：
  JWT_SECRET                JWT 签名密钥（与登录函数一致）
  FACE_SET_NAME             人脸库名称
  MIN_CONFIDENCE            最小置信度（0-100）
  OBJECTS_OF_INTEREST_LABELS 目标物体标签，逗号分隔
  REGION                    区域，如 cn-north-4
  HW_ACCESS_KEY / HW_SECRET_KEY  视觉服务与对象存储凭据（由 Terraform 注入）

事件：POST /proctor
  body: {"action": "index", "image": "<base64>", "fullName": "..."}
    或 {"action": "process", "image": "<base64>"}

响应：
  index   → 200 {"ExternalImageId": "..."}
  process → 200 [ {TestName, Success, Details}, ... ]
"""
import base64
import hashlib
import hmac
import json
import os
import time
import uuid

# ---------------------------------------------------------------------------
# JWT 校验（HS256，标准库实现，与登录函数共用同一套编码规则）
# ---------------------------------------------------------------------------
def _b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=")


def _b64url_decode(data):
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _sign(secret, message):
    return hmac.new(secret.encode("utf-8"), message, hashlib.sha256).digest()


def _verify_token(secret, token):
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header, payload, signature = parts
        signing_input = (header + "." + payload).encode("utf-8")
        expected = _b64url(_sign(secret, signing_input)).decode("utf-8")
        if not hmac.compare_digest(signature, expected):
            return None
        claims = json.loads(_b64url_decode(payload))
        if claims.get("exp", 0) < int(time.time()):
            return None
        return claims.get("sub")
    except Exception:
        return None


def _authenticated_user(event):
    headers = event.get("headers") or {}
    auth = headers.get("Authorization") or headers.get("authorization") or ""
    if auth.startswith("Bearer "):
        return _verify_token(os.environ["JWT_SECRET"], auth[7:])
    return None


# ---------------------------------------------------------------------------
# 华为云 SDK 客户端（懒加载，降低冷启动开销）
# ---------------------------------------------------------------------------
def _credentials():
    from huaweicloudsdkcore.auth.credentials import BasicCredentials
    return BasicCredentials(os.environ["HW_ACCESS_KEY"],
                            os.environ["HW_SECRET_KEY"])


def _frs_client():
    from huaweicloudsdkfrs.v2 import FrsClient
    from huaweicloudsdkfrs.v2.region.frs_region import FrsRegion
    return FrsClient.new_builder() \
        .with_credentials(_credentials()) \
        .with_region(FrsRegion.value_of(os.environ["REGION"])) \
        .build()


def _image_client():
    from huaweicloudsdkimage.v2 import ImageClient
    from huaweicloudsdkimage.v2.region.image_region import ImageRegion
    return ImageClient.new_builder() \
        .with_credentials(_credentials()) \
        .with_region(ImageRegion.value_of(os.environ["REGION"])) \
        .build()


def _moderation_client():
    from huaweicloudsdkmoderation.v3 import ModerationClient
    from huaweicloudsdkmoderation.v3.region.moderation_region import \
        ModerationRegion
    return ModerationClient.new_builder() \
        .with_credentials(_credentials()) \
        .with_region(ModerationRegion.value_of(os.environ["REGION"])) \
        .build()


# ---------------------------------------------------------------------------
# 业务逻辑
# ---------------------------------------------------------------------------
def _index_face(image_b64, full_name):
    """注册人脸：添加到人脸库并写入姓名元数据。"""
    from huaweicloudsdkfrs.v2 import (AddFacesByBase64Request,
                                      AddFacesBase64Req)
    external_image_id = str(uuid.uuid4())
    request = AddFacesByBase64Request()
    request.face_set_name = os.environ["FACE_SET_NAME"]
    request.body = AddFacesBase64Req(
        image_base64=image_b64,
        external_image_id=external_image_id,
        external_fields={"fullname": full_name},
        single=True,
    )
    _frs_client().add_faces_by_base64(request)
    return external_image_id


def _detect_faces(image_b64):
    """人脸检测：期望恰好 1 张人脸。"""
    from huaweicloudsdkfrs.v2 import (DetectFaceByBase64Request,
                                      FaceDetectBase64Req)
    test = {"TestName": "Face Detection", "Success": False, "Details": "0"}
    try:
        request = DetectFaceByBase64Request()
        request.body = FaceDetectBase64Req(image_base64=image_b64)
        response = _frs_client().detect_face_by_base64(request)
        count = len(response.faces)
        test["Success"] = count == 1
        test["Details"] = count
    except Exception as exc:  # noqa: BLE001
        test["Details"] = "Server error"
    return test


def _detect_labels(image_b64):
    """标签识别：检测目标物体（手机等）与人物。"""
    from huaweicloudsdkimage.v2 import (ImageTaggingReq,
                                        RunImageTaggingRequest)
    objects_of_interest = {
        label.strip().lower()
        for label in os.environ.get("OBJECTS_OF_INTEREST_LABELS", "").split(",")
        if label.strip()
    }
    objects_test = {"TestName": "Objects of Interest",
                    "Success": False, "Details": "0"}
    people_test = {"TestName": "Person Detection",
                   "Success": False, "Details": "0"}
    try:
        request = RunImageTaggingRequest()
        request.body = ImageTaggingReq(
            image=image_b64,
            language="zh",
            threshold=float(os.environ.get("MIN_CONFIDENCE", "85")) / 100.0,
        )
        response = _image_client().run_image_tagging(request)
        tags = response.result.tags if response.result else []
        matched = [item.tag for item in tags
                   if item.tag and item.tag.lower() in objects_of_interest]
        objects_test["Success"] = len(matched) == 0
        objects_test["Details"] = "0" if objects_test["Success"] \
            else ", ".join(sorted(matched))

        person_tags = [item for item in tags
                       if item.tag in ("人物", "人") or "person" in
                       (item.tag or "").lower()]
        people_test["Success"] = len(person_tags) > 0
        people_test["Details"] = "1" if people_test["Success"] else "0"
    except Exception as exc:  # noqa: BLE001
        objects_test["Success"] = False
        objects_test["Details"] = "Server error"
        people_test["Success"] = False
        people_test["Details"] = "Server error"
    return [objects_test, people_test]


def _detect_moderation(image_b64):
    """内容审核：期望结果建议为 pass（无不适当内容）。"""
    from huaweicloudsdkmoderation.v3 import (CheckImageModerationRequest,
                                             ImageDetectionReq)
    test = {"TestName": "Unsafe Content", "Success": False, "Details": "0"}
    try:
        request = CheckImageModerationRequest()
        request.body = ImageDetectionReq(
            image=image_b64,
            event_type="default",
        )
        response = _moderation_client().check_image_moderation(request)
        result = response.result or []
        blocked = [item for item in result if item.suggestion != "pass"]
        test["Success"] = len(blocked) == 0
        test["Details"] = "0" if test["Success"] else ", ".join(
            sorted({item.category for item in blocked}))
    except Exception as exc:  # noqa: BLE001
        test["Details"] = "Server error"
    return test


def _search_indexed_face(image_b64):
    """人脸搜索：在已注册人脸中匹配并返回姓名。"""
    from huaweicloudsdkfrs.v2 import (FaceSearchBase64Req,
                                      SearchFaceByBase64Request)
    test = {"TestName": "Person Recognition", "Success": False,
            "Details": "0"}
    try:
        request = SearchFaceByBase64Request()
        request.face_set_name = os.environ["FACE_SET_NAME"]
        request.body = FaceSearchBase64Req(
            image_base64=image_b64,
            threshold=float(os.environ.get("MIN_CONFIDENCE", "85")) / 100.0,
            top_n=1,
            return_fields=["fullname"],
        )
        response = _frs_client().search_face_by_base64(request)
        faces = response.faces or []
        if faces:
            fields = faces[0].external_fields or {}
            test["Success"] = True
            test["Details"] = fields.get("fullname") or "Unknown"
    except Exception as exc:  # noqa: BLE001
        # 未匹配到人脸时服务返回异常，等价于无人脸命中
        pass
    return test


def _handle_index(event):
    body = json.loads(event.get("body") or "{}")
    image_b64 = body.get("image")
    full_name = (body.get("fullName") or "").strip()
    if not image_b64 or not full_name:
        return _respond(400, {"error": "image and fullName are required"})
    external_image_id = _index_face(image_b64, full_name)
    return _respond(200, {"ExternalImageId": external_image_id})


def _handle_process(event):
    body = json.loads(event.get("body") or "{}")
    image_b64 = body.get("image")
    if not image_b64:
        return _respond(400, {"error": "image is required"})
    results = []
    results.extend(_detect_labels(image_b64))
    results.append(_search_indexed_face(image_b64))
    results.append(_detect_faces(image_b64))
    results.append(_detect_moderation(image_b64))
    return _respond(200, results)


def _respond(status, payload):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(payload),
    }


def handler(event, context):
    if not _authenticated_user(event):
        return _respond(401, {"error": "unauthorized"})
    try:
        body = json.loads(event.get("body") or "{}")
        action = body.get("action")
        if action == "index":
            return _handle_index(event)
        if action == "process":
            return _handle_process(event)
        return _respond(400, {"error": "unknown action"})
    except Exception as exc:  # noqa: BLE001
        return _respond(500, {"error": str(exc)})
