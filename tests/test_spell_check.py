# coding: utf-8

import pytest

from bracketdot.spell_check import spell_check


def test_0_misspell_in_1_word():
    line = ' let bracket = "test"'
    result = spell_check(line=line)
    assert len(result) == 0


def test_0_misspell_in_3_word():
    line = ' let bracketDotTest = "test"'
    result = spell_check(line=line)
    assert len(result) == 0


def test_1_misspell_in_1_word():
    line = ' let begining = "test"'
    result = spell_check(line=line)
    assert result == [{'src': 'begining', 'dst': 'beginning'}]


def test_1_misspell_in_3_words():
    line = ' let testBeginingContents = "test"'
    result = spell_check(line=line)
    assert result == [
        {'src': 'testBeginingContents', 'dst': 'testBeginningContents'}]


def test_2_misspells_in_2_words():
    line = ' let diffrentBegining = "test"'
    result = spell_check(line=line)
    assert result == [
        {'src': 'diffrentBegining', 'dst': 'differentBeginning'}]


def test_2_misspells_in_3_words():
    line = ' let testDiffrentBegining = "test"'
    result = spell_check(line=line)
    assert result == [
        {'src': 'testDiffrentBegining', 'dst': 'testDifferentBeginning'}]


def test_1_misspell_in_2_definitions():
    line = ' let begining = "test"; var appreciate = "test"'
    result = spell_check(line=line)
    assert result == [{'src': 'begining', 'dst': 'beginning'}]


def test_3_misspells_in_2_definitions():
    line = ' let beginingDiffrent = "test"; var appriciateBracketDot = "test"'
    result = spell_check(line=line)
    assert result == [
        {'src': 'beginingDiffrent', 'dst': 'beginningDifferent'},
        {'src': 'appriciateBracketDot', 'dst': 'appreciateBracketDot'}]


def test_3_misspells_with_2_ignores_in_2_definitions():
    line = ' let beginingDiffrent = "test"; var appriciateBracketDot = "test"'
    ignore_list = ['begining', 'appriciate']
    result = spell_check(line=line, ignore_list=ignore_list)
    assert result == [{'src': 'beginingDiffrent', 'dst': 'beginingDifferent'}]
