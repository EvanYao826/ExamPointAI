"""M2 接口测试"""
import requests

BASE = "http://localhost:8000/api/v1"


def login():
    """登录并返回 headers"""
    requests.post(f"{BASE}/auth/sms/send", json={"phone": "13800000000"})
    r = requests.post(f"{BASE}/auth/sms/login", json={"phone": "13800000000", "code": "888888"})
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_all():
    headers = login()
    print("登录成功\n")

    # 用户信息
    print("[1] GET /user/profile")
    r = requests.get(f"{BASE}/user/profile", headers=headers)
    print(f"    {r.status_code} {r.json()}")

    print("[2] PUT /user/profile")
    r = requests.put(f"{BASE}/user/profile", headers=headers, json={"nickname": "测试用户"})
    print(f"    {r.status_code} {r.json()}")

    # 学校专业
    print("[3] GET /school/list")
    r = requests.get(f"{BASE}/school/list", headers=headers)
    print(f"    {r.status_code} {r.json()}")

    print("[4] GET /school/1/majors")
    r = requests.get(f"{BASE}/school/1/majors", headers=headers)
    print(f"    {r.status_code} {r.json()}")

    # 科目
    print("[5] GET /subject/list")
    r = requests.get(f"{BASE}/subject/list", headers=headers)
    print(f"    {r.status_code} {r.json()}")

    print("[6] POST /user/subjects")
    r = requests.post(f"{BASE}/user/subjects", headers=headers, json={"subject_ids": [1, 5]})
    print(f"    {r.status_code} {r.json()}")

    # 题库
    print("[7] GET /bank/public")
    r = requests.get(f"{BASE}/bank/public", headers=headers)
    print(f"    {r.status_code} {r.json()}")

    print("[8] GET /bank/mine")
    r = requests.get(f"{BASE}/bank/mine", headers=headers)
    print(f"    {r.status_code} {r.json()}")

    print("\n全部完成")


if __name__ == "__main__":
    test_all()
