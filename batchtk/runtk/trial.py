def trials():
    pass


def trial(config, label, tid, dispatcher_constructor, project_path, output_path, submit):
    run_label = '{}_{}'.format(label, tid)
    dispatcher = dispatcher_constructor(project_path=project_path, output_path=output_path, submit=submit,
                                        gid=run_label)

    dispatcher.update_env(dictionary=config)
    try:
        dispatcher.run()
        dispatcher.accept()
        data = dispatcher.recv()
        dispatcher.clean()
    except Exception as e:
        dispatcher.clean()
        raise (e)
    data = pandas.read_json(data, typ='series', dtype=float)
    return data