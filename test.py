import random

from dbConnect import *



def index():
    # db = pymysql.connect(host='192.168.200.10', port=3306, database='webdb', user='root', password='123456')
    # cursor = db.cursor()
    # cursor.execute('show create table test1')
    print('#################################')
    # 连接数据库
    db = SqlDB('192.168.200.10', 3306, 'webdb', 'root', '123456')
    print('数据库连接成功')

    # 获取新表对象
    newTable = db.create_table('test1')
    print('获取新表对象成功')

    # 创建前设置主键
    newTable.primary_key = 'id'
    print('创建前设置主键成功')

    # 创建新表字段
    newTable.set_field({
        'id': 'int',
        'name': 'varchar(20)',
        'age': 'int',
        'addr': 'varchar(30)',
        'au_name': 'int',
    })
    print('获取到的表的字段:', newTable.get_field())
    #
    # # 向已有表中添加字段
    newTable.add_field('city', 'varchar(20)')
    print('添加字段后的字段名列表：', newTable.get_field())
    #
    # # 向已有表中删除字段
    newTable.drop_field('au_name')
    print('删除字段后的字段名列表：', newTable.get_field())
    #
    # # 向已有表中设置默认约束
    newTable.default('city', '贵阳')
    print('默认约束设置成功')
    #
    # # 向已有表中设置非空约束
    newTable.not_null('name')
    print('非空约束设置成功')
    #
    # # 设置普通索引
    newTable.set_index('id')
    newTable.set_index('name', 'name_index')
    print("获取设置的普通索引：", newTable.get_index())
    #
    # # 删除普通索引
    newTable.drop_index('id')
    print("获取删除后的普通索引：", newTable.get_index())
    newTable.drop_index('name_index')
    print("获取删除后的普通索引：", newTable.get_index())
    #
    # # 创建唯一索引
    newTable.set_unique('id', 'id_unique')
    print("获取创建的唯一索引：", newTable.get_unique())
    #
    # # 删除唯一索引
    newTable.drop_unique('id_unique')
    print("获取删除后的唯一索引：", newTable.get_unique())
    #
    # # 在已有表中设置主键索引
    newTable.set_primaryKey('id')
    print("获取创建的主键索引：", newTable.get_primaryKey())
    #
    # # 在已有表中设置自增长状态
    newTable.set_autoIncrement('id')
    print("自增长状态设置成功")
    #
    # # 删除主键索引
    newTable.drop_primaryKey('id')
    print("获取删除后的主键索引：", newTable.get_primaryKey())
    #
    # 获取一个新的对象添加字段
    tableobj = db.get_fromTable('test1')
    tableobj.add_field('au_id', 'int', after='city')
    #
    # # 添加外键索引，需先获取一个对象，再进行属性设置，再提交
    foreignobj = newTable.set_foreignKey()
    foreignobj.self_field = 'au_id'
    foreignobj.foreign_table = 'author'
    foreignobj.foreign_field = 'id'
    foreignobj.casecade = True
    foreignobj.update = True
    foreignobj.save()
    #
    # # 通过两种方式获取外键
    print('用创建表时候的对象获取设置后的外键索引:', newTable.get_foreignKey())
    # print('用新的对象时候的对象获取设置后的外键索引:', tableobj.get_foreignKey())
    #
    # # 删除外键
    newTable.drop_foreignKey('au_id')
    print('用新的对象时候的对象获取设置后的外键索引:', tableobj.get_foreignKey())

    #绑定查询表对象
    getdataobj = db.get_fromTable('test1')

    # 内连接查询
    getdataobj.inner_connect({
        'sheng':'s_name',
        'city':'c_name',
        'xian':'x_name',
    },
    {
        'city':'sheng.s_id=city.cfather_id',
        'xian':'city.c_id=xian.xfather_id',
    }
    )

    # 左连接查询
    getdataobj.left_connect({
        'sheng':'s_name',
        'city':'c_name',
        'xian':'x_name',
    },
    {
        'city':'sheng.s_id=city.cfather_id',
        'xian':'city.c_id=xian.xfather_id',
    }
    )

    # 右连接查询
    getdataobj.right_connect({
        'sheng':'s_name',
        'city':'c_name',
        'xian':'x_name',
    },
    {
        'city':'sheng.s_id=city.cfather_id',
        'xian':'city.c_id=xian.xfather_id',
    }
    )

    # 获取授权表
    print(db.show_grant(('user','host')))

    #添加授权表
    db.add_grant('qgd','192.168.200.1','*')
    print(db.show_grant(('user','host')))

    #删除授权表
    db.drop_grant('qgd','192.168.200.1')
    print(db.show_grant(('user','host')))



def crud():
    #  连接数据库
    db = SqlDB('192.168.31.126', 3306, 'webdb', 'root', '123456')
    print("连接成功")

    # 查询当前数据库中的表
    showtable = db.show_table()
    print(showtable)

    db.drop_table('test1')

    # 绑定表
    bindTable = db.get_fromTable('test')

    # 查询当前绑定的表
    bind_table = bindTable.get_table()
    print('当前绑定的表为：', bind_table)

    # 查询
    # 按sql语句查询
    source_result = bindTable.getBySource('select * from test')
    print("用原生语句查询成功:", source_result.get())

    # 用封装的方法查询
    bindTable.select = '*'
    bindTable.filter = {'city': '贵州'}
    method_result = bindTable.get_data()
    print("用封装方法查询成功:", method_result.get())

    # 插入数据
    for i in range(20):
        bindTable.name = '李清照' + str(i * 3) + '号'
        bindTable.age = '90'
        bindTable.sex = random.choice(['女', '男'])
        bindTable.country = '中国古代'
        bindTable.province = '未知'
        bindTable.create()

    # 修改
    # 修改数据
    bindTable.name = '王维'
    bindTable.age = 100
    bindTable.where_name = '李清照6号'
    bindTable.update()
    print('数据修改成功')

    # 删除数据
    bindTable.where_sex = '女'
    bindTable.where_name = '李清照12'
    bindTable.delete()
    print("删除数据成功")


if __name__ == '__main__':
    # crud()
    # index()
    SqlDB()