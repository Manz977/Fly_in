import sys

def fix_parser(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    with open(filename, 'w') as f:
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # E117 over-indented at 126 and surrounding
            if "if len(parts) < 2:" in line:
                f.write(line)
                # Next two lines are the raise and its content
                f.write(lines[i+1].replace("        raise", "    raise"))
                f.write(lines[i+2].replace("            \"", "        \""))
                f.write(lines[i+3].replace("        )", "    )"))
                i += 4
                continue
            
            # E303 too many blank lines
            # If line is blank and next one is blank, skip if it exceeds limit
            # Simple approach: skip if line is just whitespace and previous was also empty-ish
            
            # W391 blank line at end of file
            if i == len(lines) - 1 and line.strip() == "":
                pass # skip last blank line
            else:
                f.write(line)
            i += 1

if __name__ == "__main__":
    fix_parser("parser/parser.py")
