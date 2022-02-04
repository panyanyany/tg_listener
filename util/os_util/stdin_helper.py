
def readlines(title):
    lines = []
    print(title)
    while True:
        line = input().strip()
        if line == 'EOT' or line == '':
            break
        lines.append(line)

    return lines