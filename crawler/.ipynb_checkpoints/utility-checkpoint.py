def text2list(s):
    re = {}
    for i in s.strip().split("\n"):
        j = i.split(":")
        re[j[0].strip()] = j[1].strip()
    return re