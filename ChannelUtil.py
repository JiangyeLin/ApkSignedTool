#!/usr/bin/python
# coding=utf-8
import os
import shutil
import time

# 获取当前目录中所有的apk源包
src_apks = []
# python3 : os.listdir()即可，这里使用兼容Python2的os.listdir('.')
for file in os.listdir('.'):
    if os.path.isfile(file):
        extension = os.path.splitext(file)[1][1:]
        #遍历apk
        if 'apk' in extension:
            src_apks.append(file)

#脚本逻辑：
#检查源文件是否存在v2签名  true --> 直接写入channel信息
#           false --> 根据下方配置项部分重新帮apk签名并写入channel信息

#配置项 部分start
buildToolFile = "/Users/user1/Library/Android/sdk/build-tools/27.0.3/" 
keyStoreName = "trcube.keystore" #签名信息
KEY_STORE_PWD="qwer"
KEY_ALIAS="qwer"
KEY_PWD="qwer"
SEPARTOR="-" #分隔符，用于区分名称和版本号,且在输出命名时也会使用。 示例：
#源apk命名格式：app-1.0.0.0.apk
#输出格式：管理后台 app-channel-1.0.0.0.apk
#输出格式：阿里云   app-1.0.0.0.apk

#配置项 部分end

# 获取渠道列表
channel_file = 'info/channel.txt'
f = open(channel_file)
lines = f.readlines()
f.close()

#检查是否存在v2签名 方法
#return # 0成功 !0=失败
def checkSignature(temp_apk):
    print("检查签名结果")
    checkResult = os.popen("java -jar util/CheckAndroidV2Signature.jar " + temp_apk)
    result=checkResult.read().strip()
    print(result)
    if result == '{"ret":0,"msg":"ok","isV2":true,"isV2OK":true}':
        return 0
    else:
        return -1

#重新签名 方法
def signApp(src_apk,temp_apk):
    #字节对齐
    os.system(buildToolFile+"zipalign -v -f 4 "+src_apk+" "+ temp_apk)

    #签名
    signPath=buildToolFile+"apksigner sign --ks "+keyStoreName+" --ks-pass pass:"+KEY_STORE_PWD+" --ks-key-alias "+KEY_ALIAS+" --key-pass pass:"+KEY_PWD+ " --v1-signing-enabled true --v2-signing-enabled true "+temp_apk
    checkResult=os.system(signPath)
    if checkResult != 0:
        print("签名命令执行失败,请确认您的签名配置")
        exit(1)


for src_apk in src_apks:
    # file name (with extension)
    src_apk_file_name = os.path.basename(src_apk)
    src_apk_file_name=src_apk_file_name.replace(".apk","")

    # app名称 例如trc,trmall
    apk_name = src_apk_file_name.split(SEPARTOR)[0]
    # 版本名称
    apk_version = src_apk_file_name.split(SEPARTOR)[1]

    # 创建管理后台目录
    output_dir = "AppManager-" + apk_name + SEPARTOR + apk_version + '/'
    if os.path.exists(output_dir):
         shutil.rmtree(output_dir)
    os.mkdir(output_dir)

    # 创建阿里云对应的目录
    output_aliyun_dir = 'Aliyun-' + apk_name + SEPARTOR + apk_version + '/'
    if os.path.exists(output_aliyun_dir):
         shutil.rmtree(output_aliyun_dir)
    os.mkdir(output_aliyun_dir)

    #声明临时文件
    temp_apk = output_dir + apk_name + '.apk'

    #预检查签名
    if checkSignature(src_apk) == 0:
        #apk已签名，直接进入下一步 写入channel信息
        shutil.copy(src_apk,temp_apk)
        print("检查签名成功")
    else:
        #不存在v2签名，先重新签名
        print("检查到apk签名异常，稍后将根据脚本配置项重新签名，请确认配置项正确")
        print("当然，您也可以直接传入已签名的文件，脚本将会跳过签名步骤然后直接写入channel信息")
        time.sleep(2)
        signApp(src_apk,temp_apk)

    print("开始生成渠道包")

    #生成管理后台渠道包
    for line in lines:
        target_channel = line.split('#', 2)[0].strip()
        output=output_dir + apk_name + SEPARTOR +target_channel+ "-" +apk_version+ '.apk' #输出的渠道包名称
        channelResult = os.system("java -jar util/walle-cli-all.jar put -c "+target_channel+" " + temp_apk + " " +output)

        if channelResult == 0:
            print("已生成管理后台 "+target_channel+" 渠道包")
        else:
            print("生成管理后台 "+target_channel+" 渠道包失败")

    #继续生成阿里云渠道包
    print("继续生成阿里云渠道包")
    for line in lines:
        target_channel = line.split('#', 2)[0].strip()
        output=output_aliyun_dir + apk_name + SEPARTOR +target_channel+ '.apk' #输出的渠道包名称
        channelResult = os.system("java -jar util/walle-cli-all.jar put -c "+target_channel+" " + temp_apk + " " +output)

        if channelResult == 0:
            print("已生成阿里云 "+target_channel+" 渠道包")
        else:
            print("生成阿里云 "+target_channel+" 渠道包失败")

    #移除临时文件
    print("删除临时文件")
    os.remove(temp_apk)
    
print("脚本执行完毕")