import unittest

from src import fields 
from src import exceptions

class TestFields(unittest.TestCase):
    def setUp(self):
        self.name = 'q1'
        self.title = 'This is test variable.'
        self.labels = ['Category %d' %i for i in range(1, 11)]
        self.categories = dict(enumerate(self.labels, 1))
        
    def test_integer(self):
        int_field = fields.IntegerField(self.name, self.title)
        self.assertEqual(str(int_field), 'q1. This is test variable.')
        self.assertEqual(int_field.__repr__(), 'q1. This is test variable. of type integer')
        self.assertEqual(int_field.print_type, 'integer')
        self.assertEqual(int_field.get_field_value('5'), 5)
        self.assertEqual(int_field.get_field_value(''), None)
        self.assertRaises(exceptions.ValidationError, int_field.get_field_value, 'not int str')
        self.assertEqual(int_field.get_field_value(15.5), 15)
        self.assertRaises(exceptions.ValidationError, int_field.get_field_value, '15.5')
        int_field = fields.IntegerField(self.name, 'test field', -10, 10)
        self.assertEqual(int_field.get_field_value('-10'), -10)
        self.assertEqual(int_field.get_print_value(10), 10)
        self.assertRaises(exceptions.ValidationError, int_field.get_field_value, -11)
        
    def test_single(self):
        si_field = fields.SingleField(self.name, self.title, self.categories)
        self.assertRaises(exceptions.CategoriesDeletionError, si_field.__delattr__, 'categories')
        self.assertEqual(str(si_field), 'q1. This is test variable.')
        self.assertEqual(si_field.categories, self.categories)
        self.assertEqual(si_field.codes, list(range(1,11)))
        self.assertEqual(si_field.print_type, 'single')
        self.assertEqual(si_field.get_field_value('4'), 4)
        self.assertEqual(si_field.get_field_value(''), None)
        self.assertEqual(si_field.get_print_value('4'), 'Category 4')
        self.assertRaises(exceptions.ValidationError, si_field.get_field_value, 11)
        other_categories = ('Category %d' %i for i in range(1, 11))
        other_codes = range(1,11)[::-1]
        other_categories = dict(zip(other_codes, other_categories))
        res = zip(si_field.codes, other_codes, self.labels)
        self.assertEqual(si_field.get_categories_intersection(other_categories), res)
        
    def test_multiple(self):
        mu_field = fields.MultipleField(self.name, self.title, self.categories)
        self.assertEqual(mu_field.print_type, 'multiple')
        self.assertEqual(mu_field.categories, self.categories)
        self.assertEqual(mu_field.codes, list(range(1,11)))
        self.assertEqual(mu_field.get_field_value([1, '4', '5', '', 6.0]), [1,4,5,6])
        self.assertEqual(mu_field.get_field_value(['',]), None)
        self.assertRaises(exceptions.ValidationError, mu_field.get_field_value, [1,23,5])
        

class TestSurveyStruct(unittest.TestCase):
    def setUp(self):
        self.labels = ['Category %d' %i for i in range(1, 11)]
        self.categories = dict(enumerate(self.labels, 1))
        self.fields = [
                        fields.IntegerField('Q1', 'test q1', 1, 10), 
                        fields.IntegerField('q2', 'test q2', 1, 10),
                        fields.SingleField('Q3', 'test q3', self.categories),
                        fields.MultipleField('q4', 'test q4', self.categories)
                    ]
        self.survey = fields.SurveyStruct('srv1', 'Test Survey', self.fields)
                        
    def test_init(self):
        self.assertEqual(self.survey._fields, self.fields)
        fdict = dict([(field.name.lower(), field) for field in self.fields])
        self.assertEqual(self.survey._field_dict, fdict)
        self.assertEqual(len(self.survey), 4)
        self.assertEqual(self.survey.q1, self.fields[0])
        self.assertEqual(self.survey[1], self.fields[1])
        self.assertRaises(exceptions.FieldDoesNotExist, lambda x: self.survey.q10,0)
        
    def test_append(self):
        newfield = fields.SingleField('Q5', 'test q5', self.categories)
        self.survey.append(newfield)
        self.assertEqual(self.survey.Q5, newfield)
        self.assertEqual(self.survey.q5, newfield)
        self.assertEqual(self.survey[4], newfield)
        self.assertEqual(len(self.survey), 5)
        duplfield = fields.SingleField('Q3', 'duplicates q3!', self.categories)
        self.assertRaises(exceptions.DuplicateFieldNameError, \
                                self.survey.append, duplfield)
                                
    def test_insert(self):
        newfield1 = fields.SingleField('Q5', 'test q5', self.categories)
        newfield2 = fields.SingleField('Q6', 'test q6', self.categories)
        newfield3 = fields.SingleField('Q7', 'test q7', self.categories)
        self.survey.insert(0, newfield1)
        self.survey.insert(3, newfield2)
        self.survey.insert(7, newfield3)
        self.assertEqual(self.survey.Q5, newfield1)
        self.assertEqual(self.survey[0], newfield1)
        self.assertEqual(self.survey[3], newfield2)
        self.assertEqual(self.survey[4], self.fields[2])
        self.assertEqual(self.survey[6], newfield3)
        self.assertEqual(len(self.survey), 7)
        duplfield = fields.SingleField('Q3', 'duplicates q3!', self.categories)
        self.assertRaises(exceptions.DuplicateFieldNameError, \
                                self.survey.insert, 0, duplfield)
                                
    def test_remove(self):
        self.assertEqual(self.survey.Q1, self.fields[0])
        self.survey.remove('q1')
        self.assertRaises(exceptions.FieldDoesNotExist, lambda: self.survey.Q1)
        self.assertEqual(len(self.survey), 3)
        self.assertEqual(self.survey[0], self.fields[1])
        self.assertRaises(exceptions.FieldDoesNotExist, self.survey.remove, 'q5')
        
        
        
def run_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFields)
    unittest.TextTestRunner(verbosity=2).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSurveyStruct)
    unittest.TextTestRunner(verbosity=2).run(suite)
        
