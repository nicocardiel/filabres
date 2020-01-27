"""
    Plotting a progression bar
"""
import numpy as np
import time


def arrow(partial, total=10):
    """
    Create the arrow structure together with the spaces to be later on printed

    :param partial:
    :param total:
    :return:
    """

    # Check if partial is to big
    if partial > total:
        return '[' + '=' * total + ']'

    # Check if partial is to small
    if partial is 0:
        return '[' + ' ' * total + ']'

    start = '['
    shaft = '=' * (partial - 1)
    head = '>' * min(total - partial + 1, 1)
    space = ' ' * (total - partial)
    close = ']'
    final = start + shaft + head + space + close

    return final


def progressbar(partial, complete, length=10, text_left='', text_right='', no_return=False, percentage=False):
    fraction = np.around(np.divide(partial, complete), 2)
    arr = arrow(int(np.round(fraction * length)), length)

    # Add spaces left and right of the arrow if there are no spaces
    if text_left is not '':
        if text_left[-1] is not ' ':
            text_left = text_left + ' '

    if text_right is not '':
        if text_right[0] is not ' ':
            text_right = ' ' + text_right

    # Add a percentage
    if percentage:
        percentage = ' - {:3.0f}%|'.format(np.around(fraction * 100, decimals=0))
    else:
        percentage = ''

    # Plot the progress bar
    if partial < complete and not no_return:
        print('{0}{1}{2}{3}'.format(text_left, arr, percentage, text_right), end='\r')
    elif partial == complete or no_return:
        print('{0}{1}{2}{3}'.format(text_left, arr, percentage, text_right), end='\n')


def main():
    maximum = 50
    for i in range(maximum + 1):
        progressbar(i, maximum, 40, text_left='Prueba123', text_right='Test321', no_return=True, percentage=True)
        time.sleep(0.2)


if __name__ == "__main__":
    main()
