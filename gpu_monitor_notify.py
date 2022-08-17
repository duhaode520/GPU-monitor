import pynvml
import json
import time
import smtplib
from email.mime.text import MIMEText 
from email.utils import formataddr
from configparser import ConfigParser
import subprocess



def mail(subject, info, receivers):
    msg = MIMEText(info, 'plain', 'utf-8')
    msg['From'] =formataddr([f"From {name}",sender])

    msg['Subject'] = subject

    server = smtplib.SMTP_SSL(mail_host, 465)
    server.login(mail_user, mail_pass)
    if isinstance(receivers, list):
        for receiver in receivers:
            server.sendmail(sender, receiver, msg.as_string())
    else:
        server.sendmail(mail_user, receivers, msg.as_string())
    server.quit()
    print("mail sent")



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
    num = int(config.get('gpu', 'num'))
    assert(num > 0) # the number of available gpu is not 0
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
    # flag = True
    usage = [0 for i in range(device_num)]

    available_count = 0
    for i in range(device_num):
        thr = threshold[i] if isinstance(threshold, list) else threshold
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        meminfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
        usage[i] = int(meminfo.used/1024/1024) # show in MB

        if usage[i] < thr:
            available_count += 1
            if available_count >= num:
                flag = True
                break
    if flag : 
        if mode == 'monitor':
            subject = f'GPU in {name} is now available!'
            info = '''
            GPU Usage :
            '''.format(usage[0], usage[1], usage[2], usage[3])
            for i in range(device_num):
                info += '''
                    GPU {}: {} M
                '''.format(i, usage[i])

            mail(subject, info, receivers)
            successive_count += 1
            time.sleep(7200*successive_count) # sleep for 2 hours

        if mode == 'arrange':
            subject = f'GPU in {name} is now available!'
            task_file = config.get('gpu', 'task_file')
            p = subprocess.Popen(task_file, shell=True, 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            info = '''
            Successfully assign task {} to GPU
            '''.format(task_file)
            mail(subject, info, receivers)

            # wait for the task to finish
            return_code = p.wait()
            stdout, stderr = p.communicate()
            if return_code == 0:
                mail("Task on GPU finished", 
                    f"Task {task_file} finished", receivers)
            else :
                mail("Task on GPU failed", 
                    stderr, receivers)
            break

    else:
        successive_count = 0
        print("ALL BUSY NOW!!!!")
    
    time.sleep(30)
