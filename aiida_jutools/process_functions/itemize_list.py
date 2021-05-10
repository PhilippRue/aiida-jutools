# -*- coding: utf-8 -*-
###############################################################################
# Copyright (c), Forschungszentrum Jülich GmbH, IAS-1/PGI-1, Germany.         #
#                All rights reserved.                                         #
# This file is part of the aiida-jutools package.                             #
# (AiiDA JuDFT tools)                                                         #
#                                                                             #
# The code is hosted on GitHub at https://github.com/judftteam/aiida-jutools. #
# For further information on the license, see the LICENSE.txt file.           #
# For further information please visit http://judft.de/.                      #
#                                                                             #
###############################################################################
"""CalcFunction for itemizing Lists."""

# DEVNOTE: AiiDA best practice for process functions: one module per function.
# Reference: https://aiida.readthedocs.io/projects/aiida-core/en/latest/topics/processes/functions.html#provenance

from aiida.engine import calcfunction
from aiida.orm import List


@calcfunction
def itemize_list(a_list: List):
    """Itemize an ORM List node of python type objects into a set of ORM Data nodes. Store provenance.

    Currently supported input data types: bool, numpy.bool, int, numpy.int, float, numpy.float, str, dict,
    list (List of lists), numpy.ndarray (implicit conversion to list).

    Corresponding output Data node types: Bool, Int, Float, Str, Dict, List (list of Lists).

    :param a_list: a list node with items of python data types.
    :type a_list: List
    :return: a dict with values = one ORM Data type node for each item in the input list
    :rtype: dict

    Use cases / recipes:

    1) Rescaling structures by a set of different scaling factors. Store not only the provenance between
    structure and scaling factors, but also between an individual scaling factor and the whole set. To realize
    the latter, first store the set as List of floats. Then link the List with a set of Floats by itemizing it
    with this method.

    2) The ORM List type converts numpy array items implicitly into lists or lists of lists. So itemization of
    a List of numpy arrays into ArrayData nodes is not possible. For that, simply use an ArrayData object. Still,
    numpy array itemization can be useful. For example, to itemize a 1D numpy array into a set of Float nodes,
    call itemize_list(List(list=(list(numpy_array)))).
    """
    import numpy
    from aiida.orm import Bool, Int, Float, Str, Dict, List
    from aiida.engine import ExitCode

    type_correspondence = {
        bool: Bool,
        numpy.bool: Bool,
        int: Int,
        numpy.int: Int,
        float: Float,
        numpy.float: Float,
        str: Str,
        dict: Dict,
        list : List
    }

    warning_messages = {
        100: f"For one or more items in the list, my type correspondence dictionary has no entry."
             f"I have skipped itemization of these items. If this is a problem, please adjust my dictionary. "
             f"Type correspondence dictionary:\n{type_correspondence}"
             f"Item list:\n{a_list}"
    }

    exit_messages = {}
    exit_status = None

    orm_types = [type_correspondence.get(type(item)) for item in a_list]
    if not all([orm_type for orm_type in orm_types]):
        print(warning_messages[100])

    zeropad = f"0{len(a_list) % 10}"
    keys = [f"item_{format(index, zeropad)}" for index, item in enumerate(a_list)]

    a_dict = {}
    for index, item in enumerate(a_list):
        orm_cls = orm_types[index]
        if orm_cls:
            key = keys[index]
            if issubclass(orm_cls, Dict):
                value = orm_cls(dict=item)
            if issubclass(orm_cls, List):
                value = orm_cls(list=item)
            else:
                value = orm_cls(item)
            a_dict[key] = value

    if exit_status:
        return ExitCode(exit_status, exit_messages[exit_status])

    return a_dict