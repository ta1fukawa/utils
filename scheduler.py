import copy
import datetime
import threading
import time
import uuid

from dateutil.relativedelta import relativedelta

class Scheduler:

    thread_dict = dict()

    def set_cron(self, timelist, func, *args, **kwargs):
        cron_id = uuid.uuid4()

        next_dt = datetime.datetime.now() + relativedelta(seconds=1)
        thread = threading.Thread(target=self.__run, args=(
            cron_id, timelist, next_dt, func) + args, kwargs=kwargs)
        self.thread_dict[cron_id] = thread
        thread.start()

        return cron_id

    def remove_cron(self, cron_id):
        if cron_id in self.thread_dict:
            del self.thread_dict[cron_id]

    def remove_cron_all(self):
        self.thread_dict = dict()

    def join(self):
        thread_dict_copy = copy.copy(self.thread_dict)
        self.remove_cron_all()
        for thread in thread_dict_copy.values():
            thread.join()

    def __run(self, cron_id, timelist, now_dt, func, *args, **kwargs):
        tgt_dt = self.__get_next_dt(timelist, now_dt=now_dt)

        if tgt_dt is None:
            del self.thread_dict[cron_id]
            return

        diff_seconds = (tgt_dt.replace(microsecond=0) -
                        datetime.datetime.now()).total_seconds()
        time.sleep(max(diff_seconds, 0))

        if not cron_id in self.thread_dict:
            return

        func(datetime.datetime.now(), *args, **kwargs)

        next_dt = tgt_dt + relativedelta(seconds=1)
        thread = threading.Thread(target=self.__run, args=(
            cron_id, timelist, next_dt, func) + args, kwargs=kwargs)
        self.thread_dict[cron_id] = thread
        thread.start()

    def __get_next_dt(self, tgt_tl, now_dt=None):
        if now_dt is None:
            now_dt = datetime.datetime.now()

        now_tl = [now_dt.year, now_dt.month, now_dt.day,
                  now_dt.hour, now_dt.minute, now_dt.second]
        zero_tl = [1, 1, 1, 0, 0, 0]
        next_tl = copy.copy(tgt_tl)

        free_idx = None
        future_flag = False
        for i in range(len(now_tl)):
            # now or future
            if next_tl[i] is None:
                # future
                if future_flag:
                    next_tl[i] = zero_tl[i]
                # now or future
                else:
                    next_tl[i] = now_tl[i]
                    free_idx = i

            # past or future
            if next_tl[i] < now_tl[i]:
                # past
                if free_idx is None:
                    return

                # future
                if not future_flag:
                    future_flag = True
                    next_tl[free_idx] += 1

            # future
            if next_tl[i] > now_tl[i]:
                free_idx = -1
                future_flag = True

        next_dt = now_dt + relativedelta(years=(next_tl[0] - now_tl[0]), months=(next_tl[1] - now_tl[1]), days=(
            next_tl[2] - now_tl[2]), hours=(next_tl[3] - now_tl[3]), minutes=(next_tl[4] - now_tl[4]), seconds=(next_tl[5] - now_tl[5]))
        return next_dt
