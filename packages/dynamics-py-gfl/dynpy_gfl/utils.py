from dynpy_gfl import constants


def reverse_asc_desc_order(order):
    if order == constants.ASC:
        return constants.DESC
    elif order == constants.DESC:
        return constants.ASC
    return order
