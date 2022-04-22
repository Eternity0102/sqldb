import random

from dbConnect import *


def test():
    # 1. 连接数据库
    db = SqlDB('192.168.200.10', 3306, 'test', 'root', '123456')
    print('数据库连接成功')

    # 2.表的操作

    # 2.1查询表
    showtable = db.show_table()
    print('获取表中的内容成功', showtable)

    # 2.2 创建表（需结合4.1一起使用）
    newTable = db.create_table('test1')
    # 4.1设置表字段
    newTable.primary_key = 'id'
    newTable.zerofill = ['age']
    newTable.engine = 'innodb'
    newTable.set_field({
        'id': 'int',
        'name': 'varchar(20)',
        'age': 'int(2)',
        'sex': 'varchar(2)',
        'addr': 'varchar(30)',
        'city': 'varchar(20)',
        'au_name': 'int',
        'au_id':'int',
        'engine': 'innodb',
    })
    print('创建表mytable2后获取表内容：', db.show_table())

    # 2.3删除表
    # 为避免后面代码运行出错，此处先注释掉
    # db.drop_table('mytable2')
    # print('删除表mytable2后获取表内容：', db.show_table())

    # 2.4绑定已存在的表，相当于获取一个表对象
    alterExistTable = db.alter_table('test1')

    # 2.5获取表的字段名
    getField = newTable.get_field()
    print('获取到的表的字段:', getField)

    # 3.增删改查操作

    # 此处的查询如果所有的条件都使用上不一定能成功，未进行深度测试
    # 3.1查询表中内容
    # 3.1.1.1 绑定一个表，获取一个表对象
    bindTable = db.get_fromTable('test1')
    a = 0
    if a:
        # 3.1.1.2 获取当前绑定的表
        bindTableName = bindTable.get_table()
        print('bindTable当前绑定的表为：', bindTableName)
        # 3.1.2 使用原生sql语句查询数据库中表的信息
        source_result = bindTable.getBySource('select * from test1')
        print("用原生sql语句查询成功:", source_result.get())
        # 3.1.3.1 绑定查询集条件
        bindTable.select = ('name', 'age', 'addr', 'city')  # 用于查询集获取的字段
        bindTable.having = True  # 使用having进行筛选，不使用where，默认True
        # bindTable.having = False #使用where进行筛选，不使用having
        bindTable.filter = {'age': '66', 'city': '北京'}  # 查询筛选字段,可省略
        bindTable.group_by = 'city'  #
        bindTable.order_by = ('age', 'desc')  # 对查询结果进行排序
        bindTable.limit = 3  # 限制获取查询集条数
        # 3.1.3.2 利用绑定好的查询集条件直接查询
        method_result = bindTable.get_data()
        print("用封装方法查询成功:", method_result.get())

    # 3.2向表中插入数据

    # 3.2.1插入单行数据
    bindTable.name = '李清照'
    bindTable.age = '90'
    bindTable.sex = random.choice(['女', '男'])
    bindTable.addr = '上海滩'
    bindTable.city = '未知'
    bindTable.create()  # 提交当前绑定的属性内容到数据库
    # 上方创建结束，下方开始查询
    bindTable.select = '*'
    print('插入数据后获取表中内容', bindTable.get_data().get())
    # 3.2.2 插入多行数据
    for i in range(20):
        bindTable.name = '李清照%s号' % i
        bindTable.age = 87 + i
        bindTable.sex = random.choice(['女', '男'])
        bindTable.addr = '上海%s滩' % i
        bindTable.city = '未知%s' % i
        bindTable.create()
    # 上方创建结束，下方开始查询
    bindTable.select = '*'
    print('插入多行数据后获取表中内容', bindTable.get_data().get())

    # 3.3 修改表中数据
    bindTable.name = '王维'
    bindTable.age = 100
    bindTable.where_name = '李清照6号'
    bindTable.update()  # 提交当前绑定的属性内容到数据库修改
    # 上方属性设置结束，下方开始查询
    bindTable.select = '*'
    bindTable.having = False
    bindTable.filter = {'name': '王维'}
    print('插入多行数据后获取表中内容', bindTable.get_data().get())

    # 3.4 删除表中数据
    bindTable.where_sex = '女'
    bindTable.where_name = '李清照12号'
    bindTable.delete()  # 提交当前要修改的内容

    # 4.1 创建新表设置字段
    # 在2.2中结合4.1已经设置过了

    # 4.2 向已有表中添加字段
    newTable.add_field('country', 'varchar(20)',after='city')
    print('添加字段后的字段名列表：', newTable.get_field())

    # 4.3 向已有表中删除字段
    newTable.drop_field('city')
    print('删除字段后的字段名列表：', newTable.get_field())

    # 4.4 向已有表中设置默认约束
    newTable.default('country', '首都北京')

    # 4.5 向已有表中设置非空约束
    newTable.not_null('name')

    # 4.6 设置普通索引
    newTable.set_index('id')
    newTable.set_index('name', 'name_index')
    # 上方传参(索引字段 , 设置索引名)，索引名可以不传参，默认以字段名作为索引名
    print("获取设置的普通索引：", newTable.get_index())

    # 4.7 删除普通索引,两种方式，下同
    newTable.drop_index('id')
    print("获取删除后的普通索引：", newTable.get_index())
    newTable.drop_index('name_index')
    print("获取删除后的普通索引：", newTable.get_index())

    # 4.8 创建唯一索引
    newTable.set_unique('id', 'id_unique_name')
    print("获取创建的唯一索引：", newTable.get_unique())

    # 4.9 删除唯一索引
    newTable.drop_unique(newTable.get_unique()['id'])
    print("获取删除后的唯一索引：", newTable.get_unique())

    # 4.10 在已有表中设置主键索引
    # 创建表时已经创建主键索引
    priKey = 1
    if not priKey:
        newTable.set_primaryKey('id')
        print("获取创建的主键索引：", newTable.get_primaryKey())

    # 4.11 在已有表中设置自增长状态
    auto_incr = 1
    if not auto_incr:
        newTable.set_autoIncrement('id')
    # 设置过主键则不需要再进行设置

    # 4.12 删除主键索引
    print("获取删除前的主键索引：", newTable.get_primaryKey())
    newTable.drop_primaryKey('id')
    print("获取删除后的主键索引：", newTable.get_primaryKey())

    # 4.13 添加外键索引
    foreignobj = newTable.set_foreignKey()  # 获取设置外键对象
    foreignobj.self_field = 'au_id'
    foreignobj.foreign_table = 'test2'
    foreignobj.foreign_field = 'id'
    foreignobj.cascade = 'cascade'
    foreignobj.on_delete = True
    foreignobj.on_update = True
    foreignobj.save()

    # 4.14 通过两种方式获取外键
    print('获取设置后的外键:', newTable.get_foreignKey())

    # 4.15 删除外键
    newTable.drop_foreignKey('au_id')
    print('获取删除后的外键索引:', newTable.get_foreignKey())

    # 4.16 内连接查询
    newTable.inner_connect({
        'sheng': 's_name',
        'city': 'c_name',
        'xian': 'x_name',
    },
        {
            'city': 'sheng.s_id=city.cfather_id',
            'xian': 'city.c_id=xian.xfather_id',
        }
    )

    # 4.17 左连接查询
    newTable.left_connect({
        'sheng': 's_name',
        'city': 'c_name',
        'xian': 'x_name',
    },
        {
            'city': 'sheng.s_id=city.cfather_id',
            'xian': 'city.c_id=xian.xfather_id',
        }
    )

    # 4.18 右连接查询
    newTable.right_connect({
        'sheng': 's_name',
        'city': 'c_name',
        'xian': 'x_name',
    },
        {
            'city': 'sheng.s_id=city.cfather_id',
            'xian': 'city.c_id=xian.xfather_id',
        }
    )

    # 5.表的授权操作

    # 5.1 获取授权信息
    print(db.show_grant(('user', 'host')))

    # 5.2 添加授权表
    db.add_grant('qgd', '192.168.200.1', '*')
    print(db.show_grant(('user', 'host')))

    # 5.3 删除授权表
    db.drop_grant('qgd', '192.168.200.1')
    print(db.show_grant(('user', 'host')))



if __name__ == '__main__':
    test()
