#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
识别图片中的标签（对应监考函数中"违规物品检测"的图像识别语义）。
可传入关注标签（如 "Mobile Phone"）检查图片中是否出现对应物品。

用法:
  python detect_labels.py media/face.png "Mobile Phone"
"""
import base64
import os
import sys

from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkimage.v2 import (
    ImageClient,
    ImageTaggingReq,
    RunImageTaggingRequest,
)
from huaweicloudsdkimage.v2.region.image_region import ImageRegion

MIN_CONFIDENCE = float(os.environ.get("MIN_CONFIDENCE", "85"))


def read_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def main():
    if len(sys.argv) < 2:
        print("Usage: python detect_labels.py <image_path> [object_label]")
        sys.exit(1)
    image_path = sys.argv[1]
    target = sys.argv[2].lower() if len(sys.argv) > 2 else None

    client = ImageClient.new_builder() \
        .with_credentials(
            BasicCredentials(os.environ["HW_ACCESS_KEY"], os.environ["HW_SECRET_KEY"])
        ) \
        .with_region(ImageRegion.value_of(os.environ.get("HW_REGION", "cn-north-4"))) \
        .build()

    body = ImageTaggingReq(
        image=read_base64(image_path),
        language="zh",
        threshold=MIN_CONFIDENCE / 100.0,
    )
    request = RunImageTaggingRequest(body=body)
    try:
        response = client.run_image_tagging(request)
        result = response.to_json_object()
        print("All labels:", result)

        if target:
            found = [
                tag.get("tag")
                for tag in result.get("result", {}).get("tags", [])
                if target in str(tag.get("tag", "")).lower()
            ]
            print(f"Target label '{sys.argv[2]}' found:", bool(found))
    except exceptions.ClientRequestException as e:
        print("Error code:", e.status_code)
        print("Error message:", e.error_msg)


if __name__ == "__main__":
    main()
