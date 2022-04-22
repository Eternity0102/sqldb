"""
author:@EternityGordon Qin
"""

import re
import pymysql


class _Handler:

    def tup_combine(self,tuples):
        # 形如(A),(B),(C)
        str1 = ''
        for value in tuples:
            str1 += '(%s),' % value
        return str1[:-1]

    def dic_combineAnd(self,dic):
        # 形如 A=a and B=b and C=c
        str1 = ''
        for key in dic:
            keyl = key.split(' ')
            valuel = dic[key].split(' ')
            if len(keyl)>1:
                if re.findall(r'\w+\(\w+\)',dic[key]) :
                    str1 += '"' + str(keyl[0]) + '" '+keyl[1]+ ' ' + str(dic[key]) + r' and '
                elif re.findall(r'\w+\(\w+\)',dic[key]):
                    str1 += str(valuel[0]) + '" ' + valuel[1] + '" ' + str(dic[key]) + r' and '
                else:
                    str1 += str(key) + ' "' + str(dic[key]) + r'" and '
            else:
                str1 += str(key) + r'="' + str(dic[key]) + r'" and '
        if "where_" in str1:
            return str1[:-5].replace("where_", "")
        return str1[:-5]

    def dic_combineComma(self,dic):
        str1 = ''
        for value in dic:
            str1 += str(value) + r'= "' + str(dic[value]) + r'",'
        return str1[:-1]


class _CudData(object):

    def __init__(self,db,table_name):
        self.__db = db
        self.__cursor = self.__db.cursor()
        self.__table_name = table_name
        self.select :tuple = ()
        self.having :bool = True
        self.filter : dict = {}
        self.group_by: str = ''
        self.order_by : tuple = ()
        self.limit : int = -1
        self.__cursor.execute('desc ' + self.__table_name)
        self.__vars : list = []
        data_cache = self.__cursor.fetchall()
        for data in data_cache:
            self.__vars.append(data[0])
            exec("self.%s = ''" % data[0])  # 让字符串变为变量赋值
            exec("self.where_%s = ''" % data[0])  # 让字符串变为变量赋值

    def __del__(self):
        try:
            self.__cursor.close()
        except :
            pass

    def __findfield(self):
        self.__cursor.execute('desc '+self.__table_name)
        self.__vars = []
        data_cache = self.__cursor.fetchall()
        for data in data_cache:
            self.__vars.append(data[0])

    def __sql_excuete(self,syntax):
        '''提供sql语句查询'''
        self.__cursor = self.__db.cursor()
        self.__cursor.execute(syntax)
        self.__db.commit()

    def __select_connect(self, method, field_dic, condition_dic):
        syntax = ''
        for field in field_dic:
            syntax += field+'.'+field_dic[field]+','
        syntax = syntax[:-1]
        syntax = 'select %s from %s' % (syntax, self.__table_name)
        for condition in condition_dic:
            syntax += ' %s join '%method + condition + ' on ' + condition_dic[condition]
        self.__cursor.execute(syntax)

    def getBySource(self, syntax):
        '根据原生sql语句查询'
        self.__sql_excuete(syntax)
        retcur = self.__cursor.fetchall()
        return _HandlerData(retcur)

    def get_data(self):
        '''封装查询'''
        L = []
        #检测having字段
        if self.filter and type(self.filter) is dict:
            having_str = _Handler().dic_combineAnd(self.filter)
        elif self.filter and type(self.filter) is str:
            having_str = self.filter
        else :
            having_str = ''
        #检测order_by字段
        if self.order_by and type(self.order_by) is tuple:
            order_by_str = ' '.join(self.order_by)
        elif self.order_by and type(self.order_by) is not tuple:
            raise Exception("order_by 错误，应该传入一个元祖，第一个参数为排序字段，第二个参数为排序方式")
        else :
            order_by_str = ""
        #检测limit字段
        syntax = "select %s from %s %s %s %s %s"%(
            ','.join(self.select),
            self.__table_name,
            '%s'%('%s%s'% (' having ' if self.having else " where ",
                             having_str if  having_str  else "" )) if self.filter else "",
            'group by %s' % self.group_by if self.group_by else "",
            'order by %s ' % order_by_str if order_by_str else "",
            'limit %s' % self.limit if self.limit!=-1 else "",
        )
        self.__cursor.execute(syntax)
        self.retcur = self.__cursor.fetchall()
        for line in self.retcur:
            L.append(line)
        return _HandlerData(L)

    def get_table(self):
        '''获取当前表'''
        return self.__table_name

    def get_field(self):
        '''获取字段'''
        self.__findfield()
        return self.__vars

    def create(self):
        '''提交当前数据'''
        field_name = ''     #字段名
        value_name = ''     #字段名对应的值名
        for var in self.__vars:
            var_value = str(eval("self.%s"%var))
            if not var_value:
                continue
            else:
                field_name += var + ','
                value_name += '"'+var_value + '",'
        field_name = field_name[:-1]
        value_name = value_name[:-1]
        syntax = 'insert into %s(%s) values(%s)'%(self.__table_name,
                field_name,value_name
        )
        self.__sql_excuete(syntax)
        self.__init__(self.__db,self.__table_name)

    def update(self):
        set_dic = {}
        where_dic = {}
        for var in self.__vars:
            #获取字段名的变量值
            set_value = str(eval("self.%s" % var))
            # 获取带where_的变量值
            where_value = str(eval("self.where_%s" % var))
            if set_value :
                set_dic[var]=set_value
            if where_value:
                where_dic["where_"+var] = where_value
        set_value = _Handler().dic_combineComma(set_dic)
        where_value = _Handler().dic_combineAnd(where_dic)
        syntax = "update %s set %s where %s"%(self.__table_name,set_value,where_value)
        self.__sql_excuete(syntax)
        self.__init__(self.__db, self.__table_name)

    def delete(self):
        where_dic = {}
        for var in self.__vars:
            where_value = str(eval("self.where_%s" % var))
            if where_value:
                where_dic["where_" + var] = where_value
        where_value = _Handler().dic_combineAnd(where_dic)
        syntax = 'delete from %s where %s' % (self.__table_name,where_value)
        self.__sql_excuete(syntax)
        self.__init__(self.__db,self.__table_name)

    # 内连接查询
    def inner_connect(self,field_dic,condition_dic):
        self.__select_connect('inner',field_dic,condition_dic)

    # 左连接查询
    def left_connect(self,field_dic,condition_dic):
        self.__select_connect('left', field_dic, condition_dic)

    # 右连接查询
    def right_connect(self,field_dic,condition_dic):
        self.__select_connect('right', field_dic, condition_dic)



