# ta1fukawa/utils

様々なプロジェクトに汎用的に利用できるようなプログラムコードのセット。

汎用的と言っても個人的に使用しない機能は省いているので、誰かの役に立つかどうかはわからない。

- [daemon.py](daemon.py): Pythonのプロジェクトをバックグラウンドで動作させる。ターミナルが終了してもプログラムを続けられるようになる。
- [scheduler.py](scheduler.py): cronのように指定した時間に関数を呼び出す。呼び出し側の親プロセスが必要なので、[daemon.py](daemon.py)と組み合わせるといいかもしれない。
- [ffmpeg.py](ffmpeg.py): ffmpegのラッパー。パスのエスケープはWindows向けになっているので、別環境では要修正。
- [waifu2x.py](waifu2x.py): waifu2x-caffe-cuiのラッパー。
- [silence_remover.py](silence_remover.py): 音声から無音部分を削除する。無音の閾値、最小幅、マージンを指定できる。
