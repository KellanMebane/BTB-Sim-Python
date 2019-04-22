class Entry:
    def __init__(self, pc, target):
        self.state = 3
        self.pc = pc
        self.target = target

    def match_target(self, newTarget):
        return self.target == newTarget

    def match_pc(self, newPC):
        return self.pc == newPC

    def prediction(self):
        return self.state > 1

    def right(self):
        if self.state < 3:
            if self.state == 1:
                self.state = 2
            else:
                self.state += 1

    def wrong(self):
        if self.state > 0:
            self.state -= 1

    def format_entry(self):
        return '%d  %x  %x  %s' % (
            calculate_index(self.pc),
            self.pc, self.target, format(self.state, 'b'))


def calculate_index(pc):
    return (pc & 0xFFC) >> 2


def is_branch(pc, target):
    return (pc + 4) != target


class BTB:
    def __init__(self):
        self.branches = [None] * 1024  # BTB itself
        # holds a list of all branches (even overwritten branches)
        self.just_branches = []
        self.hits = 0
        self.misses = 0
        self.right = 0
        self.wrong = 0
        self.collisions = 0
        self.wrong_address = 0
        self.instructions = 1
        self.taken = 0

    def does_entry_exist(self, pc):
        if self.branches[calculate_index(pc)] is None:
            return False
        if self.branches[calculate_index(pc)].match_pc(pc):
            return True
        return False

    def run_on_file(self, filename):
        f = open(filename, 'r')
        lines = f.readlines()

        # grab addresses from file (2 at a time)
        for i in range(0, len(lines) - 1):
            # parse input and convert to integers
            pc = lines[i].strip()
            nex = lines[i + 1].strip()
            pc_val = int(pc, 16)  # current PC
            nex_val = int(nex, 16)  # next PC

            self.update(pc_val, nex_val)

        f.close()

    def print_branches(self):
        out = open('part1.txt', 'w')  # output file for part 1
        for branch in self.just_branches:
            # print branch information
            out.write("Branch| %-10x   Entry| PC: %-10x INDEX: %-10d   TARGET: %-10x" %
                      (branch, self.branches[calculate_index(branch)][0],
                       calculate_index(branch), self.branches[calculate_index(branch)][1]))

            # if branch has conflict add "OVERWRITE" to output
            if self.branches[calculate_index(branch)][0] != branch:
                out.write("     OVERWRITE")
            out.write('\n')
        out.close()

    def update(self, pc, target):
        self.instructions += 1

        is_taken = is_branch(pc, target)
        if is_taken is True:
            self.taken += 1

        index = calculate_index(pc)
        # is pc in BTB?
        if self.does_entry_exist(pc):
            # yes
            self.hits += 1

            # is prediction taken?
            if self.branches[index].prediction():
                # right target?
                if self.branches[index].target == target:
                    self.right += 1
                    self.branches[index].right()
                # wrong target?
                else:
                    self.wrong += 1
                    self.branches[index].wrong()
                    # is it a branch still?
                    if is_branch(pc, target):
                        self.wrong_address += 1
                        # update BTB because wrong address
                        self.branches[index] = Entry(pc, target)
            # prediction says not taken
            else:
                if is_taken:
                    self.wrong += 1
                    self.branches[index].wrong()
                else:
                    self.right += 1
                    self.branches[index].right()
        # not in BTB
        else:
            # is it a branch?
            if is_taken:
                # yes
                self.misses += 1
                # already exists but wrong PC
                if self.branches[index] is not None:
                    self.collisions += 1
                self.branches[index] = Entry(pc, target)  # enter into BTB

    def format_info(self):
        x = "Number of hits: %d\nNumber of misses: %d\nNumber of right: %d\nNumber of wrong: %d\n" % (
            self.hits, self.misses, self.right, self.wrong)
        x += "Wrong predicted adr: %d\nNumber of collisions/conflicts: %d\nHit rate: %f%%\n" % (
            self.wrong_address, self.collisions,
            self.hits / (self.hits + self.misses) * 100)
        x += "Accuracy: %f%%\nWrong address prediction: %f%%\nCPI with no BTB: %f\nCPI with BTB: %f" % (
            (self.right / self.hits) *
            100, (self.wrong_address / self.hits) * 100,
            (self.taken + self.instructions) / self.instructions,
            (self.wrong + self.misses + self.instructions) / self.instructions)
        return x

def main():
    btb = BTB()
    btb.run_on_file('sample.txt')
    out = open('state_machine_class.txt', 'w')
    out.write("%s" % (btb.format_info()))
    out.write("\n\nEntry    PC  Target  Prediction\n")
    for entry in btb.branches:
        if entry is not None:
            out.write("%s\n" % (entry.format_entry()))
    # btb.print_branches()


if __name__ == "__main__":
    main()
