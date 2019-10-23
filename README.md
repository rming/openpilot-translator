## Openpilot translator

把 Openpilot 项目 提示语 和 界面翻 译成中文版 / 其他语言。


## Help

```bash
$  python translator.py  --help
usage: translator.py [-h] --lang LANG

optional arguments:
  -h, --help            show this help message and exit
  --lang LANG, -l LANG  target language [zhs|zht]
```

## Usage

```bash
# 克隆 openpilot 项目
$ git clone https://github.com/commaai/openpilot

# 克隆 openpilot-apks 项目
$ git clone https://github.com/commaai/openpilot-apks

# 替换指定语言文字
$ python translator.py  --lang zhs

```

## Acknowledgement

Inspired by [dragonpilot](https://github.com/dragonpilot-community/dragonpilot)
