import csv

file_path = "500_rolling_stones_2012.txt"
dest_path = "albums.csv"


def read_file(path):
    result = []
    with open(path, 'r') as file:
        raw_strings = file.readlines()
    for line in raw_strings:
        line = line.strip()
        line = line.split(sep=',', maxsplit=2)
        result.append(line)

    return result


def write_to_csv(table):
    with open(dest_path, 'w', newline='') as csvfile:
        spam_writer = csv.writer(csvfile, delimiter=' ')
        for line in table:
            spam_writer.writerow(line)


def clear_titles(table):
    for line in table:
        line[1] = line[1].strip()
        line[1] = line[1].strip("'")


def main():
    table = read_file(file_path)
    clear_titles(table)
    write_to_csv(table)


if __name__ == '__main__':
    main()
