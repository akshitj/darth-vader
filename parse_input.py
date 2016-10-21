import pandas as pd
import math
import csv
from globals import dayparts


def find_substr_idx(sub_str, list):
    for idx, s in enumerate(list):
        if isinstance(s, unicode) and sub_str in s:
            return idx
    return -1


def find_end_idx(start_idx, list):
    for idx, s in enumerate(list[start_idx:]):
        if isinstance(s, float) and math.isnan(s):
            return start_idx + idx - 1
    return len(list) - 1


def get_start_end_idx(df, daypart_name):
    day_parts = df.ix[:, 0].tolist()

    start_idx = find_substr_idx(daypart_name, day_parts)
    end_idx = find_end_idx(start_idx, day_parts)
    return start_idx, end_idx


def get_day_part_data_frame(df, daypart_name):
    start_idx, end_idx = get_start_end_idx(df, daypart_name)
    day_part_df = df.ix[start_idx + 1: end_idx, :]
    return day_part_df


def get_input(file_name, daypart_name, planData):
    """

    :param file_name: str
    :param daypart_name: str
    :param planData: globals.PlanData
    :return:
    """
    df = pd.read_excel(open(file_name, 'rb'), sheetname='Without Rates')
    day_part_df = get_day_part_data_frame(df, daypart_name)

    spot_lengths = day_part_df.ix[:, 1].tolist()[1:-1]
    spot_lengths = map(int, spot_lengths)

    revenues = day_part_df.ix[:, 2].tolist()[1:-1]
    revenues = map(int, revenues)

    margins = day_part_df.ix[:, 4].tolist()[1:-1]
    margins = map(int, margins)
    planData.fill_items(spot_lengths, revenues)

    margin_percentage = (sum(margins)*100)/sum(revenues)
    planData.set_margin(margin_percentage)


def write_output(in_file_name, out_file_name, plan_data_map):
    """

    :type plan_data_map: dict(int, globals.PlanData)
    """
    df = pd.read_excel(open(in_file_name, 'rb'), sheetname='Without Rates')

    time_column = [""] * df.shape[0]
    rating_column = [""] * df.shape[0]
    spot_cost_column = [""] * df.shape[0]
    margin_column = [""] * df.shape[0]

    for day_part in dayparts:
        plan_data = plan_data_map[day_part]
        start_idx, end_idx = get_start_end_idx(df, day_part)

        # time column
        time_band = [assignment[3] for assignment in plan_data.final_assignment]
        time_band = ["time_band"] + time_band
        time_column[start_idx + 1: start_idx + 1 + len(time_band)] = time_band

        # ratings
        ratings = [assignment[2] for assignment in plan_data.final_assignment]
        ratings = ["ratings"] + ratings + [sum(ratings)]
        rating_column[start_idx + 1:start_idx + 1 + len(ratings)] = ratings

        #spot cost
        costs = [assignment[4] for assignment in plan_data.final_assignment]
        costs = ["spot_costs"] + costs + [sum(costs)]
        spot_cost_column[start_idx + 1:start_idx + 1 + len(costs)] = costs

        #margin
        margins = [assignment[1] - assignment[4] for assignment in plan_data.final_assignment]
        margins = ["margin"] + margins + [sum(margins)]
        margin_column[start_idx + 1:start_idx + 1 + len(margins)] = margins

    df.insert(1, "ratings", rating_column)
    df.insert(1, "time_band", time_column)
    df.insert(1, "spot_costs", spot_cost_column)
    df.insert(1, "margin", margin_column)



    # day_parts = df.ix[:, 0].tolist()
    # morning_idx = find_substr_idx("Morning", day_parts)
    # afternoon_idx = find_substr_idx("Afternoon", day_parts)
    # time_band = [assignment[3] for assignment in plan_data.final_assignment]
    # column = [""] * df.shape[0]
    # time_band = ["time_band"] + time_band
    # column[morning_idx + 1:morning_idx + 1 + len(time_band)] = time_band
    # print "new added column is: ", column
    # df.insert(1, "time_band", column)

    # ratings = [assignment[2] for assignment in plan_data.final_assignment]
    # column = [""] * df.shape[0]
    # ratings = ["ratings"] + ratings + [sum(ratings)]
    # column[morning_idx + 1:morning_idx + 1 + len(ratings)] = ratings
    # print "new added column is: ", column
    # df.insert(1, "ratings", column)

    writer = pd.ExcelWriter(out_file_name)
    df.to_excel(writer, 'With Time Band')
    writer.save()


def to_time(t):
    mins = t % 100
    hrs = t / 100
    t_lower = str(hrs).zfill(2) + ":" + str(mins).zfill(2)
    mins += 30
    hrs += mins / 60
    mins %= 60
    t_upper = str(hrs).zfill(2) + ":" + str(mins).zfill(2)
    return t_lower + "-" + t_upper


def get_time_bands(file_name, dayparts):
    time_bands_raw = []
    with open(file_name, 'rb') as csvfile:
        csv_rdr = csv.reader(csvfile)

        for row in csv_rdr:
            time_bands_raw.append(row)

        time_bands = dict()

        for daypart in dayparts:
            time_bands[daypart] = [[to_time(int(x[0])), int(x[1]), float(x[3])] for x in time_bands_raw if
                                   x[2].find(daypart) >= 0]
        return time_bands
