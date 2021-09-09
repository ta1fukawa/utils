import subprocess
import os
import json
import re

class Video:
    def __init__(self, path, ffprobe_path='ffprobe'):
        self.path = path
        if not os.path.isfile(self.path):
            raise Exception('Custom Error: File was not found.')

        proc = subprocess.run([ffprobe_path, '-i', self.path, '-show_streams', '-of', 'json'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
        self.streams_info = json.loads(proc.stdout)['streams']

    def __get_video_stream(self):
        for stream in self.streams_info:
            if stream['codec_type'] == 'video':
                return stream
        
        raise Exception('Custom Error: Video stream was not found.')

    def __get_audio_stream(self):
        for stream in self.streams_info:
            if stream['codec_type'] == 'audio':
                return stream
        
        raise Exception('Custom Error: Audio stream was not found.')

    def get_scale(self):
        stream = self.__get_video_stream()
        scale = (stream['width'], stream['height'])
        return scale
    
    def get_loudness(self, i, tp, lra, start=None, end=None, ffmpeg_path='ffmpeg'):
        cmd = list()
        cmd.extend([str(ffmpeg_path)])
        cmd.extend(['-ss', str(start)] if start is not None else [])
        cmd.extend(['-to', str(end)] if end is not None else [])
        cmd.extend(['-i', self.path, '-af', f'loudnorm=I={i}:TP={tp}:LRA={lra}:print_format=json', '-vn', '-f', 'null', '-'])

        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
        line_list = proc.stderr.splitlines()
        json_text = '\n'.join(line_list[len(line_list) - list(reversed(line_list)).index('{') - 1:])
        info = json.loads(json_text)
        return info

    def get_framerate(self):
        stream = self.__get_video_stream()
        framerate = stream['r_frame_rate']
        return framerate

    def get_audio_format(self):
        stream = self.__get_video_stream()
        format_ = stream['codec_name']
        return format_


class Encoder:
    def __init__(self, ffmpeg_path='ffmpeg', all_flag='-n'):
        self.cmd = []
        self.append([ffmpeg_path])
        self.append([all_flag])

    def append(self, cmd_list):
        for cmd in cmd_list:
            self.cmd.append(str(cmd))

    def run(self):
        subprocess.run(self.cmd, encoding='utf-8')

    def select_format(self, format_):
        self.append(['-f', format_])

    def select_time_range(self, start=None, duration=None, end=None):
        if duration is not None:
            if start is not None:
                end = start + duration
            elif end is not None:
                start = end - duration
            else:
                raise Exception()
        
        if start is not None:
            self.append(['-ss', start])
        if end is not None:
            self.append(['-to', end])

    def input_(self, path):
        self.append(['-i', path])

    def video_option(self, frame_rate=None, pass_=None):
        if frame_rate is not None:
            self.append(['-r', frame_rate])
        
        if pass_ is not None:
            self.append(['-pass', pass_])

    def audio_option(self, sampling_rate=None, n_channel=None):
        if sampling_rate is not None:
            self.append(['-ar', sampling_rate])
        
        if n_channel is not None:
            self.append(['-ac', n_channel])

    def map_option(self, file_no=0, stream_type=None, stream_no=None, ignore_error=False):
        # Stream type: [v] Video, [a] Audio, [s] Subtitle, [d] Data, [t] Attachments
        specifier = f'{file_no}'
        specifier += f':{stream_type}' if stream_type is not None else ''
        specifier += f':{stream_no}' if stream_no is not None else ''
        specifier += '?' if ignore_error else ''

        self.append(['-map', specifier])

    def metadate_option(self, metadata):
        self.append(['-metadata', metadata])

    def codec_option(self, codec, stream_type=None, stream_no=None):
        specifier = ''
        specifier += f':{stream_type}' if stream_type is not None else ''
        specifier += f':{stream_no}' if stream_no is not None else ''

        self.append([f'-c{specifier}', codec])

    def fileter_option(self, filter_):
        self.append(['-filter_complex', filter_])

    def output(self, path):
        self.append([path])

class Filter:
    def __init__(self):
        self.video_filter_list = []
        self.audio_filter_list = []

    def get_filter_text(self):
        video_filter_text = ','.join(self.video_filter_list)
        audio_filter_text = ','.join(self.audio_filter_list)
        filter_text = ';'.join(filter(None, [video_filter_text, audio_filter_text]))
        return filter_text

    def pad_to_fit_aspect(self, target_scale, original_scale, color):
        tw, th = target_scale
        ow, oh = original_scale
        direction = (ow * th) / (oh * tw)

        if direction > 1:
            filter_ = f'pad=iw:iw*{th}/{tw}:0:(ih-oh)/2:{color}'
        elif direction < 1:
            filter_ = f'pad=ih*{tw}/{th}:ih:(iw-ow)/2:0:{color}'
        else:
            return

        self.video_filter_list.append(filter_)

    def change_scale(self, target_scale, original_scale):
        tw, th = target_scale
        ow, oh = original_scale

        if tw != ow or th != oh:
            filter_ = f'scale={tw}:{th}'
        else:
            return

        self.video_filter_list.append(filter_)

    def interpolate_60fps(self):
        filter_ = f'minterpolate=60:2:0:1:8:16:32:0:1:5'
        self.video_filter_list.append(filter_)

    def draw_text(self, text, pos_x, pos_y, font_path=None, font_size=None, font_color=None, border_width=None, border_color=None, alpha=None):
        filter_ = f'drawtext=text=\'{text}\':x={pos_x}:y={pos_y}'
        filter_ += f':fontfile={font_path}' if font_path is not None else ''
        filter_ += f':fontsize={font_size}' if font_size is not None else ''
        filter_ += f':fontcolor={font_color}' if font_color is not None else ''
        filter_ += f':borderw={border_width}' if border_width is not None else ''
        filter_ += f':bordercolor={border_color}' if border_color is not None else ''
        filter_ += f':alpha={alpha}' if alpha is not None else ''

        self.video_filter_list.append(filter_)

    def draw_box(self, pox_x, pos_y, width, height, border_color, border_width):
        filter_ = f'drawbox={pox_x}:{pos_y}:{width}:{height}:{border_color}:{border_width}'
        self.video_filter_list.append(filter_)


    def norm_loudness(self, i, tp, lra, ref_i, ref_tp, ref_lra, ref_thresh, offset):
        filter_ = f'loudnorm=I={i}:TP={tp}:LRA={lra}:measured_I={ref_i}:measured_TP={ref_tp}:measured_LRA={ref_lra}:measured_thresh={ref_thresh}:offset={offset}'
        self.audio_filter_list.append(filter_)

class FF_Utils:
    @staticmethod
    def get_text_size(text, font_path, font_size, border_width=None, ffmpeg_path='ffmpeg'):
        filter_ = f'drawtext=fontfile={font_path}:fontsize={font_size}:x=0*print(tw):y=0*print(th):text=\'{text}\''
        filter_ += f':borderw={border_width}' if border_width is not None else ''

        cmd = [ffmpeg_path, '-f', 'lavfi', '-i', 'color=size=16x16:rate=1', '-t', '1', '-vf', filter_, '-f', 'null', '-']
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        size = [int(float(item)) for item in [line for line in proc.stderr.splitlines() if '.000000' in line][-3:-1]]
        return size
        
    @staticmethod
    def escape_path(text):
        while True:
            last_text = text

            text = text.replace('\\', '＼')
            text = text.replace('/', '／')
            text = text.replace(':', '：')
            text = text.replace('*', '＊')
            text = text.replace('?', '？')
            text = text.replace('"', '”')
            text = text.replace('<', '＜')
            text = text.replace('>', '＞')
            text = text.replace('|', '｜')

            if last_text == text:
                break

        return text

    @staticmethod
    def escape_drawtext(text):
        while True:
            last_text = text

            text = text.replace('\'', '<<single-quote>>')
            text = text.replace('"', '<<double-quote>>')
            text = text.replace(',', '<<comma>>')
            text = text.replace('\\', '<<backslash>>')
            text = text.replace(':', '<<colon>>')
            text = text.replace('{', '<<left-bracket>>')
            text = text.replace('}', '<<right-bracket>>')

            if last_text == text:
                break

        while True:
            last_text = text

            text = text.replace('<<single-quote>>', '\'\\\\\\\'\'')
            text = text.replace('<<double-quote>>', '\'\\\\\\"\'')
            text = text.replace('<<comma>>', '\\,')
            text = text.replace('<<backslash>>', '\\\\\\\\')
            text = text.replace('<<colon>>', '\\\\\\:')
            text = text.replace('<<left-bracket>>', '\\\\\\{')
            text = text.replace('<<right-bracket>>', '\\\\\\}')

            if last_text == text:
                break

        return text

    @staticmethod
    def extract_custom_format(text, bank):
        while True:
            last_text = text

            for key in bank.keys():
                text = text.replace(f'<<{key}>>', bank[key])
                text = text.replace(f'<<{key}:path>>', FF_Utils.escape_path(bank[key]))
                text = text.replace(f'<<{key}:text>>', FF_Utils.escape_drawtext(bank[key]))

            if last_text == text:
                break

        return text

    @staticmethod
    def time_decode(text):
        time_list = re.findall(r'^(\d+):(\d{2}).(\d{3})$', text)[0]
        time = int(time_list[0]) * 60 + int(time_list[1]) + int(time_list[2]) * 1e-3
        return time
      
