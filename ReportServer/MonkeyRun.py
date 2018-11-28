# coding=utf-8


'''
配置config.yaml执行
'''

import subprocess,os,sys
from BasicMonkey import BasicMonkey
from AdbCommon import AdbCommon
from DateBean import DateBean
import logger
import MonkeyParamters
from jenkinsApiTest import jenkinsApi
from report import *
reload(sys)
sys.setdefaultencoding('utf-8')
base_dir = os.path.dirname(__file__)
apkdir = os.path.join(base_dir)+'/TestApp'
def file_name(file_dir):
    L=[]
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if os.path.splitext(file)[1] == '.apk':
                L.append(os.path.join(root, file))
    return L

def getdevices():
    '''
    获取设备id
    :return: 0表示未获取到,id是设备的真实id
    '''

    try:
        cmd = "adb devices"
        pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout
        id = pipe.read().split()[-2]
        if id != 'devices':
            return id
        else:
            logger.log_info("List of devices attached")
            return 0

    except Exception, e:
        logger.log_error("the process doesn't exist." + str(e))
        return 0

def run():
    #env = os.environ["ENV"]
    env = MonkeyParamters.env
    apkpackagename = MonkeyParamters.apkpackagename
    # apk包名
    seed = MonkeyParamters.seed
    # monkey命令的seed值
    apkpath = ''.join(file_name(apkdir))
    apkname = ''.join(file_name(apkdir)).split('/')[-1]
    # apk路径
    throttle = MonkeyParamters.throttle
    # 时间间隔
    devices = getdevices()
    # 设备号
    whitelist = MonkeyParamters.whitelist
    # 白名单
    blacklist = MonkeyParamters.blacklist

    # 黑名单
    eventcount=MonkeyParamters.eventcount
    #事件次数
    loglevel = MonkeyParamters.loglevel
    # 日志等级

    adc = AdbCommon(devices)
    # 初始化AdbCommon类
    db = DateBean()
    ja = jenkinsApi()
    lastSuccessfulBuildNum = ja.getlastSuccessfulBuildNum()
    logger.setup_logger(loglevel)
    # 设置log级别




    try:
        apkpath = adc.getfolderapk(apkpath)
        flag6 = True
    except Exception, e:
        logger.log_error('获取apk路径失败'  + '\n' + '异常信息:' + str(e))

    if  flag6 == True :

        info = 'apkpackagename is:"{}'.format(apkpackagename) + '\n' + \
              'seed is:{}'.format(seed) + '\n' + \
               'apkpath is: {}'.format(apkpath) + '\n' + \
              'throttle is: {}'.format(throttle) + '\n' + \
               'whitelist is: {}'.format(whitelist) + '\n' + \
               'blacklist is: {}'.format(blacklist) + '\n' + \
               'env is: {}'.format(env) + '\n' + \
               'devices is: {}'.format(devices) + '\n' +\
               'apkname is: {}'.format(apkname)+ '\n' +\
               'eventcount is: {}'.format(eventcount)+ '\n' + \
               'lastSuccessfulBuildNum is: {}'.format(lastSuccessfulBuildNum)

        logger.log_info(info)

        if devices != 0:
            if adc.installdependapp() == 0:
                if adc.launch_app(db.simiasquename,db.simiasqueactivity) == 0:
                    adc.sendbroadcast(0)
                    # 开启隐藏导航栏
                    if adc.installapp(apkpackagename, apkpath) == 0:
                       main(devices=devices,seed=seed, apkpackagename=apkpackagename,apkpath=apkpath,apkname=apkname,env=env,
                            throttle=throttle,whitelist=whitelist,blacklist=blacklist, db=db,eventcount=eventcount,ja=ja,lastSuccessfulBuildNum=lastSuccessfulBuildNum)
                       #adc.delallfiles('MonkeyLog')
                       #adc.delallfiles('Log')
                       #adc.delallfiles('TestApp')
                       #testappfolder = os.getcwd() + '/' + 'TestApp'
                       #if len(os.listdir(testappfolder)) == 0:
                           #return 0
                       #else:
                           #return 1
                    else:
                        logger.log_info('安装%s失败,请检查apk文件路径%s' % (apkpackagename, apkpath))
                        return 1

            else:
                logger.log_info('安装依赖app失败')
                return 1

        else:
            logger.log_info('手机设备未链接')
            return 1

    else:
        logger.log_info('请检查apk路径')
        return  1



