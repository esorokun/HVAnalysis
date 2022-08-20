import logging


log_dict = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}
input_data_folder = 'data/input'
all_date_list = [
                 #'2018-09-14', '2018-09-15', '2018-09-16', '2018-09-17', '2018-09-18',
                 '2018-09-19',
                 '2018-09-20', '2018-09-21', '2018-09-22', '2018-09-23', '2018-09-24', '2018-09-25',
                 '2018-09-26', '2018-09-27', '2018-09-28', '2018-09-29', '2018-09-30', '2018-10-01',
                 '2018-10-02', '2018-10-03', '2018-10-04', '2018-10-05', '2018-10-06', '2018-10-07',
                 '2018-10-08', '2018-10-09', '2018-10-10', '2018-10-11', '2018-10-12', '2018-10-13',
                 '2018-10-14', '2018-10-15', '2018-10-16', '2018-10-17', '2018-10-18', '2018-10-19',
                 '2018-10-20', '2018-10-21', '2018-10-22', '2018-10-23', '2018-10-24', '2018-10-25',
                 '2018-10-26', '2018-10-27', '2018-10-28', '2018-10-29', '2018-10-30', '2018-10-31',
                 '2018-11-01', '2018-11-02', '2018-11-03', '2018-11-04', '2018-11-05', '2018-11-06',
                 '2018-11-07', '2018-11-08', '2018-11-09', '2018-11-10', '2018-11-11', '2018-11-12']

new_date_list = ['2022-06-01', '2022-06-02', '2022-06-03', '2022-06-04', '2022-06-05',
                 '2022-06-06', '2022-06-07', '2022-06-08', '2022-06-09', '2022-06-10',
                 '2022-06-11', '2022-06-12', '2022-06-13', '2022-06-14', '2022-06-15',
                 '2022-06-16', '2022-06-17', '2022-06-18', '2022-06-19', '2022-06-20',
                 '2022-06-21', '2022-06-22', '2022-06-23', '2022-06-24', '2022-06-25',
                 '2022-06-26', '2022-06-27', '2022-06-28', '2022-06-29', '2022-06-30',
                 '2022-07-01']

curr_file_names = [f'{input_data_folder}/heinzCurr_{d}.csv' for d in all_date_list]
volt_file_names = [f'{input_data_folder}/heinzVolt_{d}.csv' for d in all_date_list]
Heinz_I_curr_file_names = [f'{input_data_folder}/NP04_DCS_01_Heinz_I._{d}.csv' for d in new_date_list]
Heinz_I_Filtered_curr_file_names = [f'{input_data_folder}/NP04_DCS_01_Heinz_I_Filtered._{d}.csv' for d in new_date_list]
Heinz_V_volt_file_names = [f'{input_data_folder}/NP04_DCS_01_Heinz_V._{d}.csv' for d in new_date_list]
Heinz_V_Cathode_volt_file_names = [f'{input_data_folder}/NP04_DCS_01_Heinz_V_Cathode._{d}.csv' for d in new_date_list]
Heinz_V_Raw_volt_file_names = [f'{input_data_folder}/NP04_DCS_01_Heinz_V_Raw._{d}.csv' for d in new_date_list]
output_folder = 'data/output'


def configure_from_args(args):
    logging.basicConfig(level=log_dict[args.loglvl])
    logging.info(f'Set log level to {args.loglvl}')
    global output_folder; output_folder = args.outputfolder
    if args.datelist is not None:
        global curr_file_names
        global volt_file_names
        global Heinz_I_curr_file_names
        global Heinz_I_Filtered_curr_file_names
        global Heinz_V_volt_file_names
        global Heinz_V_Cathode_volt_file_names
        global Heinz_V_Raw_volt_file_names
        curr_file_names = [f'{input_data_folder}/heinzCurr_{d}.csv' for d in args.datelist]
        volt_file_names = [f'{input_data_folder}/heinzVolt_{d}.csv' for d in args.datelist]
        Heinz_I_curr_file_names = \
            [f'{input_data_folder}/NP04_DCS_01_Heinz_I._{d}.csv' for d in args.datelist]
        Heinz_I_Filtered_curr_file_names = \
            [f'{input_data_folder}/NP04_DCS_01_Heinz_I_Filtered._{d}.csv' for d in args.datelist]
        Heinz_V_volt_file_names = \
            [f'{input_data_folder}/NP04_DCS_01_Heinz_V._{d}.csv' for d in args.datelist]
        Heinz_V_Cathode_volt_file_names = \
            [f'{input_data_folder}/NP04_DCS_01_Heinz_V_Cathode._{d}.csv' for d in args.datelist]
        Heinz_V_Raw_volt_file_names = \
            [f'{input_data_folder}/NP04_DCS_01_Heinz_V_Raw._{d}.csv' for d in args.datelist]
