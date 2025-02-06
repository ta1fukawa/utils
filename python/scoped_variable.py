# スコープを限定した変数を定義するコード
# - コードの可読性を向上し、バグを抑制するために使用する

from contextlib import contextmanager

@contextmanager
def scoped(value):
    yield value

# テストコード
if __name__ == '__main__':
    with scoped('Hello') as v:
        print(v)
