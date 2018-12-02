from PIL import Image
import argparse

# 定义参数，参数默认未字符行，其他类型需要单独定义type
argparser = argparse.ArgumentParser()
argparser.add_argument('file')
argparser.add_argument('--width', type=int, default=80)
argparser.add_argument('--height', type=int, default=80)
argparser.add_argument('-o', '--output')

# 参数解析，赋值
args = argparser.parse_args()
IMG = args.file
WIDTH = args.width
HEIGHT = args.height
OUTPUT = args.output

# 像素RGB转字符


def get_char(r, g, b, alpha=256):
    chars = list(
        "@#$%QWERTYUIOPASDFGHJKLZXCVBNMasdfghjklqwertyuiopzxcvbnm^*~+_/;., ")
    gray = 0.2126 * r + 0.7152 * g + 0.0722 * b
    length = len(chars)
    if alpha == 0:
        return ' '
    return chars[int((length*gray)/alpha)]


# 主函数
if __name__ == "__main__":
    # 读取图片
    im = Image.open(IMG)
    # 图片重定义大小
    im = im.resize((WIDTH, HEIGHT), Image.NEAREST)
    txt = ''
    for i in range(HEIGHT):
        for j in range(WIDTH):
            txt += get_char(*im.getpixel((j, i)))
        txt += '\n'
    print(txt)
    # 文本输出
    if OUTPUT:
        with open(OUTPUT, 'w') as f:
            f.write(txt)
    else:
        with open('output.txt', 'w') as f:
            f.write(txt)
