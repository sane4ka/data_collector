"""
Defines Fields used in data surveys to hold questionaire answers. Fields hold
attributes of questionaire variables like name, title, categories for categorial
variables. Also convert input values to form appropriate to field and provide 
internal type checks (i.e. if input value is in categories codes.
Types of fields: IntegerField, FloatField, StringField, SingleField, MultipleField
"""

from src import exceptions


class Field(object):
    """Base class for all field types. Field class holds main descriptive 
    attributes of data survey var. Can check if input value is suitable for this
    Field and convert value to some pretty form for showing to user
    """
    def __init__(self, name, title=''):
        self.name = name
        self.title = title.strip()
        
    def __str__(self):
        return '%s. %s' %(self.name, self.title)
        
    def __repr__(self):
        return '%s. %s of type %s' %(self.name, self.title, self.print_type)
        
    @property
    def print_type(self):
        return self.__class__.__name__.replace('Field', '').lower()
        
    def get_print_value(self, value):
        """Converts value to pretty form for showing to user. Returns the 
        converted value. Subclasses should override this.
        """
        return value
        
    def get_field_value(self, value):
        """
        Converts the input value into the expected Python data type and validates
        for Field type rules. Raises exceptions.ValidationError if the data can't
        be converted or doesn't validate. Returns the converted value. 
        Subclasses should override this.
        """
        return value


class IntegerField(Field):
    def __init__(self, name, title, min=None, max=None):
        super(IntegerField, self).__init__(name, title)
        if min is not None:
            min = int(min)
        if max is not None:
            max = int(max)
        self.min = min
        self.max = max
        
    def _in_min_max_interval(self, value):
        if (self.min and value < self.min):
            raise exceptions.ValidationError('Provided value %s less that allowed  '
            'minimum value %d for field %s' %(value, self.min, repr(self)))
        if (self.max and value > self.max):
            raise exceptions.ValidationError('Provided value %s bigger that allowed  '
            'maximum value %d for field %s' %(value, self.min, repr(self)))
        return True
    
    def get_field_value(self, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            if not value:
                return None
            raise exceptions.ValidationError('Invalid input %s for field %s' \
                                                            %(value, repr(self)))
        if self._in_min_max_interval(value):
            return value
        
        
class FloatField(IntegerField):
    
    def get_field_value(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            if not value:
                return None
            raise exceptions.ValidationError('Invalid input %s for field %s' \
                                                            %(value, repr(self)))
        if self._in_min_max_interval(value):
            return value


class StringField(Field):
    def get_field_value(self, value):
        if not value:
            return ''
        return str(value)


class CategoriesMixin(object):
    def __init__(self, name, title, categories):
        super(CategoriesMixin, self).__init__(name, title)
        self._categories = self._get_categories(categories)
        self.codes = sorted(self._categories.keys()[:])
        
    def _get_categories(self, categories):
        categories = dict(categories)
        result_categories, category_labels = {}, []
        for code, label in categories.items():
            label.strip()
            try:
                code = int(code)
            except (TypeError, ValueError):
                raise exceptions.CategoryCodeError('Invalid value for category code: %s' %code)
            if label.lower() in category_labels:
                raise DuplicateCategoryError('Category %s already exists in categories of field %s' \
                                            %(value, repr(self)))
            result_categories[code] = label
            category_labels.append(label.lower())
        return result_categories
            
    def get_categories_intersection(self, other_categories):
        """Returns categories with same labels in own categories and 
        other_categories in form: 
        [(category_code, other_category_code, category_label), ...]
        """
        label_dict = dict(zip([c.lower() for c in other_categories.values()], \
                                other_categories.keys()))
        intersection = []
        for code, label in sorted(self.categories.items()):
            other_code = label_dict.get(label.lower(), None)
            if other_code:
                intersection.append((code, other_code, label))
        return intersection
    
    @property
    def categories(self):
        return self._categories
        
    @categories.setter
    def categories(self, newcategories):
        self._categories = self._get_categories(categories)
        self.codes = list[sorted(self._categories.keys())]
    
    @categories.deleter
    def categories(self):
        raise exceptions.CategoriesDeletionError(\
                "Categories of field %s can't be deleted" %repr(self))
        
    def get_print_categories(self):
        return sorted(self._categories.items())


class SingleField(CategoriesMixin, IntegerField):
    
    def get_field_value(self, value):
        value = super(SingleField, self).get_field_value(value)
        if value is None:
            return value
        if value not in self.codes:
            raise exceptions.ValidationError(\
                    'Provided value %d not in category codes of field %s' \
                    %(value, repr(self)))
        return value
            
    def get_print_value(self, value):
        value = self.get_field_value(value)
        return self._categories[value]


class MultipleField(SingleField):
    
    def get_field_value(self, values):
        result_values = []
        for value in values:
            value = super(MultipleField, self).get_field_value(value)
            if value is None:
                continue
            if value not in self.codes:
                raise exceptions.ValidationError(\
                    'Provided value %d not in category codes of field %s' \
                    %(value, repr(self)))
            result_values.append(value)
        if not result_values:
            return None
        return result_values
            
    def get_print_value(self, value):
        values = self.get_field_value(value)
        return [self._categories[value] for value in values]


class SurveyStruct(object):
    def __init__(self, fields=[]):
        """fields - a list of fields, _field_dict - dict for addressing fields 
        by its names.
        """
        self._fields = [] 
        self._field_dict = {}
        for field in fields:
            self.append(field)
        
    def _add_to_dict(self, field):
        field_name = field.name.lower().strip()
        if field_name in self._field_dict:
            raise exceptions.DuplicateFieldNameError(\
                'Error while adding field %s: field with given name already '
                'exists in the survey' %field)
        self._field_dict[field_name] = field
        
    def _get_from_dict(self, field_name):
        field = self._field_dict.get(field_name.lower().strip())
        if field:
            return field
        raise exceptions.FieldDoesNotExist(\
                "Field with name %s doesn't exists in the survey" %field_name)
                        
            
    def __eq__(self, struct):
        return self._field_dict == struct._field_dict
        
    def append(self, field):
        self._add_to_dict(field)
        self._fields.append(field)
        
    def insert(self, i, field):
        self._add_to_dict(field)
        self._fields.insert(i, field)
        
    def remove(self, field_name):
        field = self._get_from_dict(field_name)
        self._field_dict.pop(field_name.lower())
        self._fields.remove(field)
        
    def __getitem__(self, i):
        return self._fields[i]
        
    def __iter__(self):
        return self._fields
        
    def __len__(self):
        return len(self._fields)
        
    def __getattr__(self, field_name):
        """Gets field by its name"""
        return self._get_from_dict(field_name)
            
