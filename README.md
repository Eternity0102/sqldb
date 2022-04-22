# 基于PYTHON语言pymysql库封装开源项目使用说明

```
文档阅读说明：
	该文档对应的dbConnect.py文件基于python库pymysql编写，内部封装了基本的mysql语句，初略封装部分功能不完善，可能出现部分操作出现报错的情况，有能力或使用的可以拿去爆改，仅用于个人学习测试
```



## 1.连接数据库

1. 通过创建对象传参方式直接获取数据库连接对象

   ```python
    db = SqlDB('192.168.200.10', 3306, 'webdb', 'root', '123456')
   ```

2. 运行后通过输入方式获取数据库连接对象

   ```python
    db = SqlDB()
   #终端输入
   #请输入数据库服务器IP地址：192.168.200.10
   #请输入端口号：3306
   #输入连接数据库名：webdb
   #输入用户名：root
   #输入密码：123456
   #请输入字符编码：utf8
   ```







## 2.表的操作

### 1.查询表

```python
showtable = db.show_table()
print(showtable)
```

### 2.创建表

只能获取一个表对象，需要进行设置字段操作才能在数据库中生成表

```python
newTable = db.create_table('test1')#创建一个名为test1的新表，获取一个新表对象，可对该表进行操作
```

### 3.删除表

```python
db.drop_table('test1')
```

### 4.绑定表

绑定一个表对象，对表进行操作

```python
bindTable = db.alter_table()
```

### 5.获取表的字段名

```python
getField = newTable.get_field()
print('获取到的表的字段:', getField)
```





## 3.增删改查操作(CRUD)

```mysql
对象.字段名可用于对当前属性的值进行设置
对象.where_字段名当做于查询条件
所有的表中操作都提供了'where_字段名'
例如：
    bindTable.name = '王维'
    bindTable.age = 100
    bindTable.where_name = '李清照6号'
相当于sql语句：
	update test1 set name='王维',age=100 where name='李清照'
```



### 1.查询表中内容

1. 获取数据库中表的 对象操作

   1. 绑定一个表，获取一个表对象

      ```python
      bindTable = db.get_fromTable('test')
      ```

   2. 获取当前绑定的表

      ```python
      bindTableName = bindTable.get_table()
      print('当前绑定的表为：', bindTableName)
      ```

2. 使用原生sql语句查询数据库中表的信息

   ```python
   source_result = bindTable.getBySource('select * from test')
   print("用原生语句查询成功:", source_result.get())
   ```

3. 用绑定对象的函数提供的方法查询

   1. 绑定查询集条件

      ```python
      bindTable.select = ('name','age','addr')#用于查询集获取的字段
      bindTable.having = True #使用having进行筛选，不使用where，默认True
      #bindTable.having = False #使用where进行筛选，不使用having
      bindTable.filter = {'age':'66','city':'北京'}#查询筛选字段,可省略
      bindTable.group_by = 'city'#
      bindTable.order_by = ('age','desc')#对查询结果进行排序
      bindTable.limit = 3 #限制获取查询集条数
      ```

   2. 利用绑定好的查询集条件直接查询

      ```python
      method_result = bindTable.get_data()
      print("用封装方法查询成功:", method_result.get())
      ```

### 2.向表中插入记录

当创建表对象后，数据表中所有的字段都会被映射为一个对象属性，直接通过**对象.字段名**可以直接操作当前字段

1. 插入单行数据

   ```python
   bindTable.name = '李清照'
   bindTable.age = '90'
   bindTable.sex = random.choice(['女', '男'])
   bindTable.country = '中国古代'
   bindTable.province = '未知'
   bindTable.create()#提交当前绑定的属性内容到数据库
   ```

2. 插入多行数据

   可使用循环遍历某个列表的方式插入数据，或采用下列方式批量插入测试数据

   ```python
       for i in range(20):
           bindTable.name = '李清照' + str(i * 3) + '号'
           bindTable.age = '90'
           bindTable.sex = random.choice(['女', '男'])
           bindTable.country = '中国古代'
           bindTable.province = '未知'
           bindTable.create()
   ```

### 3.修改表记录

直接修改表中数据，通过**对象.字段名**操作字段

```python
bindTable.name = '王维'
bindTable.age = 100
bindTable.where_name = '李清照6号'
bindTable.update()#提交当前绑定的属性内容到数据库修改
```

### 4.删除表记录

```python
bindTable.where_sex = '女'
bindTable.where_name = '李清照12'
bindTable.delete()#提交当前要修改的内容
```









