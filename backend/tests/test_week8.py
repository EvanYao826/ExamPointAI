"""第八周接口测试：排行榜 + 统计"""
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

    # 先获取下一题，确认 bank_id 和可用题目
    r = requests.get(f"{BASE}/question/next", headers=headers, params={"bank_id": 1})
    if r.status_code == 200:
        q = r.json()
        print(f"下一题: id={q['id']}, bank_id={q['bank_id']}")
    else:
        print(f"获取下一题失败: {r.status_code} {r.text}")
        return

    # 答这道题
    print("\n--- 答题产生数据 ---")
    r = requests.post(f"{BASE}/question/submit", headers=headers, json={
        "question_id": q["id"],
        "user_answer": "A",
        "cost_time": 10,
    })
    print(f"[{'PASS' if r.status_code == 200 else 'FAIL'}] submit -> {r.status_code}")
    if r.status_code == 200:
        print(f"       {r.json()}")

    # 用正确的 subject_id=5 查询
    print("\n--- 排行榜 (subject_id=5) ---")
    for name, path in [("GET /ranking/daily", "/ranking/daily"), ("GET /ranking/weekly", "/ranking/weekly")]:
        r = requests.get(f"{BASE}{path}", headers=headers, params={"subject_id": 5})
        print(f"[{'PASS' if r.status_code == 200 else 'FAIL'}] {name} -> {r.status_code}")
        if r.status_code == 200:
            print(f"       {r.json()}")

    print("\n--- 学习统计 (subject_id=5) ---")
    r = requests.get(f"{BASE}/statistics/overview", headers=headers, params={"subject_id": 5})
    print(f"[{'PASS' if r.status_code == 200 else 'FAIL'}] GET /statistics/overview -> {r.status_code}")
    if r.status_code == 200:
        print(f"       {r.json()}")

    print("\n第八周接口测试完成")


if __name__ == "__main__":
    test_all()
