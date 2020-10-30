import os
import re
from grid import Grid

FOLDER_LOCATION = "small_example"
OUTPUT_FILE = "small_output_without_whitespace.txt"

def display_brain(brain, vertical_pixel_resolution, horizontal_pixel_resolution, file=None):
    space = ""
    ans = ""
    for i in range(vertical_pixel_resolution):
        for j in range(horizontal_pixel_resolution):
            ans += str(brain[i][j]) + space if brain[i][j] % 1 == 0 else "X" + space
        ans += "\n"
    if file is None:
        print(ans)
    else:
        with open(file, 'w') as f:
            f.write(ans)


specs_file = open(os.path.join(FOLDER_LOCATION, 'specs.txt'))
for line in specs_file:
    check = re.fullmatch(r"\s*[Vv]ertical pixel resolution: (\d+)\s*", line)
    if check:
        vertical_pixel_resolution = int(check.group(1))
    check = re.fullmatch(r"\s*[Hh]orizontal pixel resolution: (\d+)\s*", line)
    if check:
        horizontal_pixel_resolution = int(check.group(1))
specs_file.close()
assert vertical_pixel_resolution and horizontal_pixel_resolution, "Could not find at least one of vertical and horizontal pixel resolution."

brain = {i: {j: None for j in range(vertical_pixel_resolution)} for i in range(horizontal_pixel_resolution)}
# print(brain)

# read in the critical_raw file
critical_file = open(os.path.join(FOLDER_LOCATION, 'critical_raw.txt'))
for i in range(vertical_pixel_resolution):
    for j in range(horizontal_pixel_resolution):
        char = None
        while char not in ("0", "1"):
            char = critical_file.read(1)
            if not char:
                raise ValueError("Was expecting more values")

        val = int(char)

        if i not in brain:
            brain[i] = {}
        if j not in brain[i]:
            brain[i][j] = None
        brain[i][j] = val

print("Critical area:")
display_brain(brain, vertical_pixel_resolution, horizontal_pixel_resolution)

# determine which ones are bordering - mark them with 0.5
max_horizontal_pixel_index = horizontal_pixel_resolution - 1
max_vertical_pixel_index = vertical_pixel_resolution - 1
TOP_LEFT, TOP, TOP_RIGHT, LEFT, RIGHT, BOTTOM_LEFT, BOTTOM, BOTTOM_RIGHT = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
for i in range(vertical_pixel_resolution):
    for j in range(horizontal_pixel_resolution):
        # only care about non-critical cells
        if brain[i][j] == 0:
            checks = set([TOP_LEFT, TOP, TOP_RIGHT, LEFT, RIGHT, BOTTOM_LEFT, BOTTOM, BOTTOM_RIGHT])
            if i == 0:
                for val in (TOP_LEFT, TOP, TOP_RIGHT):
                    checks.discard(val)
            if j == 0:
                for val in (TOP_LEFT, LEFT, BOTTOM_LEFT):
                    checks.discard(val)

            if i == max_vertical_pixel_index:
                for val in (BOTTOM_LEFT, BOTTOM, BOTTOM_RIGHT):
                    checks.discard(val)

            if j == max_horizontal_pixel_index:
                for val in (BOTTOM_RIGHT, RIGHT, TOP_RIGHT):
                    checks.discard(val)

            bordering_critical = False
            for check in checks:
                i_check, j_check = i + check[0], j + check[1]
                if brain[i_check][j_check] == 1:
                    bordering_critical = True
                    break
            if bordering_critical:
                brain[i][j] = 0.5

print("Border without tumor taken out:")
display_brain(brain, vertical_pixel_resolution, horizontal_pixel_resolution)

# read in the tumor_raw file
tumor_file = open(os.path.join(FOLDER_LOCATION, 'tumor_raw.txt'))
tumor_brain = {i: {j: None for j in range(vertical_pixel_resolution)} for i in range(horizontal_pixel_resolution)}
for i in range(vertical_pixel_resolution):
    for j in range(horizontal_pixel_resolution):
        char = None
        while char not in ("0", "1"):
            char = tumor_file.read(1)
            if not char:
                raise ValueError("Was expecting more values")


        val = int(char)
        if brain[i][j] in (0, 1):
            brain[i][j] = 0
        else:
            if val == 1:
                brain[i][j] = 0
            else:
                brain[i][j] = 1

        tumor_brain[i][j] = val

print("Tumor:")
display_brain(tumor_brain, vertical_pixel_resolution, horizontal_pixel_resolution)

print("Final result:")
display_brain(brain, vertical_pixel_resolution, horizontal_pixel_resolution)
display_brain(brain, vertical_pixel_resolution, horizontal_pixel_resolution, file=OUTPUT_FILE)
