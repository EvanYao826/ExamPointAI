"""迁移：phone 字段允许为空"""
import pymysql

conn = pymysql.connect(host='localhost', user='root', password='123456', database='exam_point')
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE `user` MODIFY COLUMN `phone` VARCHAR(20) NULL COMMENT '手机号'")
    conn.commit()
    print('phone 字段已改为允许为空')
except Exception as e:
    print(f'错误: {e}')
finally:
    conn.close()
