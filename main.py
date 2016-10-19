from parse_input import get_input
from globals import PlanData

# main function. first point of execution
if __name__ == "__main__":

    input_file_name = '/home/akshit/ad-planner/ad-planner-op.xls'

    get_input(input_file_name)

    plan_data = PlanData()
    plan_data.get_max_ratings()