import mysql.connector

cnx = mysql.connector.connect(user='root', password='root',
                              host='127.0.0.1',
                              database='IAS')
query = "select * from SCHED;"
cursor = cnx.cursor(buffered=True)
# cursor.execute(query)

add_scheduler_row = ("INSERT INTO SCHED "
               "(algoname, status, start_time, end_time, ip_port, processid) "
               "VALUES (%s, %s, %s, %s, %s, %s)")

data_row = ('dummy', 'Vanderkelen',  '12', '13','as','pid')

# Insert new employee
cursor.execute(add_scheduler_row, data_row)
emp_no = cursor.lastrowid
cnx.commit()
print(emp_no)
print(cursor.rowcount)
# if(cursor.rowcount > 0):
#     o1 = cursor.fetchall()
#     print(o1)
# cursor.close()
# cursor = cnx.cursor()
cursor.execute(query)
if(cursor.rowcount > 0):
    o2 =cursor.fetchall()
    print(o2)
cursor.close()
cnx.close()
