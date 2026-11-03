#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容审核：检测图片是否包含违规内容（对应监考函数中的"内容审核"语义）。
suggestion 为 "pass" 表示通过，否则返回违规分类。

用法:
  python detect_moderation.py media/image1.png
"""
import base64
import os
import sys

from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkmoderation.v3 import (
    CheckImageModerationRequest,
    ImageDetectionReq,
    ModerationClient,
)
from huaweicloudsdkmoderation.v3.region.moderation_region import ModerationRegion


def read_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def main():
    if len(sys.argv) < 2:
        print("Usage: python detect_moderation.py <image_path>")
        sys.exit(1)
    image_path = sys.argv[1]

    client = ModerationClient.new_builder() \
        .with_credentials(
            BasicCredentials(os.environ["HW_ACCESS_KEY"], os.environ["HW_SECRET_KEY"])
        ) \
        .with_region(ModerationRegion.value_of(os.environ.get("HW_REGION", "cn-north-4"))) \
        .build()

    body = ImageDetectionReq(
        image=read_base64(image_path),
        event_type="default",
    )
    request = CheckImageModerationRequest(body=body)
    try:
        response = client.check_image_moderation(request)
        result = response.to_json_object()
        print("Moderation result:", result)
        suggestion = result.get("result", {}).get("suggestion")
        print("Verdict:", "PASS" if suggestion == "pass" else "BLOCKED")
    except exceptions.ClientRequestException as e:
        print("Error code:", e.status_code)
        print("Error message:", e.error_msg)


if __name__ == "__main__":
    main()
