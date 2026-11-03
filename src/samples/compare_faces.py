#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比较两张图片中的人脸是否为同一人（对应原 compare-faces 语义）。

用法:
  python compare_faces.py media/image1.png media/image2.png
"""
import base64
import os
import sys

from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkfrs.v2 import (
    CompareFaceByBase64Request,
    FaceCompareBase64Req,
    FrsClient,
)
from huaweicloudsdkfrs.v2.region.frs_region import FrsRegion


def read_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def main():
    if len(sys.argv) < 3:
        print("Usage: python compare_faces.py <image1_path> <image2_path>")
        sys.exit(1)
    image1_path, image2_path = sys.argv[1], sys.argv[2]

    client = FrsClient.new_builder() \
        .with_credentials(
            BasicCredentials(os.environ["HW_ACCESS_KEY"], os.environ["HW_SECRET_KEY"])
        ) \
        .with_region(FrsRegion.value_of(os.environ.get("HW_REGION", "cn-north-4"))) \
        .build()

    body = FaceCompareBase64Req(
        image1_base64=read_base64(image1_path),
        image2_base64=read_base64(image2_path),
    )
    request = CompareFaceByBase64Request(body=body)
    try:
        response = client.compare_face_by_base64(request)
        print("Similarity:", response.to_json_object())
    except exceptions.ClientRequestException as e:
        print("Error code:", e.status_code)
        print("Error message:", e.error_msg)


if __name__ == "__main__":
    main()
