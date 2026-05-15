import sys

def fix_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    with open(filename, 'w') as f:
        for i, line in enumerate(lines):
            # Line 126 is index 125 (1-based to 0-based)
            # The current code:
            # 125:                        if len(parts) < 2:
            # 126:                        raise ValueError(
            # 127:                            "Missing value after 'nb_drones:'"
            # 128:                    )
            # 134:                        raise ValueError(msg)
            
            if i == 125 or i == 126: # line 126 and 127
                f.write("    " + line)
            elif i == 127: # line 128 (closing parenthesis of raise)
                f.write("    " + line)
            elif i == 133: # line 134 (double indented raise inside except)
                f.write(line.replace("                        raise", "                    raise"))
            else:
                f.write(line)

if __name__ == "__main__":
    fix_file(sys.argv[1])
