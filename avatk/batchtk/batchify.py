import pandas
import itertools
def batchify( batch_dict, bin_size = 1, file_label = None ):
    """
    batch_dict = {string: list}
    bin_size = integer
    file_label = string
    --------------------------------------------------------------------------------------------------------------------
    creates a list of pandas dataframes, if file_label exists, each pandas dataframe is written to a csv file.
    """
# rewrite using pandas.cut ? : https://pandas.pydata.org/docs/reference/api/pandas.cut.html
    bins = []

    bin_num = 0
    curr_size = 0
    curr_batch = []

    for run, batch in enumerate(dcx(**batch_dict)):
        batch.update({"run": run})
        curr_batch.append(pandas.Series(batch))
        curr_size += 1
        if curr_size == bin_size:
            curr_size = 0
            bin_df = pandas.DataFrame(curr_batch)
            curr_batch = []
            bins.append(bin_df)
            # write bin to csv if file_label
            if file_label:
                filename = "{}{}.csv".format(file_label, bin_num)
                bin_num += 1
                bin_df.to_csv(filename, index=False)
    if curr_batch:
        # write last batch if empty
        bin_df = pandas.DataFrame(curr_batch)
        bins.append(bin_df)
        if file_label:
            filename = "{}{}.csv".format(file_label, bin_num)
            bin_df.to_csv(filename, index=False)
    return bins

def dcx(**kwargs):
    """
    Dictionary preserving Cartesian (x) product, returned as a generator
    https://stackoverflow.com/questions/5228158/cartesian-product-of-a-dictionary-of-lists
    """
    for instance in itertools.product(*kwargs.values()):
        yield dict(zip(kwargs.keys(), instance))

