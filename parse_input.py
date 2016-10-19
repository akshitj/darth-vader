from pandas import read_excel


def get_input(file_name):
    df = read_excel(open(file_name, 'rb'), sheetname='Without Rates')
    print df.head()