

from split_pinyin import get_split_py

from Pinyin2Hanzi import DefaultDagParams, dag


class Pinyin2Hanzi:
    def __init__(self):
        self._dagparams = DefaultDagParams()

    def _py2hz_dag(self, pinyin_list):
        if len(pinyin_list) == 1:
            num = 1000
        elif len(pinyin_list) == 2:
            num = 20
        elif len(pinyin_list) == 3:
            num = 10
        elif len(pinyin_list) <= 5:
            num = 5
        elif len(pinyin_list) <= 7:
            num = 3
        else:
            num = 1
        return dag(self._dagparams, pinyin_list, num, True)

    def py2hz(self, text):
        assert isinstance(text, str)
        match, completion, other = get_split_py(text)
        ret = []
        if match:
            for m in match:
                for item in self._py2hz_dag(m):
                    ret.append([m, (item.path, item.score), 0])
        elif completion:
            for c in completion:
                for item in self._py2hz_dag(c):
                    ret.append([c, (item.path, item.score), 1])
        elif other:
            for o in other:
                for item in self._py2hz_dag(o[:-1]):
                    ret.append([o, (item.path, item.score), 2])
        if ret:
            min_score = min(r[1][1] for r in ret)

            def func(r):
                if r[-1] in [0, 1]:
                    return len(r[0]) * (-min_score) - r[1][1]
                return len(r[0][-1]) * len(text) * (-min_score) + len(r[0][:-1]) * (-min_score) - r[1][1]

            ret = sorted(ret, key=func)
        return ret


if __name__ == '__main__':

    pred = Pinyin2Hanzi().py2hz('jintiantianqizenmeyang')
    [print(p) for p in pred]


