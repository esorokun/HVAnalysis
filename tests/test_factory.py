from HVAnalysis import dfwrapper, conf, writing


class TestArgs:
    datelist = ['2018-09-25']
    loglvl = 0
    outputfolder = 'test_output'


conf.configure_from_args(TestArgs)

curr_wrapper = dfwrapper.HeinzWrapper(conf.curr_file_names, 'curr')
volt_r_wrapper = dfwrapper.HeinzWrapper(conf.volt_file_names, 'volt')
comb_wrapper = dfwrapper.ResistanceWrapper(curr_wrapper, volt_r_wrapper)
linos_writer = writing.LinosWriter(comb_wrapper, 'test_output')
ernests_writer = writing.ErnestsWriter(comb_wrapper, 'test_output')


def test_true():
    assert True


def test_df_wrapper():
    assert linos_writer.get_unstable_periods() == ernests_writer.get_unstable_periods()


def test_overlap_removal():
    overlapping_periods = ernests_writer.write_unstable_periods()
    clean_periods = ernests_writer.write_unstable_not_overlapping_periods()
    assert overlapping_periods == clean_periods


