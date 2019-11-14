# ApkSignedTool

前言

在Android 7.0上引入了v2签名机制，v2签名是对整个apk基于二进制生成签名，因此只要apk有任何改动都会导致校验失败。而我们原来v1版的渠道包生成方案是在apk中META-INF目录中插入一个空文件标识渠道，这必然会破坏apk的二进制结果从而导致签名失效。

至于v3签名，是Android 9.0开始才引入的方案，是对v2完善和补充，具体的原理和签名结构均参照v2模式

在此我们使用了美团的Walle来实现兼容v2签名的渠道包生成脚本，脚本现已支持v2&v3

参见APK 签名方案 v2

使用方法

脚本逻辑：脚本会自动检测apk,如果已签名则直接写入渠道信息；若不存在v2则根据配置项部分重新签名。因此对于源文件无特殊要求，放入debug包、v1包、v2包都可以使用

1.放入apk文件

2.修改py文件中配置项部分(可选)

3.执行脚本

注意：
新脚本打包channel获取方式变更，脚本请搭配lib-common 1.1.1.0食用 

脚本详解

脚本主要分三步流程

1.zipalign字节对齐

2.apk签名

3.生成渠道包

注意：为了防止源文件忘记勾选v2或者说三方加固破坏签名等情况，脚本集成了签名功能，因此不管你的源文件是否签名过，脚本都会帮你apk文件重新签名并进行校验。

这三步都是对官方命令行的封装，有疑问请直接参阅文档

1. https://developer.android.com/studio/publish/app-signing?hl=zh-cn#sign-manually
2. https://developer.android.com/studio/command-line/apksigner.html?hl=zh-cn
3. https://github.com/Meituan-Dianping/walle/blob/master/walle-cli/README.md

测试用例

测试build-tools=27.0.3

  apk来源\设备环境	Android 4.4	Android 7.1	Android 9.0
  只勾选V1     	           	           	           
  勾选v1及v2   	           	           	           
  360加固     	           	           	           

测试步骤

1. 在设备上安装线上APK，使用新脚本打包，验证老脚本迁移后可否顺利升级
2. 验证新脚本apk获取的渠道名是否正确

坑点

1. <del>若使用命令行签名，build-tools>=28，会引入v3签名。但是如果使用Android studio打包，即使项目build-tools版本为28，也不会引入v3签名。而且Android studio上也只提供了v1v2的选择项。因此推测google只在命令行签名工具中开放了v3 <del>
2. <del>渠道包脚本会破坏v3签名，解决方法有两个，要么修改脚本来兼容v3的签名格式，要么使用build-tool27打包不要引入v3。本脚本目前选择的是后者.<del>
3. walle脚本已更新，同时支持v2&v3
