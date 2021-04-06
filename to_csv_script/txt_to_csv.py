import csv

file_path = "500_rolling_stones_2012_sp_some_deleted.txt"
dest_path = "../album_info/albums.csv"


def read_file(path, result):
    with open(path, 'r') as file:
        raw_strings = file.readlines()  # reading "raw" text file

    for line in raw_strings:  # processing it into computer-readable format
        line = line.strip()
        line = line.split(sep=',', maxsplit=1)  # split into artis and title
        result.append(line)

    return result


def write_to_csv(table):
    with open(dest_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=";")
        for line in table:
            csv_writer.writerow(line)


def clear_titles(table):  # further text cleaning
    for line in table:
        line[1] = line[1].strip()
        line[1] = line[1].removeprefix("'").removesuffix("'")  # removing "double quotation"


def main():
    table = read_file(file_path, [["Artist", "Title"]])
    clear_titles(table)
    #write_to_csv(table)   # There are some issues with the text file - don't write to csv until the errors are fixed


if __name__ == '__main__':
    main()
