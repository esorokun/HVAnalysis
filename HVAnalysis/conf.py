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
curr_file_names = [f'{input_data_folder}/heinzCurr_{d}.csv' for d in all_date_list]
volt_file_names = [f'{input_data_folder}/heinzVolt_{d}.csv' for d in all_date_list]
output_folder = 'data/output'


def configure_from_args(args):
    logging.basicConfig(level=log_dict[args.loglvl])
    logging.info(f'Set log level to {args.loglvl}')
    global output_folder; output_folder = args.outputfolder
    if args.datelist is not None:
        global curr_file_names
        global volt_file_names
        curr_file_names = [f'{input_data_folder}/heinzCurr_{d}.csv' for d in args.datelist]
        volt_file_names = [f'{input_data_folder}/heinzVolt_{d}.csv' for d in args.datelist]
