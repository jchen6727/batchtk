def flush_fptr(fptr):
    try:
        fptr.fsync()
    except AttributeError:
        fptr.flush()