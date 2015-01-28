"""
Exception and warning classes.
"""

class DuplicateFieldNameError(Exception):
    """Provided field can't be added to survey because other field with same 
    name exists in the scheme
    """
    pass

class FieldDoesNotExist(Exception):
    """The requested field can't be found in survey struct"""
    pass
    
class ValidationError(Exception):
    """An error while validating data"""
    pass

class CategoryCodeError(Exception):
    """Category code can't be converted into int"""
    pass
    
class DuplicateCategoryError(Exception):
    """Error raises when some category label is duplicated through categories"""
    pass

class CategoriesDeletionError(Exception):
    """Error raises when while trying to delete field categories"""
    pass
