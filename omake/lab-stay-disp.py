import os
import json
import tkinter as tk
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(2)

class App:
    def __init__(self, data_filepath):
        self.data_filepath = data_filepath  # 名簿のJSONファイルのパス
        self.update_time = None             # 名簿の更新時刻
        self.zaisitsu_gakubans = {}         # 在室学生の学籍番号
        self.grade_area = {}                # 学年領域

        self.max_cols = 5  # 名前の最大列数（ディスプレイによって調整する）

        self.grades = ['teacher', 'd', 'm2', 'm1', 'b4', 'b3']

        self.grade_title = {
            'teacher': '教員',
            'd': 'Dr.',
            'm2': 'M2',
            'm1': 'M1',
            'b4': 'B4',
            'b3': 'B3',
        }

        self.color_map = {
            'teacher': { 'fg': '#FFFFFF', 'bg': '#429324' },
            'd': { 'fg': '#FFFFFF', 'bg': '#029354'},
            'm2': { 'fg': '#FFFFFF', 'bg': '#028E62'},
            'm1': { 'fg': '#FFFFFF', 'bg': '#037970'},
            'b4': { 'fg': '#FFFFFF', 'bg': '#03637E'},
            'b3': { 'fg': '#FFFFFF', 'bg': '#034E7C'},
        }

        self.window = tk.Tk()
        self.window.attributes('-fullscreen', True)  
        self.fullScreenState = False
        self.window.bind("<F11>", self.toggleFullScreen)
        self.window.bind("<Escape>", self.quit)

        screen_width = self.window.winfo_screenwidth()
        if screen_width >= 3840:
            self.display_rate = 4
        elif screen_width >= 2560:
            self.display_rate = 3
        elif screen_width >= 1920:
            self.display_rate = 2
        else:
            self.display_rate = 1

        self.root_frame = tk.Frame(self.window, background='#222222')
        self.root_frame.pack(fill=tk.BOTH, expand=True)

        self.container = tk.Frame(self.root_frame, background='#222222')
        self.container.pack(fill=tk.BOTH, expand=True, padx=20 * self.display_rate, pady=10 * self.display_rate)

        self.head_area = tk.Frame(self.container, background='#222222')
        self.head_area.pack(side=tk.TOP, fill=tk.X)

        self.title = tk.Label(self.head_area, text='神野研究室　在室状況', font=('Noto Sans CJK JP DemiLight', 20 * self.display_rate), background='#222222', foreground='#FFFFFF')
        self.title.pack(side=tk.LEFT, padx=(0, 20 * self.display_rate))

        self.ninzu_label = tk.Label(self.head_area, text='現在0人', font=('Noto Sans CJK JP Light', 15 * self.display_rate), background='#222222', foreground='#DDDDDD')
        self.ninzu_label.pack(side=tk.RIGHT, padx=(20 * self.display_rate, 0))

        self.check_update()
        self.window.mainloop()

    def toggleFullScreen(self, event):
        self.fullScreenState = not self.fullScreenState
        self.window.attributes("-fullscreen", self.fullScreenState)

    def quit(self, event):
        self.window.quit()
        self.window.destroy()

    def check_update(self):
        update_time = os.path.getmtime(self.data_filepath)
        if self.update_time != update_time:
            self.update_time = update_time
            try:
                self.update_data()
            except json.decoder.JSONDecodeError:
                print('JSONDecodeError')
                pass
        self.window.after(1000, self.check_update)

    def update_data(self):
        with open(self.data_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for gakuban in list(self.zaisitsu_gakubans.keys()):
            if gakuban not in data:
                # 名簿から削除された時
                self.remove_item(gakuban)

        for gakuban, person in data.items():
            if person['stay'] == 1 and gakuban not in self.zaisitsu_gakubans:
                # 新たに在室した時
                self.add_item(gakuban, person)

            elif person['stay'] == 0 and gakuban in self.zaisitsu_gakubans:
                # 退出した時
                self.remove_item(gakuban)

        # 現在の在室人数を表示
        self.ninzu_label.configure(text='現在 {} 人'.format(len(self.zaisitsu_gakubans)))

    def add_item(self, gakuban, person):
        if person['grade'] not in self.grade_area:
            # その学年の在室がまだないとき

            # その学年の挿入先を探す（一つ下の学年を見つける）
            after_area = None
            for grade in self.grades[::-1]:
                if grade in self.grade_area:
                    after_area = self.grade_area[grade]

                if grade == person['grade']:
                    break

            # 学年のフレームを作成
            grade_area = tk.Frame(self.container, background='#222222')
            grade_area.pack(before=after_area, side=tk.TOP, fill=tk.X, pady=(12 * self.display_rate, 0))
            self.grade_area[person['grade']] = grade_area

            # 学年のタイトルを作成
            grade_title = tk.Label(grade_area, text=self.grade_title[person['grade']], font=('Noto Sans CJK JP Thin', 10 * self.display_rate), background='#222222', foreground=self.color_map[person['grade']]['fg'], width=1 * self.display_rate)
            grade_title.pack(side=tk.LEFT, padx=(0, 20 * self.display_rate))

            # 学年の名前領域を作成
            grade_grid = tk.Frame(grade_area, background='#222222')
            grade_grid.pack(side=tk.LEFT, fill=tk.X, padx=(20 * self.display_rate, 0))

        # 学年の名前領域
        grade_grid = self.grade_area[person['grade']].winfo_children()[-1]

        # 名前を作成
        label = tk.Canvas(
            grade_grid,
            width=160 * self.display_rate,
            height=36 * self.display_rate,
            background=self.color_map[person['grade']]['bg'],
            highlightthickness=0,
        )
        label.create_text(
            80 * self.display_rate,
            18 * self.display_rate,
            text=person['name'],
            font=('Noto Sans CJK JP Medium', 12 * self.display_rate),
            fill=self.color_map[person['grade']]['fg'],
        )
        label.grid(
            row=(len(grade_grid.winfo_children()) - 1) // self.max_cols,
            column=(len(grade_grid.winfo_children()) - 1) % self.max_cols,
            padx=(0, 8 * self.display_rate),
            pady=4 * self.display_rate,
        )
        self.zaisitsu_gakubans[gakuban] = label

    def remove_item(self, gakuban):
        label = self.zaisitsu_gakubans[gakuban]
        grade_grid = label.master
        grade_area = grade_grid.master
            
        # 名前を見つけて削除
        number = grade_grid.winfo_children().index(label)
        label.destroy()
        del self.zaisitsu_gakubans[gakuban]

        # 後ろの名前を一つずつ前にシフト
        for number in range(number, len(grade_grid.winfo_children())):
            label = grade_grid.winfo_children()[number]
            label.grid(
                row=number // self.max_cols,
                column=number % self.max_cols,
                padx=(0, 8 * self.display_rate),
                pady=4 * self.display_rate,
            )

        # 学年の名前領域が空になったら学年ごと削除
        if len(grade_grid.winfo_children()) == 0:
            grade_area.destroy()
            for grade in self.grades:
                if grade in self.grade_area and self.grade_area[grade] == grade_area:
                    del self.grade_area[grade]
                    break

if __name__ == '__main__':
    app = App('data.json')  
