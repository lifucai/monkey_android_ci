# coding:utf-8
import sys
import smtplib, time, os
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import MailConfig
reload(sys)
sys.setdefaultencoding('utf-8')
report_template = ''' 
<head>
  <meta content="text/html; charset=utf-8" http-equiv="content-type" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title> - TestReport</title>
  <style>
    body {
      background-color: #f2f2f2;
      color: #333;
      margin: 0 auto;
      width: 960px;
    }
    .details {
      width: 960px;
      margin-bottom: 20px;
    }
    @media screen and (max-width: 700px) {
      .box {
        width: 70%%;
      }
      .popup {
        width: 70%%;
      }
    }

  </style>
</head>

<body>
  <h1>Android Monkey Test Report: </h1>
  <h2>基本信息</h2>
  <table id="summary" class="details">
    %s
  </table>

  <h2>错误信息</h2>
  <table id="suite_1" class="details">
    %s
  </table>
  <h2>monkey执行命令</h2>
  <table id="suite_2" class="details">
   %s
  </table>
</body>
'''


class ErrorMsg:
    def __init__(self, error_type, error_count, error_desc):
        self.error_type = error_type
        self.error_count = error_count
        self.error_desc = error_desc


'''
    获取基本信息
'''


def get_basic_info(apk, apk_href, run_time, model, system_version):
    basic_format = '<tr bgcolor=lightblue><td>%s</td><td>%s</td></tr>\n'
    basic_href_format = '<tr bgcolor=lightblue><td>%s</td><td><a href=%s>%s</a></td></tr>'
    run_time_info = basic_format % ('monkey运行时长', run_time)
    apk_info = basic_href_format % ('测试包', apk_href, apk)
    model_info = basic_format % ('设备型号', model)
    version_info = basic_format % ('系统版本', system_version)
    basic_info = apk_info + model_info + version_info + run_time_info;
    return basic_info


'''
    获取错误信息
'''


def get_error_info(error_list):
    basic_format = '<tr bgcolor=lightblue><td>%s</td><td>%s</td><td>%s</td></tr>\n'
    title_format = '<tr bgcolor="#F5DEB3"><td>%s</td><td>%s</td><td>%s</td></tr>'
    title = title_format % ('错误类型', '数量', '错误信息')
    error_info = title
    if isinstance(error_list, list):
        if len(error_list) == 0:
            return error_info
        else:
            for errorObj in error_list:
                if isinstance(errorObj, ErrorMsg):
                    info = basic_format % (errorObj.error_type, errorObj.error_count, errorObj.error_desc)
                    error_info = error_info + info

    return error_info


'''
    获取monkey命令
'''


def get_monkey_cmd_info(monkey_cmd):
    return '<tr bgcolor=lightblue><td>%s</td></tr>\n' % (monkey_cmd)


'''
    生成邮件内容
'''


def get_email_content(apk, apk_href, run_time, model, system_version, error_list, monkey_cmd):
    # 获取基本信息
    basic_info = get_basic_info(apk, apk_href, run_time, model, system_version)
    # 获取错误信息
    error_info = get_error_info(error_list)
    # 获取执行命令
    cmd_info = get_monkey_cmd_info(monkey_cmd)

    email_content = report_template % (basic_info, error_info, cmd_info)
    return email_content


'''
    发送邮件
'''


def send_email(mail_body, log_list):
    code = 0
    result = '邮件发送成功'

    '''发送html内容邮件'''
    sender = MailConfig.mail_user
    receivers = MailConfig.debuglist
    # 发送邮件主题
    t = time.strftime("%Y%m%d", time.localtime())
    subject = '[xxxx]AndroidMonkeyTestReport_' + t
    # 发送邮箱服务器
    smtpserver_host = MailConfig.mail_host
    smtp_port = MailConfig.mail_port
    # 发送邮箱用户/密码
    username = MailConfig.mail_user
    password = MailConfig.mail_pass
    smtp = None
    try:
        # 组装邮件内容和标题，中文需参数‘utf-8’，单字节字符不需要
        msg = MIMEMultipart()
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = sender
        msg['To'] = ";".join(receivers)

        report_content = MIMEText(mail_body, _subtype='html', _charset='utf-8')
        msg.attach(report_content)

        for log_path in log_list:
            if os.path.exists(log_path):
                logpart = MIMEApplication(open(log_path, 'rb').read())
                logpart.add_header('Content-Disposition', 'attachment', filename=os.path.basename(log_path))
                msg.attach(logpart)

        # 登录并发送邮件
        smtp = smtplib.SMTP()
        smtp.connect(smtpserver_host, smtp_port)
        smtp.starttls()
        smtp.login(username, password)
        smtp.sendmail(sender, receivers, msg.as_string())
    except Exception, e:
        code = -1
        result = '邮件发送失败' + e.message
    finally:
        if not smtp is None:
            smtp.quit()
        #print code
        #print result
        return code, result


'''
    发送测试报告
'''


def send_monkey_report(apk, apk_href, run_time, model, system_version, error_list, monkey_cmd, log_list):
    code = -1
    result = '发送失败'
    email_content = ''

    # 参数校验异常
    if (not isinstance(error_list, list)) or (not isinstance(log_list, list)):
        code = -1
        result = '发送邮件参数异常！！'
        return code, result

    # 生成邮件内容
    try:
        email_content = get_email_content(apk, apk_href, run_time, model, system_version, error_list, monkey_cmd)
    except Exception, e:
        code = -1
        result = '生成邮件内容失败：' + e.message
        return code, result

    code, result = send_email(email_content, log_list)
    return code, result

# error_list = []
# monkey_cmd = '''
# adb -s 0216029b21df2403 shell monkey -s 20 -p xxxxx --hprof -
#     -throttle 0 --ignore-crashes --ignore-timeouts --ignore-security-exceptions --ignore-nativ
#     e-crashes --monitor-native-crashes --pct-syskeys 0 -v -v -v 100000  2>MonkeyLog/MonkeyErro
#     r_20181109160202.log 1>MonkeyLog/MonkeyInfo_20181109160202.log
#
# '''
# for i in range(5):
#     error_msg = ErrorMsg("exception", 5,
#                          "第3行 , 错误原因::IncludeCategory: android.intent.category.LAUNCHER<br>第4行 , 错误原因::IncludeCategory: android.intent.category.MONKEY")
#     error_list.append(error_msg)
#
# email_content = get_email_content("test.apk",
#                                   "http://www.baidu.com",
#                                   160, "oppoR11", "7.0", error_list, monkey_cmd)
#
# # path = '/Users/xxxx/Desktop/xxxx.html'
# #
# # w = file(path, 'w')
# # w.write(email_content)
# # w.close()
# log_path = ['/Users/xxxx/Desktop/xxxx.html']
#
# send_monkey_report("test.apk","www.baidu,com",160,"oppoR11", "7.0", error_list, monkey_cmd,log_path)
