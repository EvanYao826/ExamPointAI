"""接口测试脚本 - 测试 M2 前 4 个接口"""
import requests

BASE = "http://localhost:8000/api/v1"


def test_all():
    print("=" * 50)
    print("考点通 M2 接口测试")
    print("=" * 50)

    # 1. 登录拿 token
    print("\n[1] 发送验证码...")
    r = requests.post(f"{BASE}/auth/sms/send", json={"phone": "13800000000"})
    print(f"    {r.status_code} - {r.json()}")

    print("\n[2] 登录...")
    r = requests.post(f"{BASE}/auth/sms/login", json={"phone": "13800000000", "code": "888888"})
    print(f"    {r.status_code} - {r.json()}")
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"    token: {token[:20]}...")

    # 2. GET /user/profile
    print("\n[3] GET /user/profile")
    r = requests.get(f"{BASE}/user/profile", headers=headers)
    print(f"    {r.status_code} - {r.json()}")

    # 3. PUT /user/profile
    print("\n[4] PUT /user/profile (更新昵称)")
    r = requests.put(f"{BASE}/user/profile", headers=headers, json={"nickname": "测试用户"})
    print(f"    {r.status_code} - {r.json()}")

    # 4. GET /school/list
    print("\n[5] GET /school/list")
    r = requests.get(f"{BASE}/school/list", headers=headers)
    print(f"    {r.status_code} - {r.json()}")

    print("\n[6] GET /school/list?name=示例")
    r = requests.get(f"{BASE}/school/list", params={"name": "示例"}, headers=headers)
    print(f"    {r.status_code} - {r.json()}")

    # 5. GET /school/{id}/majors
    print("\n[7] GET /school/1/majors")
    r = requests.get(f"{BASE}/school/1/majors", headers=headers)
    print(f"    {r.status_code} - {r.json()}")

    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)


if __name__ == "__main__":
    test_all()
