def main():
    f = open('sample.txt', 'r')
    out = open('part1.txt', 'w')
    lines = f.readlines()
    branches = [None] * 1024
    just_branches = []

    for i in range(0, len(lines) - 1):
        pc = lines[i].strip()
        nex = lines[i + 1].strip()
        pc_val = int(pc, 16)
        nex_val = int(nex, 16)
        if (nex_val != pc_val + 4):
            state = 0
            if branches[(pc_val & 0xFFC) >> 2] is not None:
                state = branches[(pc_val & 0xFFC) >> 2][2] + 1
            branches[(pc_val & 0xFFC) >> 2] = (pc_val, nex_val, state)
            if pc_val not in just_branches:
                just_branches.append(pc_val)

    for branch in just_branches:
        out.write("Branch| %-10x   Entry| PC: %-10x INDEX: %-10d   TARGET: %-10x" %
                  (branch, branches[(branch & 0xFFC) >> 2][0], (branch & 0xFFC) >> 2, branches[(branch & 0xFFC) >> 2][1]))
        if branches[(branch & 0xFFC) >> 2][0] != branch:
            out.write("     OVERWRITE")
        out.write('\n')


if __name__ == "__main__":
    main()
