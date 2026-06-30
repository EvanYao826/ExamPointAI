"""M2 全部接口测试（16个）"""
import os

import pytest
import requests

BASE = "http://localhost:8000/api/v1"


def login():
    """登录并返回 headers"""
    requests.post(f"{BASE}/auth/sms/send", json={"phone": "13800000000"})
    r = requests.post(f"{BASE}/auth/sms/login", json={"phone": "13800000000", "code": "888888"})
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_all():
    if os.getenv("RUN_LIVE_API_TESTS") != "1":
        pytest.skip("设置 RUN_LIVE_API_TESTS=1 后，对已启动的 localhost:8000 执行接口联调")

    headers = login()
    print("登录成功\n")

    tests = [
        # 认证
        ("POST /auth/sms/send", "POST", "/auth/sms/send", {"json": {"phone": "13800000000"}}),
        ("POST /auth/sms/login", "POST", "/auth/sms/login", {"json": {"phone": "13800000000", "code": "888888"}}),
        # 用户
        ("GET /user/profile", "GET", "/user/profile", {}),
        ("PUT /user/profile", "PUT", "/user/profile", {"json": {"nickname": "测试用户"}}),
        # 学校
        ("GET /school/list", "GET", "/school/list", {}),
        ("GET /school/1/majors", "GET", "/school/1/majors", {}),
        # 科目
        ("GET /subject/list", "GET", "/subject/list", {}),
        ("POST /user/subjects", "POST", "/user/subjects", {"json": {"subject_ids": [1, 5]}}),
        # 题库
        ("GET /bank/public", "GET", "/bank/public", {}),
        ("GET /bank/mine", "GET", "/bank/mine", {}),
        ("GET /bank/1", "GET", "/bank/1", {}),
        # 题目
        ("GET /question/next", "GET", "/question/next", {"params": {"bank_id": 1}}),
        ("POST /question/submit", "POST", "/question/submit", {"json": {"question_id": 1, "user_answer": "A", "cost_time": 10}}),
        ("GET /question/1/analysis", "GET", "/question/1/analysis", {}),
        # 错题
        ("GET /wrong/list", "GET", "/wrong/list", {}),
        ("GET /wrong/count", "GET", "/wrong/count", {}),
    ]

    for name, method, path, kwargs in tests:
        r = requests.request(method, f"{BASE}{path}", headers=headers, **kwargs)
        status = "PASS" if r.status_code == 200 else "FAIL"
        print(f"[{status}] {name} -> {r.status_code}")

    print("\nM2 全部 16 个接口测试完成")


if __name__ == "__main__":
    test_all()
