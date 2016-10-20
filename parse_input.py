import pandas as pd


def find_substr_idx(sub_str, list):
    for idx, s in enumerate(list):
        if isinstance(s, unicode) and sub_str in s:
            return idx
    return -1


def get_input(file_name, planData):
    """

    :param file_name:
    :param planData: globals.PlanData
    :return:
    """
    df = pd.read_excel(open(file_name, 'rb'), sheetname='Without Rates')
    day_parts = df.ix[:, 0].tolist()
    morning_idx = find_substr_idx("Morning", day_parts)
    afternoon_idx = find_substr_idx("Afternoon", day_parts)
    morning_df = df.ix[morning_idx + 1: afternoon_idx - 2, :]
    spot_lengths = morning_df.ix[:, 1].tolist()[1:-1]
    spot_lengths = map(int, spot_lengths)
    print "spot lengths are: ", spot_lengths
    revenues = morning_df.ix[:, 2].tolist()[1:-1]
    revenues = map(int, revenues)
    planData.fill_items(spot_lengths, revenues)

def write_output(in_file_name, out_file_name, planData):
    """

    :param in_file_name:
    :param out_file_name:
    :param planData: globals.PlanData
    :return:
    """
    df = pd.read_excel(open(in_file_name, 'rb'), sheetname='Without Rates')
    day_parts = df.ix[:, 0].tolist()
    morning_idx = find_substr_idx("Morning", day_parts)
    afternoon_idx = find_substr_idx("Afternoon", day_parts)
    morning_df = df.ix[morning_idx + 1: afternoon_idx - 2, :]
    time_band = [assignment[3] for assignment in planData.final_assignment]
    column = [""]*df.shape[0]
    time_band = ["time_band"] + time_band
    column[morning_idx+1:morning_idx+1+len(time_band)] = time_band
    print "new added column is: ", column
    df.insert(1, "time_band", column)

    ratings = [assignment[2] for assignment in planData.final_assignment]
    column = [""] * df.shape[0]
    ratings = ["ratings"] + ratings + [sum(ratings)]
    column[morning_idx + 1:morning_idx + 1 + len(ratings)] = ratings
    print "new added column is: ", column
    df.insert(1, "ratings", column)

    writer = pd.ExcelWriter(out_file_name)
    df.to_excel(writer, 'With Time Band')
    writer.save()