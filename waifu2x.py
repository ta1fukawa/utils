import subprocess

class Waifu2x:
    def __init__(self, waifu2x_path='waifu2x-caffe-cui'):
        self.cmd = []
        self.append([waifu2x_path])

    def append(self, cmd_list):
        for cmd in cmd_list:
            self.cmd.append(str(cmd))

    def run(self):
        subprocess.run(self.cmd)

    def input_(self, path):
        self.append(['-i', path])

    def select_model(self, model):
        self.append(['-m', model])

    def set_scale(self, target_scale, original_scale):
        tw, th = target_scale
        ow, oh = original_scale
        direction = (ow * th) / (oh * tw)

        if direction >= 1:
            self.append(['-w', tw])
        elif direction < 1:
            self.append(['-h', th])

    def select_noise_level(self, level):
        self.append(['-n', level])

    def select_processer(self, processer):
        self.append(['-p', processer])

    def output(self, path):
        self.append(['-o', path])
