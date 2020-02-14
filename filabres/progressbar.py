import sys


def progressbar(count, total, suffix='', bar_len=40):
    """
    Display progress bar.

    Based on https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
    """

    # clean progress bar when reaching 100%
    if count == total:
        emptyline = ' ' * (bar_len + len(suffix) + 12)
        sys.stdout.write('%s\r' % (emptyline))
        sys.stdout.flush()
        return

    # reduce the number updates of the progress bar
    if count < total:
        if total >= bar_len:
            times = int(total / bar_len)
            if times > 1:
                if count % times != 0:
                    return

    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '#' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
    sys.stdout.flush()  # As suggested by Rom Ruben
