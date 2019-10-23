#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import re
import shutil
import tempfile
import argparse
import json

class Translator:
    def __init__(self, lang):
        self.lang        = lang
        self.basePath    = os.path.dirname(os.path.abspath(__file__))
        self.opJsonFile  = self.basePath + "/i18n/openpilot/%s.json" % self.lang
        self.apkJsonFile = self.basePath + "/i18n/apks/%s.json" % self.lang
        # 字体文件目录
        self.opFontDir  = self.basePath + "/i18n/fonts/%s/." % self.lang
        self.dstFontDir = self.basePath + "/openpilot/fonts"
        # op启动文件
        self.opLaunchFile = self.basePath + "/openpilot/launch_openpilot.sh"
        # TableCell Style
        self.apkStyleFile = "openpilot-apks/offroad/node_modules/comma-x-native/x/components/TableCell/TableCellStyles.js"
        # 需要替换翻译信息的目录地址
        self.opPath   = self.basePath + "/openpilot/selfdrive/controls/lib"
        self.apkPath1 = self.basePath + "/openpilot-apks/offroad/js/components"
        self.apkPath2 = self.basePath + "/openpilot-apks/frame/app/src/main/java/ai/comma/plus/frame"
        self.apkPath3 = self.basePath + "/openpilot-apks/frame/app/src/main/res/layout"
        self.opFiles     = []
        self.apkFiles    = []
        self.opJson      = {}
        self.apkJson     = {}
        self.readJson()
        self.getFiles()

    def readJson(self):
        with open(self.opJsonFile) as f:
            self.opJson = json.load(f)
        with open(self.apkJsonFile) as f:
            self.apkJson = json.load(f)

    def getFiles(self):
        # 所有需要搜索替换的 op 代码
        self.opFiles = self.getAllFileByPath(self.opPath)
        # 所有需要搜索替换的 apk 代码
        apkFiles1 = self.getAllFileByPath(self.apkPath1)
        apkFiles2 = self.getAllFileByPath(self.apkPath2)
        apkFiles3 = self.getAllFileByPath(self.apkPath3)
        self.apkFiles.extend(apkFiles1)
        self.apkFiles.extend(apkFiles2)
        self.apkFiles.extend(apkFiles3)

    def run(self):
        # 替换 op 翻译
        for find, replace in self.opJson.iteritems():
            for f in self.opFiles:
                self.sedInplace(f, find.encode('utf-8'), replace.encode('utf-8'))

        # 替换 apk 翻译
        for find, replace in self.apkJson.iteritems():
            for f in self.apkFiles:
                self.sedInplace(f, find.encode('utf-8'), replace.encode('utf-8'))

        # 复制字体文件到目录
        os.system("cp -rf %s %s" % (self.opFontDir, self.dstFontDir))

        # 添加自动安装字体文件的命令
        self.addInstallCommand()

        # 修改 TableCell Style
        self.fixTableCellStyle()

    def getAllFileByPath(self, path):
        files = []
        parents = os.listdir(path)
        for parent in parents:
            if parent[0] == ".": continue
            child = os.path.join(path, parent)
            if os.path.isdir(child):
                childFiles = self.getAllFileByPath(child)
                files.extend(childFiles)
            else:
                if child[0] == ".": continue
                files.append(child)
        return files

    def addInstallCommand(self):
        installCmd = "\n/usr/bin/sh /data/openpilot/fonts/installer.sh &"
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmpFile:
            with open(self.opLaunchFile) as srcFile:
                lines = srcFile.read()
                lines = re.sub(re.escape(installCmd), "", lines)
                tmpFile.write(re.sub(re.escape("\n"), "\n" + installCmd, lines, 1))
        shutil.copystat(self.opLaunchFile, tmpFile.name)
        shutil.move(tmpFile.name, self.opLaunchFile)

    def fixTableCellStyle(self):
        find = "defaultSizeTableCellDrawer: {"
        replace = "\npaddingTop:10,"
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmpFile:
            with open(self.apkStyleFile) as srcFile:
                lines = srcFile.read()
                lines = re.sub(re.escape(replace), "", lines)
                tmpFile.write(re.sub(re.escape(find), find + replace, lines, 1))
        shutil.copystat(self.apkStyleFile, tmpFile.name)
        shutil.move(tmpFile.name, self.apkStyleFile)

    def sedInplace(self, filename, pattern, repl):
        patternCompiled = re.compile(re.escape(pattern))
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmpFile:
            with open(filename) as srcFile:
                lines = srcFile.read()
                tmpFile.write(patternCompiled.sub(repl, lines))

        shutil.copystat(filename, tmpFile.name)
        shutil.move(tmpFile.name, filename)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang', '-l', required=True, help='target language [zhs|zht]')
    args = parser.parse_args()
    # run translator
    worker = Translator(args.lang)
    worker.run()



