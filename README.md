# GPU Monitor
A simple gpu monitor script to detect whether the GPUs are available to meet the demand of our DL training task. When the GPUs are available, the monitor will send you an email to notify that you can use the GPUs.

Meanwhile, in the `arrange` mode, the monitor will automatically execute the selected task as soon as the free GPU space meet the demand.

## Request
```
pynvml
```

## Usage
**First**, configure the config.ini profile to set the email address of sender and receivers, the SMTP server, the demand of free space in each GPU.

```ini
[mail]
mail_host = smtp.xxx.com ; host name of smtp server
mail_user = username  ; username of the sender 
mail_pass = yourpass    ; password
sender = sender@xxx.com ; address of the sender 
receivers = ["receiver@xxx.com"] ; list of receivers

[gpu]
name = gpu ; name of the server, which will be showed on the email's title

; demand of free GPU space, can be a simple integer or a list of integers, if the threshold is a list, the length of this list must equal to the number of GPUs
threshold = 8000 

; monitor mode, in "monitor" mode, the monitor will only monitor GPU and notify, in "arrange" mode, the monitor will execute the task if GPUs are available
mode = arrange
; mode = monitor

num = 1 # number of GPUs that need to meet the demand of threshold
task="echo hello" # only use in arrange mode, could be a shell command
```

---

**Second**, run the gpu_monitor_notify.py

```sh
python gpu_monitor_notify.py
```

For nohup execution, using `nohup_run` to run the program in the background.

To kill the nohup program
```sh
ps -aux | grep gpu_monitor_notify # get pid of the nohup program
kill -9 pid
```
