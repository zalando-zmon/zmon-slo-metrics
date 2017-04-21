#!/usr/bin/env python3
from app import app


def run():
    # TODO: run SLI update
    # gevent.spawn(run_sli_update)
    # run our standalone gevent server
    app.run(port=8080, server='gevent')


if __name__ == '__main__':
    run()
