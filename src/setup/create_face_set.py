#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建监考系统使用的人脸库（部署完成后执行一次）。

前置条件:
  1. 已开通人脸识别服务 FRS
  2. 已配置环境变量 HW_ACCESS_KEY / HW_SECRET_KEY（或直接修改下方 AK/SK）
  3. 已安装依赖: pip install huaweicloudsdkfrs

用法:
  python create_face_set.py

说明:
  人脸库名称需与部署变量 face_set_name 保持一致（默认 virtual-proctor-face-set）。
  人脸库可容纳 10000 张人脸；如已存在同名库，脚本会直接退出。
"""
import os

from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkfrs.v2 import (
    CreateFaceSetRequest,
    CreateFaceSetReq,
    FrsClient,
    ShowFaceSetRequest,
    TypeInfo,
)
from huaweicloudsdkfrs.v2.region.frs_region import FrsRegion

FACE_SET_NAME = os.environ.get("FACE_SET_NAME", "virtual-proctor-face-set")


def main():
    client = FrsClient.new_builder() \
        .with_credentials(
            BasicCredentials(os.environ["HW_ACCESS_KEY"], os.environ["HW_SECRET_KEY"])
        ) \
        .with_region(FrsRegion.value_of(os.environ.get("HW_REGION", "cn-north-4"))) \
        .build()

    # 先检查是否已存在
    show_request = ShowFaceSetRequest(face_set_name=FACE_SET_NAME)
    try:
        client.show_face_set(show_request)
        print(f"Face set '{FACE_SET_NAME}' already exists, nothing to do.")
        return
    except exceptions.ClientRequestException as e:
        if e.status_code != 404:
            print("Error checking face set:", e.error_msg)
            return

    # 创建人脸库，external_fields 用于内嵌姓名等元数据
    body = CreateFaceSetReq(
        face_set_name=FACE_SET_NAME,
        face_set_capacity=10000,
        external_fields={"fullname": TypeInfo(type="string")},
    )
    request = CreateFaceSetRequest(body=body)
    try:
        response = client.create_face_set(request)
        print("Face set created:", response.to_json_object())
    except exceptions.ClientRequestException as e:
        print("Error code:", e.status_code)
        print("Error message:", e.error_msg)


if __name__ == "__main__":
    main()
