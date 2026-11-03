#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
向人脸库中添加人脸（对应原 index-face 语义）。

前置条件:
  1. 已创建人脸库（可先运行 src/setup/create_face_set.py）
  2. 已配置环境变量 HW_ACCESS_KEY / HW_SECRET_KEY / HW_REGION（如 cn-north-4）
  3. 已安装依赖: pip install huaweicloudsdkfrs

用法:
  python add_face.py media/face-index.jpeg "Zhang San"
"""
import base64
import os
import sys

from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkfrs.v2 import (
    AddFacesBase64Req,
    AddFacesByBase64Request,
    FrsClient,
)
from huaweicloudsdkfrs.v2.region.frs_region import FrsRegion

FACE_SET_NAME = os.environ.get("FACE_SET_NAME", "virtual-proctor-face-set")


def read_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def main():
    if len(sys.argv) < 3:
        print("Usage: python add_face.py <image_path> <full_name>")
        sys.exit(1)
    image_path, full_name = sys.argv[1], sys.argv[2]

    client = FrsClient.new_builder() \
        .with_credentials(
            BasicCredentials(os.environ["HW_ACCESS_KEY"], os.environ["HW_SECRET_KEY"])
        ) \
        .with_region(FrsRegion.value_of(os.environ.get("HW_REGION", "cn-north-4"))) \
        .build()

    body = AddFacesBase64Req(
        image_base64=read_base64(image_path),
        external_image_id=full_name.replace(" ", "_"),
        external_fields={"full_name": full_name},
        single=True,
    )
    request = AddFacesByBase64Request(
        face_set_name=FACE_SET_NAME,
        body=body,
    )
    try:
        response = client.add_faces_by_base64(request)
        print("Face added:", response.to_json_object())
    except exceptions.ClientRequestException as e:
        print("Error code:", e.status_code)
        print("Error message:", e.error_msg)


if __name__ == "__main__":
    main()
