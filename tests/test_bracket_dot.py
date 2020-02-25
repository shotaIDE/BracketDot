# coding: utf-8

import pytest

from bracketdot.bracket_dot import get_bracket_to_dot


def test_not_convert():
    line = ' textField.enabled = YES; '
    result = get_bracket_to_dot(line=line)
    assert result is None


def test_method_call_without_arguments_when_return_value_not_used():
    line = ' [view layoutIfNeeded]; '
    result = get_bracket_to_dot(line=line)
    assert result is None


def test_method_call_without_arguments_when_return_value_used():
    line = ' if ([view isFirstResponder]) {'
    result = get_bracket_to_dot(line=line)
    assert result['dst'] == ' if (view.isFirstResponder) {'


def test_getter_call():
    line = ' UIColor *backgroundColor = [view backgroundColor]; '
    result = get_bracket_to_dot(line=line)
    assert result['dst'] == (' UIColor *backgroundColor = '
                             'view.backgroundColor; ')


def test_setter_call():
    line = ' [view setBackgroundColor:backgroundColor]; '
    result = get_bracket_to_dot(line=line)
    assert result['dst'] == ' view.backgroundColor = backgroundColor; '


# def test_array_getter_call_with_int():
#     line = ' NSString *test = [testArray objectAtIndex:2]; '
#     result = get_bracket_to_dot(line=line)
#     assert result['dst'] == ' NSString *test = testArray[2]; '

def test_array_getter_call_with_variable():
    line = ' NSString *testValue = [testArray objectAtIndex:testIndex]; '
    result = get_bracket_to_dot(line=line)
    assert result['dst'] == ' NSString *testValue = testArray[testIndex]; '


def test_array_getter_call_with_variable():
    line = (' [testArray replaceObjectAtIndex:testIndex '
            'withObject:testString]; ')
    result = get_bracket_to_dot(line=line)
    assert result['dst'] == ' testArray[testIndex] = testString; '


def test_dictionary_getter_call_with_variale():
    line = ' NSString *testValue = [testDictionary objectForKey:testKey]; '
    result = get_bracket_to_dot(line=line)
    assert result['dst'] == ' NSString *testValue = testDictionary[testKey]; '


def test_dictionary_setter_call_with_variable():
    line = ' [testDictionary setObject:testValue forKey:testKey]; '
    result = get_bracket_to_dot(line=line)
    assert result['dst'] == ' testDictionary[testKey] = testValue; '