## 4.创建/修改表的操作

### 1. 创建新表设置字段

```python
newTable = db.create_table('test1')
newTable.engine = 'innodb'#默认是innodb，可以设置其他存储引擎
newTable.set_field({
    'id': 'int',
    'name': 'varchar(20)',
    'age': 'int(2)',
    'sex': 'varchar(2)',
    'addr': 'varchar(30)',
    'city': 'varchar(20)',
    'au_name': 'varchar(25)',
    'au_id':'int',
})#传入一个键值对设置表字段以及数据类型，执行完后直接提交到数据库
```

可以在创建表之前设置主键和zerofill属性，在执行set_field方法之前

```python
newTable.primary_key = 'id'
newTable.zerofill = ['id','age','money']#必须是一个列表
```

若修改表则获取对象即可

```python
newTable = db.alter_table('test1')
```

### 2.向已有表中添加字段

```python
newTable.add_field('country', 'varchar(20)',after='city')#在city之后添加字段
print('添加字段后的字段名列表：', newTable.get_field())
```

### 3.向已有表中删除字段

```python
newTable.drop_field('city')
print('删除字段后的字段名列表：', newTable.get_field())
```

### 4.向已有表中设置默认约束

```python
newTable.default('country', '首都北京')
```

### 5.向已有表中设置非空约束

```python
newTable.not_null('name')
```

### 6.设置普通索引

```python
newTable.set_index('id')
newTable.set_index('name', 'name_index')
# 上方传参(索引字段 , 设置索引名)，索引名可以不传参，默认以字段名作为索引名
print("获取设置的普通索引：", newTable.get_index())
```

### 7.删除普通索引

```python
newTable.drop_index('id')
print("获取删除后的普通索引：", newTable.get_index())
newTable.drop_index('name_index')
print("获取删除后的普通索引：", newTable.get_index())
```

### 8.创建唯一索引

```python
newTable.set_unique('id', 'id_unique')
# 上方传参(索引字段 , 设置索引名)，索引名可以不传参，默认以字段名作为索引名
print("获取创建的唯一索引：", newTable.get_unique())
```

### 9.删除唯一索引

```python
newTable.drop_unique('id_unique')
print("获取删除后的唯一索引：", newTable.get_unique())
```

### 10.在已有表中设置主键索引

```python
newTable.set_primaryKey('id')
print("获取创建的主键索引：", newTable.get_primaryKey())
```

### 11.在已有表中设置自增长状态

```python
newTable.set_autoIncrement('id')
#设置过主键则不需要再进行设置
```

### 12.删除主键索引

```python
newTable.drop_primaryKey('id')
print("获取删除后的主键索引：", newTable.get_primaryKey())
```

### 13.添加外键索引

需先获取一个对象，再进行属性设置，再提交

```python
foreignobj = newTable.set_foreignKey()
foreignobj.self_field = 'au_id'
foreignobj.foreign_table = 'author'
foreignobj.foreign_field = 'id'
foreignobj.casecade = True
foreignobj.update = True
foreignobj.save()
```

### 14.获取外键

```python
print('获取设置后的外键索引:', newTable.get_foreignKey())
```

### 15.删除外键

```python
newTable.drop_foreignKey('au_id')
print('获取删除后的外键索引:', newTable.get_foreignKey())
```

### 16.内连接查询

```python
newTable.inner_connect({
'sheng':'s_name',
'city':'c_name',
'xian':'x_name',
},
{
'city':'sheng.s_id=city.cfather_id',
'xian':'city.c_id=xian.xfather_id',
}
)
```

### 17.左连接查询

```python
newTable.left_connect({
    'sheng':'s_name',
    'city':'c_name',
    'xian':'x_name',
},
    {
        'city':'sheng.s_id=city.cfather_id',
        'xian':'city.c_id=xian.xfather_id',
    }
)
```

### 18.右连接查询

```python
newTable.right_connect({
'sheng':'s_name',
'city':'c_name',
'xian':'x_name',
},
{
'city':'sheng.s_id=city.cfather_id',
'xian':'city.c_id=xian.xfather_id',
}
)
```







## 5.表的授权操作

### 1.获取授权信息

```python
print(db.show_grant(('user','host')))
```

### 2.添加授权表

```python
db.add_grant('qgd','192.168.200.1','*')
print(db.show_grant(('user','host')))
```

### 3.删除授权表

```python
db.drop_grant('qgd','192.168.200.1')
print(db.show_grant(('user','host')))
```

