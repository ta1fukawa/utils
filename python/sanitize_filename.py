# Windows/Linux系に対応したファイル名正規化コード
# - ファイル名に使用不可能な文字を全角文字に置き換える
# - replace_toが指定されたときは、その文字に置き換える

def sanitize_filename(filename, replace_to=None):
    replacements = {'\\': '¥', '/': '／', ':': '：', '*': '＊', '?': '？', '"': '”', '<': '＜', '>': '＞', '|': '｜', '\0': ''}
    if replace_to is not None:
        replacements = {k: replace_to for k in replacements}
    for original, replacement in replacements.items():
        filename = filename.replace(original, replacement)
    return filename

# テストコード
if __name__ == '__main__':
    print(sanitize_filename('He says: "knowledge is <power>."'))
