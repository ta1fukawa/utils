# 複数インスタンスでの同時実行を防止するコード
# - OS機能の一つであるファイルの排他ロックを利用する
# - fcntlを使用するためUNIX/Linux上でのみ動作する

import fcntl

def exclusive_execution(lockfile, func, *args, **kwargs):
    with open(lockfile, 'w') as f:
        try:
            # 排他モードでファイルをロック
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            # ロックに失敗＝すでに実行中
            return None
        # ロックに成功＝他で実行されていない
        ret = func(*args, **kwargs)
        # ロックを解除
        fcntl.flock(f, fcntl.LOCK_UN)
    return ret

# テストコード
if __name__ == '__main__':
    import time
    if exclusive_execution('.lock', lambda: (print('Running.'), time.sleep(10))):
        print('Finished!')
    else:
        print('Another instance is running.')