class _HandlerData(object):
    def __init__(self,retcur):
            self.retcur = retcur

    def get(self,num=-1):
        L = []
        if num != -1:
            if num<len(self.retcur):
                for linenum in range(num):
                    L.append(self.retcur[linenum])
            else:
                raise IndexError()
        else:
            total = 0
            for line in self.retcur:
                if total == 10:
                    break
                L.append(line)
                total+=1
        return L


class _AlterTable(object):
    def __init__(self,db,table_name):
        self.__table_name = table_name
        self.__db = db
        self.__cursor = self.__db.cursor()

    def __del__(self):
        try:
            self.__cursor.close()
        except :
            pass

    def __get_fieldType(self,field):
        self.__cursor.execute('desc '+self.__table_name)
        for cur in self.__cursor.fetchall():
            if cur[0]==field:
                return cur[1]
        return ''

    def __findfield(self):
        self.__cursor.execute('desc '+self.__table_name)
        self.__vars = []
        data_cache = self.__cursor.fetchall()
        for data in data_cache:
            self.__vars.append(data[0])

    def get_field(self):
        self.__findfield()
        return self.__vars

    def add_field(self,field,field_type,first='',after=''):
        if first:
            last = ' first %s'%first
        elif after:
            last = ' after %s'%after
        else:
            last = ''
        syntax = 'alter table %s add %s %s %s;'%(self.__table_name,field,field_type,last)
        self.__cursor.execute(syntax)

    def drop_field(self,field):
        syntax = 'alter table %s drop %s'%(self.__table_name,field)
        self.__cursor.execute(syntax)

    def default(self,field,set_value):
        field_type = self.__get_fieldType(field)
        if field_type:
            syntax = 'alter table %s modify %s %s default "%s"'%(self.__table_name,field,field_type,set_value)
            self.__cursor.execute(syntax)
        else:
            raise

    def not_null(self,field):
        field_type = self.__get_fieldType(field)
        if field_type:
            syntax = 'alter table %s modify %s %s not null'%(self.__table_name,field,field_type)
            self.__cursor.execute(syntax)
        else:
            raise

    def set_index(self,field,name=''):
        name = name if name else field
        syntax = 'create index '+ name + ' on '+ self.__table_name +'(%s)'%field
        self.__cursor.execute(syntax)

    def get_index(self):
        dic = {}
        self.__cursor.execute('show index from '+self.__table_name)
        for cur in self.__cursor.fetchall():
            # 字段名:索引名
            if cur[1]:
                dic[cur[4]]=cur[2]
        return dic

    def drop_index(self,index_name):
        syntax = 'drop index ' + index_name + ' on ' + self.__table_name
        self.__cursor.execute(syntax)

    def set_unique(self,field,name=''):
        name = name if name else field
        syntax = 'create unique index ' + name + ' on ' + self.__table_name + '(%s)'%field
        self.__cursor.execute(syntax)

    def get_unique(self):
        dic = {}
        self.__cursor.execute('show index from '+self.__table_name)
        for cur in self.__cursor.fetchall():
            #字段名:索引名
            if not cur[1] and cur[2]!='PRIMARY':
                dic[cur[4]]=cur[2]
        return dic

    def drop_unique(self,unique_name):
        syntax = 'drop index ' + unique_name + ' on ' + self.__table_name
        self.__cursor.execute(syntax)

    def set_primaryKey(self,field,auto_increment=True):
        syntax = 'alter table '+self.__table_name+' add primary key(%s)'%field
        print(syntax)
        self.__cursor.execute(syntax)

    def set_autoIncrement(self,field):
        field_type = self.__get_fieldType(field)
        syntax = 'alter table %s change %s %s %s auto_increment'%(
            self.__table_name,field,field,field_type
        )
        self.__cursor.execute(syntax)

    def get_primaryKey(self):
        self.__cursor.execute('show index from '+self.__table_name)
        for cur in self.__cursor.fetchall():
            if cur[2]=='PRIMARY':
                return cur[4]
        else:
            return ''

    def drop_primaryKey(self,modifyNull=False):
        self.__cursor.execute('desc '+self.__table_name)
        for cur in self.__cursor.fetchall():
            if cur[3]=='PRI':
                field = cur[0]
                field_type = cur[1]
                break
        else:
            raise Exception('表中没有添加主键索引primary key')
        syntax = 'alter table '+self.__table_name+' modify '+field+' '+field_type
        self.__cursor.execute(syntax)
        syntax = 'alter table '+self.__table_name+' drop primary key'
        self.__cursor.execute(syntax)
        if modifyNull:
            syntax = 'alter table '+self.__table_name+' modify '+field+' '+field_type+' default null'
            self.__cursor.execute(syntax)

    def set_foreignKey(self):
        class InnerClassForeignKey:
            def __init__(self,db,table_name):
                self.self_field : str = ''
                self.foreign_table : str = ''
                self.foreign_field : str = ''
                self.on_delete : bool = False
                self.on_update : bool = False
                self.cascade : str = 'cascade'
                self.__cursor = db.cursor()
                self.__table_name = table_name

            def __del__(self):
                try:
                    self.__cursor().close()
                except :
                    pass

            def save(self):
                syntax = 'alter table %s add foreign key(%s) '%(self.__table_name,self.self_field)
                syntax += 'references %s(%s) '%(self.foreign_table,self.foreign_field)
                syntax += 'on update %s '%self.cascade if self.on_update else ''
                syntax += 'on delete %s '%self.cascade if self.on_update else ''
                print(syntax)
                self.__cursor.execute(syntax)
        return InnerClassForeignKey(self.__db,self.__table_name)

    def get_foreignKey(self):
        L = []
        self.__cursor.execute('show create table '+self.__table_name)
        curs = self.__cursor.fetchall()
        show = curs[0][1]
        key_name = [m.group(2) for m in re.finditer('(CONSTRAINT `)(\w+)(`)', show)]
        key_field = [m.group(2) for m in re.finditer('(FOREIGN KEY \(`)(\w+)(`\))', show)]
        references = [m.group(2) for m in re.finditer('(REFERENCES )(`.*`\))', show)]
        for num in range(len(references)):
            references[num] = references[num].replace('`', '').replace(' ', '')
        if len(key_name) == len(key_field) == len(references):
            for num in range(len(key_name)):
                #           外键名           外键字段      外键表（字段名）
                L.append([key_name[num], key_field[num], references[num]])
            L.sort()
        return L

    def drop_foreignKey(self,field='',key_name=''):
        if key_name:
            key_name = key_name
        else:
            key_list = self.get_foreignKey()
            for key in key_list:
                if key[1]==field:
                    key_name = key[0]
                    break
            else:
                str = '字段%s未关联外键' % field
                raise Exception(str)
        syntax = 'alter table %s drop foreign key %s' % (self.__table_name, key_name)
        self.__cursor.execute(syntax)


