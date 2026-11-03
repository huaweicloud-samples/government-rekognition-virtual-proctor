#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在人脸库中搜索与给定图片最相似的人脸（对应原 search-faces 语义）。

前置条件同 add_face.py。

用法:
  python search_face.py media/face-search.jpeg
"""
import base64
import os
import sys

from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkfrs.v2 import (
    FaceSearchBase64Req,
    FrsClient,
    SearchFaceByBase64Request,
)
from huaweicloudsdkfrs.v2.region.frs_region import FrsRegion

FACE_SET_NAME = os.environ.get("FACE_SET_NAME", "virtual-proctor-face-set")
THRESHOLD = float(os.environ.get("SEARCH_THRESHOLD", "0.8"))


def read_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def main():
    if len(sys.argv) < 2:
        print("Usage: python search_face.py <image_path>")
        sys.exit(1)
    image_path = sys.argv[1]

    client = FrsClient.new_builder() \
        .with_credentials(
            BasicCredentials(os.environ["HW_ACCESS_KEY"], os.environ["HW_SECRET_KEY"])
        ) \
        .with_region(FrsRegion.value_of(os.environ.get("HW_REGION", "cn-north-4"))) \
        .build()

    body = FaceSearchBase64Req(
        image_base64=read_base64(image_path),
        threshold=THRESHOLD,
        top_n=1,
        return_fields=["external_fields"],
    )
    request = SearchFaceByBase64Request(
        face_set_name=FACE_SET_NAME,
        body=body,
    )
    try:
        response = client.search_face_by_base64(request)
        print("Search result:", response.to_json_object())
    except exceptions.ClientRequestException as e:
        print("Error code:", e.status_code)
        print("Error message:", e.error_msg)


if __name__ == "__main__":
    main()
