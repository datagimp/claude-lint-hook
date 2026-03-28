"""Sample Python file with linting issues for testing."""

import os
import sys


def bad_function( x,y,z ):
    """This function has formatting issues."""
    result=x+y+z
    return result


# Unused variable
unused = "this is unused"


# Missing whitespace around operators
value=1+2


# Line too long
very_long_variable_name_that_definitely_violates_common_style_guides = "hello world"


class BadClass:
    def __init__(self):
        self.value=1

    def bad_method(self):
        pass
