# coding=utf-8

'''
monkey常用操作类
@author
'''


import os,sys
import time
import re
import subprocess
from AdbCommon import AdbCommon
import random
import logger
import linecache
from DateBean import DateBean
import  MonkeyParamters
from report import *
#quotiety = int(10000000 / 60)
reload(sys)
sys.setdefaultencoding('utf-8')
quotiety = int(62500 / 60)
# 事件和时间的系数
flipjavaIOException = 'flipjava.io.IOException'
CRASH = 'CRASH'
ANR = 'ANR'
anr = 'anr'
Exception= 'Exception'
error= 'error'
Error= 'Error'
NoResponse = 'No Response'
NullPointer="java.lang.NullPointerException"
IllegalState="java.lang.IllegalStateException"
IllegalArgument="java.lang.IllegalArgumentException"
ArrayIndexOutOfBounds="java.lang.ArrayIndexOutOfBoundsException"
RuntimeException="java.lang.RuntimeException"
SecurityException="java.lang.SecurityException"
Monkey_Finish='Monkey finished'
IncludeCategory='IncludeCategory'
# 过滤Monkey关键字

key = []

e = None
pid = None
activitywhitelist = []
activityblacklist = []

class BasicMonkey():

    def __init__(self, dev):
        self.dev = dev
        # 设备devicesid
        #self.event = pow(10, 5)
        # 发送事件总数,100W
        self.adc = AdbCommon(self.dev)
        self.db = DateBean()

    def init_runmonkey(self, packagename,env):
        # 引导页升级提示关闭坐标
        x_upgrade = 950
        y_upgrade = 700
        # 引导页登录按钮坐标
        x_login = 300
        y_login = 1400
        # 账号坐标
        x_login_account = 400
        y_login_account = 580
        # 密码坐标
        x_login_pwd = 400
        y_login_pwd = 800
        # 登录按钮坐标
        x_login_btn = 400
        y_login_btn = 1080
        # 暂不开通坐标
        x_noopen_btn = 400
        y_noopen_btn = 1080
        # 我知道了坐标
        x_know_btn = 400
        y_know_btn = 1200
        # 立即体验坐标
        x_exp_btn = 400
        y_exp_btn = 1300
        # 关闭广告坐标
        x_adv_btn = 980
        y_adv_btn = 480
        # 首页登录坐标
        x_firstpage_btn = 800
        y_firstpage_btn = 1650
        # 启动app
        self.adc.launch_app(packagename, packagename + '.ui.SplashScreenActivity')
        #点击升级关闭按钮
        self.adc.click_ele(x_upgrade, y_upgrade)
        #点击立即体验
        self.adc.click_ele(x_exp_btn, y_exp_btn)
        # 点击关闭广告
        self.adc.click_ele(x_adv_btn, y_adv_btn)
        # 点击首页登录按钮
        self.adc.click_ele(x_firstpage_btn, y_firstpage_btn)
        if env == 'test':
            # 点击账号坐标
            test_accont = MonkeyParamters.testaccount
            test_pwd = MonkeyParamters.testpwd
            self.adc.click_ele(x_login_account, y_login_account)
            self.adc.input_text(test_accont)
            self.adc.click_ele(x_login_pwd, y_login_pwd)
            self.adc.input_text(test_pwd)
            self.adc.click_ele(x_login_btn, y_login_btn)
        if env == 'demo':
            # 点击账号坐标
            demo_accont = MonkeyParamters.demoaccount
            demo_pwd = MonkeyParamters.demopwd
            self.adc.click_ele(x_login_account, y_login_account)
            self.adc.input_text(demo_accont)
            self.adc.click_ele(x_login_pwd, y_login_pwd)
            self.adc.input_text(demo_pwd)
            self.adc.click_ele(x_login_btn, y_login_btn)
        # 点击立即体验
        self.adc.click_ele(x_exp_btn, y_exp_btn)
        # 点击双重验证暂不开通
        #self.adc.click_ele(x_noopen_btn, y_noopen_btn)
        # 点击我知道了
        #self.adc.click_ele(x_know_btn, y_know_btn)
        # 点击立即体验
        #self.adc.click_ele(x_exp_btn, y_exp_btn)
        # 点击关闭广告
        self.adc.click_ele(x_adv_btn, y_adv_btn)

    def runmonkey(self,seed, packagename, throttle, eventcount,monkeylog,errorlog):
        '''
        执行Monkey
        :return:
        '''
        cmd = 'adb -s %s shell monkey ' \
              '-s %d ' \
              '-p %s ' \
              '--hprof ' \
              '--throttle %d ' \
              '--ignore-crashes ' \
              '--ignore-timeouts ' \
              '--ignore-security-exceptions ' \
              '--ignore-native-crashes ' \
              '--monitor-native-crashes ' \
              '--pct-syskeys 0 ' \
              '-v -v -v %d  2>%s 1>%s' % \
              (self.dev,int(seed), packagename, int(throttle),
               int(eventcount),errorlog,monkeylog)

        logger.log_info("Monkey命令:%s" % cmd)
        pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout
        return cmd


    def stopmonkey(self):
        '''
        停止Monkey
        :return:
        '''
        # 利用管道打印内容
        try:

            grep_cmd = "adb -s %s shell ps | grep monkey" % self.dev
            pipe = os.popen(grep_cmd)
            result = pipe.read()
            if result == '':
                logger.log_info('monekey进程不存在')
            else:
                logger.log_info('monekey进程存在')
                pid = result.split()[1]
                # kill monkey进程
                stop_cmd = "adb -s %s shell kill %s" % (self.dev,pid)
                os.system(stop_cmd)
                self.stopmonkey()
        except Exception as e:
            logger.log_error('stopmonkey异常: ' + str(e))


    def getmonkey(self,monkeylog):
        '''
        通过monkeylog日志判断monkey是否结束
        :param monkeylog:
        :return: 0表示未结束,1表示结束
        '''
        with open(monkeylog) as f:
            if Monkey_Finish in f.read():
                return 1
            else:
                return 0


    def findmonkey(self):
        '''
        寻找Monkey的pid
        :return:
        '''
        global e
        global pid
        try:
            grep_cmd = "adb -s %s shell ps | grep monkey" % self.dev
            pipe = os.popen(grep_cmd)
            pids = pipe.read()
            if pids == '':
               logger.log_info("当前monkey进程不存在")
               return 1
            else:
               pid = pids.split()[1]
            logger.log_info("当前monkey进程pid:%s" % pid)
            return 0
        except Exception ,e:
            logger.log_error("当前monkey进程不存在:%s" % str(e))
            return 1

    def emptylogcat(self):
        '''
        在monkey运行前执行adb logcat -c清空所有log缓存日志
        :return: 0表示执行成功,1表示执行出现异常
        '''
        try:
            logger.log_info("使用adb logcat -c清空手机中的手机中的log")
            os.popen("adb -s %s logcat -c" % self.dev )
            return 0

        except Exception,e:
            logger.log_error("执行adb logcat -c出现异常%s" % str(e))
            return 1


    def getlogcat(self):
        '''
        获取logcat日志中所有日志
        :return:返回保存logcat的文件地址
        '''
        if not os.path.exists(self.db.logdir):
            os.mkdir(self.db.logdir)
        logcatname = self.db.logdir + "/" + time.strftime("%Y%m%d%H%M%S") + "_logcat.log"
        # 定义logcat文件保存地址
        cmd = "adb -s %s logcat -d  >%s" % (self.dev,logcatname)
        # 获取logcat日志
        os.popen(cmd)
        time.sleep(2)
        return logcatname

    def monkey_finish(self,logcatpath):
        '''
        根据log文件是否包含 monkey finish判断是否执行结束
        0：结束 1：没有
        '''
        f = open(logcatpath, "r")
        lines = f.readlines()  # 读取所有行
        last_line = lines[-1]  # 取最后一行
        if len(lines) == 0:
            logger.log_info("扫描%s路径的log日志为空,将删除" % logcatpath)
            os.system('rm -rf %s' % logcatpath)
            return 1
        else:
            if re.findall(Monkey_Finish, last_line):
                return 0

    def writeerror(self,logcatpath,wirteerrorpath):
        '''
        根据log文件地址,写入到error文件中
        :param logcatpath: log文件地址
        :param wirteerrorpath: 写入error的文件地址
        :return:0表示有错误日志,1表示没有错误日志
        '''
        try:
            f = open(logcatpath, "r")
            lines = f.readlines()
            if len(lines) == 0:
                logger.log_info("扫描%s路径的log日志为空,将删除" % logcatpath)
                os.system('rm -rf %s' % logcatpath)
            else:
                logger.log_info("扫描%s路径的log日志不为空" % logcatpath)
                fr = open(wirteerrorpath, "a")
                crashnum = 0
                anrnumber = 0
                errornum = 0
                noresponsenum = 0
                exceptionnum = 0
                number = 1
                emCrash = ErrorMsg(CRASH, crashnum, '')
                emANR = ErrorMsg(ANR, anrnumber, '')
                emNoResponse = ErrorMsg(NoResponse, noresponsenum, '')
                emError = ErrorMsg(Error, errornum, '')
                emException = ErrorMsg(Exception, exceptionnum, '')
                for line in lines:
                    if (re.findall(CRASH, line)):
                        crashnum += 1
                        emCrash.error_count = crashnum
                        emCrash.error_desc = emCrash.error_desc + "第%s行" % number + ' , ' + "错误原因:%s" % line + '<br>'
                    if (re.findall(ANR, line)):
                        anrnumber += 1
                        emANR.error_count = anrnumber
                        emANR.error_desc = emANR.error_desc + "第%s行" % number + ' , ' + "错误原因:%s" % line + '<br>'
                    if (re.findall(anr, line)):
                        anrnumber += 1
                        emANR.error_count = anrnumber
                        emANR.error_desc = emANR.error_desc + "第%s行" % number + ' , ' + "错误原因:%s" % line + '<br>'
                    if (re.findall(NoResponse, line)):
                        noresponsenum += 1
                        emNoResponse.error_count = noresponsenum
                        emNoResponse.error_desc = emNoResponse.error_desc + "第%s行" % number + ' , ' + "错误原因:%s" % line + '<br>'
                    if (re.findall(error, line)):
                        errornum += 1
                        emError.error_count = errornum
                        emError.error_desc = emError.error_desc + "第%s行" % number + ' , ' + "错误原因:%s" % line + '<br>'
                    if (re.findall(Error, line)):
                        errornum += 1
                        emError.error_count = errornum
                        emError.error_desc = emError.error_desc + "第%s行" % number + ' , ' + "错误原因:%s" % line + '<br>'
                    if (re.findall(Exception, line)):
                        if (re.findall(flipjavaIOException, line)):
                            pass
                        else:
                            exceptionnum += 1
                            emException.error_count = exceptionnum
                            emException.error_desc = emException.error_desc + "第%s行" % number + ' , ' + "错误原因:%s" % line + '<br>'
                    number += 1
                    f.close()
                    fr.close()
                if os.path.getsize(wirteerrorpath)  == 0:
                    logger.log_info("扫描%s路径的log日志中未发现错误日志" % logcatpath)
                    #os.system('rm -rf %s' % wirteerrorpath)
                    return 1,emCrash,emANR,emNoResponse,emError,emException
                else:
                    logger.log_info("扫描%s路径的log日志中发现错误日志" % logcatpath)
                    return 0,emCrash,emANR,emNoResponse,emError,emException
        except Exception,e:
            logger.log_info(e.message)



    def returnmonkey(self,activity):
        '''
        如果不在monkey的运行activity中,重新返回monkey运行
        :param activity 当前运行的activity
        :return:
        '''

        if activity.startswith('com.luojilab'):
            logger.log_info('monke运行未溢出activity范围')
            return 0
        else:
            logger.log_info('monke运行溢出activity范围,跳转到%s' % self.activity)
            cmd = "adb -s %s shell am start -n %s/%s" % (self.dev, self.pck, self.activity)
            os.system(cmd)
            return 1


    def whitelistrun(self,activity,whitelist,apkpackage):
        '''
        白名单机制,只能执行定义的activity
        com.xxxxx.xxxxx.erechtheion.activity.ErechInfoActivity
        com.xxxxx.xxxxx.ddplayer.player.LuoJiLabPlayerActivity
        com.xxxxx.xxxxx.HomeTabActivity
        com.xxxxx.xxxxx.studyplan.ui.activity.SettingStudyPlanActivity
        :param activity 当前运行的activity
        :param whitelist白名单列表
        :return:
        '''
        #global activitywhitelist
        if isinstance(whitelist,str):
            activitywhitelist = whitelist.split(',')
        if re.findall(activity,str(activitywhitelist)):
            logger.log_info('monke运行未溢出白名单范围')
            return 0

        else:
            try:
                randomactivity = (random.randint(0, len(activitywhitelist) - 1))
                logger.log_info('monke运行溢出activity范围,跳转到%s' % activitywhitelist[randomactivity])
                cmd = "adb -s %s shell am start -n %s/%s" % (self.dev, apkpackage, activitywhitelist[randomactivity])
                logger.log_info('monkey跳转命令:%s' % cmd)
                os.system(cmd)
                return 1
            except Exception as e:
                logger.log_error('monke运行跳转到白名单异常: ' + str(e))


    def blacklistrun(self,activity,blacklist,apkpackage):
        '''apkpackage

        运行到黑名单跳转到首页activity
        :return:
        '''
        #global activityblacklist
        mainactivity = 'xxxxx.ui.MainActivity'

        if isinstance(blacklist,str):
           activityblacklist = blacklist.split(',')
        if re.findall(activity,str(activityblacklist)):
            logger.log_info('运行到黑名单,执行命令跳转到首页')
            cmd = "adb -s %s shell am start -n %s/%s" % (self.dev, apkpackage, mainactivity)
            logger.log_info('monkey跳转到首页:%s' % cmd)
            os.system(cmd)
            return 0

        else:
            logger.log_info('未运行到黑名单')
            return 1

    def grepmonkey(self,filename):
        '''
        从monkeylog日志从获取行数,判断是否结束
        如果本次和前一次的行数一样,则认为已经结束了monkey
        :return:
        '''
        return len(linecache.getlines(filename))


