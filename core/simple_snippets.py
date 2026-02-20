def compare_version(ver1, ver2):
    version1_parts = ver1.split('.')
    version2_parts = ver2.split('.')

    for i in range(max(len(version1_parts), len(version2_parts))):
        v1 = int(version1_parts[i]) if i < len(version1_parts) else 0
        v2 = int(version2_parts[i]) if i < len(version2_parts) else 0

        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1

    return 0


def is_subsequence(s, t):
    t_index = 0
    s_index = 0
    while t_index < len(t) and s_index < len(s):
        if s[s_index] == t[t_index]:
            s_index += 1
        t_index += 1
    return s_index == len(s)


def debugprint(printvar):  # wip
    print(f'{printvar}')
    for attr in dir(printvar):
        print('debugprint.%s = %r' % (attr, getattr(printvar, attr)))
    return


