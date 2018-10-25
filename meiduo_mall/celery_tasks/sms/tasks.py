import logging

from celery_tasks.main import app
# from meiduo_mall.libs.yuntongxun.sms import CCP
from meiduo_mall.libs.qcloudsms_py.sms import send_template_sms

@app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    # ccp = CCP()
    # ccp.send_template_sms(mobile, [sms_code, '5'], 1)
    send_template_sms(mobile,sms_code)

