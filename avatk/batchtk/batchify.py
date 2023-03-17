import pandas
import itertools
def batchify( batch_dict = {}, bin_size = 1, file_label = "batch" ):
    """
    batch_dict = {string: generator values}
    """
    run = 0
    bin_num = 0
    curr_size = 0
    curr_batch = []

    for batch in dcx(**batch_dict):
        batch.update({"run": run})
        curr_batch.append(batch)
        run += 1
        curr_size += 1
        if curr_size == bin_size:
            # write bin to csv
            filename = "{}{}.csv".format(file_label, bin_num)
            pandas.DataFrame




def dcx(**kwargs):
    """
    Dictionary preserving Cartesian (x) product
    https://stackoverflow.com/questions/5228158/cartesian-product-of-a-dictionary-of-lists
    """
    for instance in itertools.product(*kwargs.values()):
        yield dict(zip(kwargs.keys(), instance))

