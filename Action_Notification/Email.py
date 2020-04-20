import smtplib,json
 
def sendemail(from_addr, to_addr_list, 
              subject, message,
              login, password,
              smtpserver='smtp.gmail.com:587',
              cc_addr_list=''):
    header  = 'From: %s ' % from_addr
    header += 'To: %s' % ','.join(to_addr_list)
    header += 'Cc: %s' % ','.join(cc_addr_list)
    header += 'Subject: %s' % subject
    message = header + message
 
    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login,password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()

def set_message_for_Security(input_message):
    message = """\
    Security Alert Notification
    \n Location = """ + input_message["location"] + """
    \n Time of Audit = """ + input_message["time_stamp"] + """
    \n Status = """ + input_message["status"]
    return str(message)


def sendemail_via_gmail(stats,automated='Automatic Mail'):
    print(" Inside Email ")

    if __debug__:
        print(" Input of Mail in Email class ")
        print(stats)
    
    email = smtplib.SMTP('smtp.gmail.com', 587) 
    email.starttls() 

    '''
    http://127.0.0.1:9941/send_email/%7B'status':%20'Safe',%20'time_stamp':%20'Monday_20_April_2020_08_56_AM',%20'algorithm':%20'Illegal_Access_Detection',%20'topic_name':%20'Security_Breach'%7D
    '''

    # sender_email = "varunsurat1995@gmail.com"
    # sender_email_password = "Varun@123"

    sender_email = "nssridummy@gmail.com"
    sender_email_password = "ias_12345"
    subject = "IAS_App_Mail_Security_Alert_Notification"

    print(" Inside Email 2")

    # email.login("nssridummy@gmail.com", "ias_12345")
    print(email.login(sender_email, sender_email_password))

    print(" Inside Email 4")
    print(" Inside Email 4-0")



    # if __debug__:
        # input_message = json.loads(stats)
    # print("input_message ",input_message,"")

    receiver_email = stats["to_email_id"]


    if receiver_email == "self":
        receiver_email = sender_email

    mail_body = set_message_for_Security(stats)
    mail_body = str(automated) + "\n " + mail_body

    # header  = 'From: %s ' % sender_email
    # header += 'To: %s' % receiver_email
    # header += 'Subject: %s' % subject

    # mail_body = header + mail_body

    print(" Inside Email 5")
    print(mail_body)
  
    # terminating the session 
    email.sendmail(sender_email, receiver_email, mail_body)
    email.quit()
    
    print("Server Done")


if __name__ == '__main__':
    local_stats = \
        "{\"location\" : \"Room1\",\"status\" : \"Breached\",\
        \"to_email_id\" : \"nssridummy@gmail.com\",\"time_stamp\" : \"Monday, 20 April 2020 06:15AM\"}";
    sendemail_via_gmail(local_stats,automated='Manual')

