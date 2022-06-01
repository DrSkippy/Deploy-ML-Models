file_path = "../data/adult_earning/"
hfile = file_path + "adult.names"

def get_header():
    header = []
    with open(hfile, "r") as infile:
        for line in infile:
            if line.startswith("|") or line.startswith(">") or line.startswith("\n"):
                continue
            else:
                header.append(line.split(":")[-1])
    header.append("class")
    return header
