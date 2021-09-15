import sys
sys.path.append('..')

from ffmpeg import Video, Encoder, Filter, FF_Utils

font_path   = '/your/font/path.otf'
input_path  = '/your/video/path.mp4'
output_path = '/output/video/path.mp4'
target_scale = (1920, 1080)
start_time = 0.00
end_time   = None

start_time = FF_Utils.time_decode(start_time)
end_time = FF_Utils.time_decode(end_time)

video = Video(input_path)
original_scale = video.get_scale()
loudness = video.get_loudness(-14, -3, 11, start=start_time, end=end_time)

filter_ = Filter()
filter_.norm_loudness(-14, -3, 11, loudness['input_i'], loudness['input_tp'], loudness['input_lra'], loudness['input_thresh'], loudness['target_offset'])
filter_.pad_to_fit_aspect(target_scale, original_scale, 'Black')
filter_.change_scale(target_scale, original_scale)

encoder = Encoder(all_flag='-y')
encoder.select_time_range(start=start_time, end=end_time)
encoder.input_(input_path)
encoder.append(['-map_chapters', '-1'])
encoder.video_option(frame_rate='30000/1001')
encoder.map_option(stream_type='v')
encoder.audio_option(sampling_rate=48000, n_channel=2)
encoder.map_option(stream_type='a')
encoder.codec_option('h264_nvenc', stream_type='v')
encoder.fileter_option(filter_.get_filter_text())
encoder.output(output_path)
encoder.append(['-hide_banner', '-loglevel', 'error'])
# print('"' + '" "'.join(encoder.cmd) + '"')
encoder.run()
