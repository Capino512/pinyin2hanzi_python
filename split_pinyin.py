

from Pinyin2Hanzi.util import __pinyin, remove_tone, normlize_pinyin


__max_length = max(len(__py) for __py in __pinyin)


def parse_py(text): # string, lower, remove_tone, normlize_pinyin
    def parse_one(start):
        py_list = []
        no_match = True
        for i in range(start, min(len(text), start + __max_length)):
            i += 1
            if text[start:i] in __pinyin:
                py_list.append([start, i])
                no_match = False
        if no_match:
            py_list.append([start, None])
        return py_list

    def parse_all(last_list):
        current_list = []
        for ret in last_list:
            start, end = ret[-1]
            if end is None:
                current_list.append(ret)
            else:
                py_list = parse_one(end)
                for pl in py_list:
                    current_list.append(ret + [pl])
        return current_list

    result_list = [[[None, 0]]]
    while True:
        result_list = parse_all(result_list)
        if all(x[-1][1] is None for x in result_list):
            break
    return result_list


def complete_py(text):
    return list(filter(lambda py: text == py[:len(text)], __pinyin))


def get_split_py(text):
    match = []
    completion = []
    excessive_split = []
    other = []

    py_text = remove_tone(text.lower())
    py_text = normlize_pinyin(py_text)

    for r in parse_py(py_text):
        ret = []
        for start, end in r[1:]:
            ret.append(py_text[start:end])
        if ret[-1] == '':
            match.append(ret if len(ret) == 1 else ret[:-1])
        else:
            completed = complete_py(ret[-1])
            if completed:
                for c in completed:
                    completion.append(ret[:-1] + [c])
                continue
            if len(ret) > 1 and ret[-2] + ret[-1] in __pinyin:
                excessive_split.append(ret)
                continue
            other.append(ret)

    match = sorted(match, key=lambda x: len(x))
    completion = sorted(completion, key=lambda x: len(x))
    # excessive_split = sorted(excessive_split, key=lambda x: len(x))
    other = sorted(other, key=lambda x: len(x[-1]) * len(py_text) + len(x))

    return match, completion, other


if __name__ == '__main__':

    m, c, o = get_split_py('jintiantianqizenmeyang')
    [print(mm) for mm in m]