def main(**kwargs):
    '''
        Main主脚本执行Monkey
        '''
    env = kwargs['env']
    apkpath = kwargs['apkpath']
    apkname = kwargs['apkname']
    devices = kwargs['devices']
    seed = kwargs['seed']
    apkpackagename = kwargs['apkpackagename']
    throttle = kwargs['throttle']
    whitelist = kwargs['whitelist']
    blacklist = kwargs['blacklist']
    eventcount = kwargs['eventcount']
    db = kwargs['db']
    lastSuccessfulBuildNum = kwargs['lastSuccessfulBuildNum']
    apk_href = MonkeyParamters.jenkins_server_url + "/job/" + MonkeyParamters.job_name + "/" + str(lastSuccessfulBuildNum)
    adc = AdbCommon(devices)
    bsm = BasicMonkey(devices)
    # 初始化类
    bsm.init_runmonkey(apkpackagename, env)
    # 初始化app登录

    monkeylog = base_dir+'/'+db.monkeylog
    monkeyerrorlog = base_dir+'/'+db.monkeyerrorlog
    writeerror = base_dir+'/'+db.writeerror

    starttime = int(abs(round(time.time(), 0)))

    starttimestamps = time.strftime('%Y-%m-%d %H:%M:%S')
    logger.log_info('Monkey脚本 - 开始' + '\n' \
                    + '开始时间:%s' % str(starttimestamps))

    monkeycmd = bsm.runmonkey(seed, apkpackagename, throttle, eventcount, monkeylog, monkeyerrorlog)
    # monkeycmd = bsm.runmonkey(seed, apkpackagename, throttle, monkeylog)
    # 执行Monkey

    flag = True
    # time.sleep(3)

    while flag:

        adc.checkwifi()
        # 检查wifi状态并开启

        activity = adc.getactivity()
        # 获取当前运行的activity
        if whitelist != '':
            bsm.whitelistrun(activity, whitelist, apkpackagename)
            # 检测monkey运行状态
        if blacklist != '':
            bsm.blacklistrun(activity, blacklist, apkpackagename)
            # 检测monkey运行状态

        currenttime = int(abs(round(time.time(), 0)))
        # 获取当前运行时间

        logger.log_info('已经运行时间: %d' % (currenttime - starttime))
        # logger.log_info('预期运行时间: %d' % (int(runtime) * 60))
        '''
        if (currenttime - starttime) >= (int(runtime) * 60):
            bsm.stopmonkey()
            flag = False
        '''
        if bsm.monkey_finish(monkeylog) == 0:
            bsm.stopmonkey()
            flag = False

    endtime = int(abs(round(time.time(), 0)))
    runtime = time.strftime("%H:%M:%S", time.gmtime(endtime - starttime))

    endtimestamps = time.strftime('%Y-%m-%d %H:%M:%S')

    logger.log_info('Monkey脚本 - 结束' + '\n' + \
                    ',结束时间:%s' % str(endtimestamps) + \
                    ',耗时%s秒' % str(runtime))

    adc.sendbroadcast(1)
    # 关闭隐藏导航
    result = bsm.writeerror(monkeylog, writeerror)
    if result[0] == 0:
        emCrash = result[1]
        emANR = result[2]
        emNoResponse = result[3]
        emError = result[4]
        emException = result[5]
        model = adc.getmobilebrand()
        system_version = adc.getmobileversion()
        error_list = [emCrash, emANR, emNoResponse, emError, emException]
        log_list = [monkeylog]
        # 获取monkeylog所有日志send_mail(devices,monkeylog, writeerror,str(difftime),monkeycmd)
        code,msg = send_monkey_report(apkname, apk_href, runtime, model, system_version, error_list, monkeycmd, log_list)
        logger.log_info(msg)
    else:
        emCrash = result[1]
        emANR = result[2]
        emNoResponse = result[3]
        emError = result[4]
        emException = result[5]
        model = adc.getmobilebrand()
        system_version = adc.getmobileversion()
        error_list = [emCrash, emANR, emNoResponse, emError, emException]
        log_list = [monkeylog]
        # 获取monkeylog所有日志send_mail(devices,monkeylog, writeerror,str(difftime),monkeycmd)
        code, msg = send_monkey_report(apkname, apk_href, runtime, model, system_version, error_list, monkeycmd, log_list)
        logger.log_info(msg)


if __name__ == '__main__':
    run()






