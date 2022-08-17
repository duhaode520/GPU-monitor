import pynvml
import json
import time
import smtplib
from email.mime.text import MIMEText 
from email.utils import formataddr
from configparser import ConfigParser



def mail(info, receivers):
    msg = MIMEText(info, 'plain', 'utf-8')
    msg['From'] =formataddr([f"From {name}",sender])

    subject = f'GPU in {name} is now available!'
    msg['Subject'] = subject

    server = smtplib.SMTP_SSL(mail_host, 465)
    server.login(mail_user, mail_pass)
    if isinstance(receivers, list):
        for receiver in receivers:
            server.sendmail(sender, receiver, msg.as_string())
    else:
        server.sendmail(mail_user, receivers, msg.as_string())
    server.quit()
    print("SUCCESS")



# read config file
config = ConfigParser()
config.read('config.ini', encoding='UTF-8')

# mail section
mail_host = config.get('mail', 'mail_host')
mail_user = config.get('mail', 'mail_user')
mail_pass = config.get('mail', 'mail_pass')
sender = config.get('mail', 'sender')
receivers = config.get('mail', 'receivers')
if receivers[0] == '[': 
    receivers = json.loads(receivers)


# gpu section
threshold = config.get('gpu', 'threshold')
if threshold[0] == '[':
    threshold = json.loads(threshold)
else:
    threshold = int(threshold)
mode = config.get('gpu', 'mode')
if 'num' in config['gpu']:
    num = config.get('gpu', 'num')
    assert(num) # the number of available gpu is not 0
else:
    num = 1
name = config.get('gpu', 'name')

pynvml.nvmlInit()
available_num = -1
device_num = pynvml.nvmlDeviceGetCount()

# when separately set thresholds,
# the number of gpu must equal to the number of thresholds
if isinstance(threshold, list):
    assert(len(threshold) == device_num)

successive_count = 0
while True:
    flag = False # if the gpu is available
    usage = [0 for i in range(device_num)]

    available_count = 0
    for i in range(device_num):
        thr = threshold[i] if isinstance(threshold, list) else threshold
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        meminfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
        usage[i] = int(meminfo.used/1024/1024) # show in MB

        if int(meminfo.used/1024/1024) < thr:
            available_count += 1
            if available_count >= num:
                flag = True
                break
    if flag : 
        if mode == 'monitor':
            info = '''
            GPU Usage :
                    GPU 0: {} M
                    GPU 1: {} M
                    GPU 2: {} M
                    GPU 3: {} M
            '''.format(usage[0], usage[1], usage[2], usage[3])
            mail(info, receivers[0])
            successive_count += 1
            time.sleep(7200*successive_count) # sleep for 2 hours
    else:
        successive_count = 0
        print("ALL BUSY NOW!!!!")
    
    time.sleep(30)
