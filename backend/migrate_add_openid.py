"""迁移：给 user 表添加 openid 字段"""
import pymysql

conn = pymysql.connect(host='localhost', user='root', password='123456', database='exam_point')
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE `user` ADD COLUMN `openid` VARCHAR(100) UNIQUE COMMENT '微信openid' AFTER `phone`")
    conn.commit()
    print('openid 字段添加成功')
except Exception as e:
    if 'Duplicate column' in str(e):
        print('openid 字段已存在')
    else:
        print(f'错误: {e}')
finally:
    conn.close()
