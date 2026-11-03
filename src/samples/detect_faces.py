#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检测图片中的人脸（对应原 detect-faces 语义）。
返回每张人脸的矩形、关键点、属性与置信度。

用法:
  python detect_faces.py media/face.png
"""
import base64
import os
import sys

from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkfrs.v2 import (
    DetectFaceByBase64Request,
    FaceDetectBase64Req,
    FrsClient,
)
from huaweicloudsdkfrs.v2.region.frs_region import FrsRegion


def read_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def main():
    if len(sys.argv) < 2:
        print("Usage: python detect_faces.py <image_path>")
        sys.exit(1)
    image_path = sys.argv[1]

    client = FrsClient.new_builder() \
        .with_credentials(
            BasicCredentials(os.environ["HW_ACCESS_KEY"], os.environ["HW_SECRET_KEY"])
        ) \
        .with_region(FrsRegion.value_of(os.environ.get("HW_REGION", "cn-north-4"))) \
        .build()

    body = FaceDetectBase64Req(image_base64=read_base64(image_path))
    request = DetectFaceByBase64Request(body=body)
    try:
        response = client.detect_face_by_base64(request)
        print("Detected faces:", response.to_json_object())
    except exceptions.ClientRequestException as e:
        print("Error code:", e.status_code)
        print("Error message:", e.error_msg)


if __name__ == "__main__":
    main()