class _NewTable(_AlterTable):

    def __init__(self,db,table_name):
        super().__init__(db,table_name)
        self.primary_key: str = ''
        self.zerofill: list = []
        self.__table_name = table_name
        self.__db = db
        self.__cursor = self.__db.cursor()
        self.engine: str = 'innodb'

    def set_field(self,field_dic):
        if self.zerofill:
            if type(self.zerofill) is not list:
                raise TypeError(self.zerofill)
        var = ''
        engine = ''
        for field in field_dic:
            zerofill = field if field in self.zerofill else ''
            auto_increment = ' primary key auto_increment' if self.primary_key==field else ''
            var += field + ' ' + field_dic[field]+auto_increment+(' zerofill '
                if zerofill else '')+', '
        var = var[:-2]
        syntax = 'create table %s(%s) %s'%(self.__table_name,var,'engine="%s"'%self.engine)
        print(syntax)
        self.__cursor.execute(syntax)


class SqlDB(object):
    '''
    主要控制类，用于访问数据库
    '''
    def __init__(self,ipaddr='',port=0,dbname='',user='',password='',charset='utf8'):
        if ipaddr and port and dbname and user and password:
            self.ipaddr = ipaddr
            self.port = port
            self.__dbname = dbname
            self.user = user
            self.password = password
            self.charset = charset
        else :
            self.ipaddr = input("请输入数据库服务器IP地址：")
            self.port = input("请输入端口号：")
            self.__dbname = input("输入连接数据库名：")
            self.user = input("输入用户名：")
            self.password = input("输入密码：")
            self.charset = input("请输入字符编码：")
        self.__connect()

    def __del__(self):
        try:
            self.__cursor.close()
            self.__db.close()
        except Exception:
            pass

    def __connect(self):
        hostdic = {
            'host':self.ipaddr,
            'port':int(self.port),
            'user':self.user,
            'password':self.password,
            'database':self.__dbname,
            'charset':self.charset,
        }
        self.__db = pymysql.connect(**hostdic)
        self.__cursor = self.__db.cursor()

    def get_fromTable(self,table_name):
        self.__table_name = table_name
        return _CudData(self.__db,self.__table_name)

    def show_table(self):
        '''获取所有表'''
        self.__cursor.execute('show tables')
        return self.__cursor.fetchall()

    def create_table(self,table_name):
        return _NewTable(self.__db,table_name)

    def drop_table(self,table_name):
        syntax = 'drop table '+ table_name
        self.__cursor.execute(syntax)

    def alter_table(self,table_name):
        return _AlterTable(self.__db,table_name)

    def show_grant(self,field_set):
        L = []
        syntax = 'select '+','.join(field_set)+' from mysql.user'
        self.__cursor.execute(syntax)
        for cur in self.__cursor.fetchall():
            L.append(cur)
        return L

    def add_grant(self,user,permission_ip='%',permit_table='*'):
        syntax = 'grant all privileges on %s.%s to "%s"@"%s" with grant option'%(
            self.__dbname,permit_table,user,permission_ip
        )
        self.__cursor.execute(syntax)

    def drop_grant(self,user,permission_ip):
        syntax = 'drop user "%s"@"%s"'%(user,permission_ip)
        self.__cursor.execute(syntax)



















