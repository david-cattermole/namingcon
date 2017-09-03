"""
Heart of the naming convention API.
"""

import os
import imp
import re
import abc
import sys
import uuid
import collections
import codecs
import hashlib

import enchant

import namingcon.config as cfg
import namingcon.cache as cache


_imported_modules = []
_conventions = {}


def import_function(module_name, function_name):
    findMod = imp.find_module(module_name)
    if not findMod:
        pass

    mod = None
    try:
        mod = imp.load_module(module_name, findMod[0], findMod[1], findMod[2])
        # NOTE: We need to add the loaded module into a global variable
        # so that the Python Garbage collector doesn't delete the
        # module, because we might run code in the module some time.
        _imported_modules.append(mod)
    except ImportError:
        print 'Failed importing:', name
    if not mod:
        print 'Module doesn\'t exist:', module_name

    func = getattr(mod, function_name, None)
    return func


def expand_words_data(data):
    words = []
    for word in data:
        if isinstance(word, list):
            for j in word:
                if j not in words:
                    words.append(str(j))
        elif isinstance(word, basestring):
            i_split = word.split(' ')
            for j in i_split:
                j_split = j.split('-')
                for k in j_split:
                    k = str(k)
                    if k not in words:
                        words.append(k)
    return words


def load_words_config(names, excludes=None):
    if excludes is None:
        excludes = []

    include_paths = []
    for name in names:
        path = cfg.getConfigPath('words', name + '.json')
        if not os.path.isfile(path):
            continue
        include_paths.append(path)

    exclude_paths = []
    for name in excludes:
        path = cfg.getConfigPath('words', name + '.json')
        if not os.path.isfile(path):
            continue
        exclude_paths.append(path)

    config_hash = str(names)
    if excludes is not None:
        config_hash += 'EXCLUDES:' + str(excludes)
    config_hash = str(hash(config_hash))
    uid = hashlib.sha1(config_hash)
    config_uuid = str(uuid.UUID(bytes=uid.digest()[:16]))
    cache_path = cfg.getConfigPath('words', 'cache', config_uuid + '.txt')
    if os.path.isfile(cache_path):
        f = open(cache_path, 'r')
        include_words = f.readlines()
        f.close()
        return cache_path, include_words

    include_words = []
    for path in include_paths:
        data = cfg.readConfig(path)
        include_words += expand_words_data(data)

    exclude_words = []
    for path in exclude_paths:
        data = cfg.readConfig(path)
        exclude_words += expand_words_data(data)

    words = set(include_words) - set(exclude_words)

    lines = []
    for word in words:
        if word not in exclude_words:
            lines.append(word + os.linesep)
    f = open(cache_path, 'w')
    f.writelines(lines)
    f.close()
    del lines
    return cache_path, words


def load_regex_config(name):
    path = cfg.getConfigPath('validators', name + '.json')
    data = cfg.readConfig(path)
    return data


def load_validator_config(filename):
    path = cfg.getConfigPath('validators', filename + '.json')
    data = {}
    if os.path.isfile(path):
        data = cfg.readConfig(path)
    else:
        msg = 'Validator could not be found: %r'
        raise RuntimeError(msg % filename)
    return data


def construct_validator(cfg):
    assert isinstance(cfg, dict)
    assert 'type' in cfg

    typ = cfg.get('type')
    assert isinstance(typ, basestring)

    validator = None
    if typ in ['dict', 'dictionary']:
        validator = DictValidator(**cfg)
    elif typ in ['re', 'regex']:
        validator = RegexValidator(**cfg)
    elif typ in ['func', 'function']:
        validator = FunctionValidator(**cfg)
    assert validator is not None
    assert isinstance(validator, Validator)
    return validator


def camel_case_split(identifier):
    # TODO: Write other split functions.
    matches = re.finditer(
        '.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)',
        identifier)
    return [m.group(0) for m in matches]


def levenshtein_dist(a, b):
    """
    Calculates the Levenshtein distance between a and b.

    From: http://hetland.org/coding/python/levenshtein.py
    """
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n

    current = range(n + 1)
    for i in range(1, m + 1):
        previous, current = current, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete = previous[j] + 1, current[j - 1] + 1
            change = previous[j - 1]
            if a[j - 1] != b[i - 1]:
                change = change + 1
            current[j] = min(add, delete, change)

    return current[n]


class Style(object):
    """
    A naming style.
    """

    def __init__(self, name):
        self._data = None
        self._path = None
        path = cfg.getConfigPath('styles', name + '.json')
        if os.path.isfile(path):
            self._data = cfg.readConfig(path)
            self._path = path
        else:
            msg = 'Naming Style %r was not found.'
            raise TypeError(msg % path)

    def regex(self):
        pattern = self._data.get('pattern')
        assert isinstance(pattern, basestring)
        regex = re.compile(regex_str)
        return regex

    def split(self, text):
        # TODO: Support more split types.
        return camel_case_split(text)


class Convention(object):
    """
    A naming convention.
    """

    def __init__(self, name):
        self._data = None
        self._path = None
        path = cfg.getConfigPath('conventions', name + '.json')
        if os.path.isfile(path):
            self._data = cfg.readConfig(path)
            self._path = path
        else:
            msg = 'Naming Convention %r was not found.'
            raise TypeError(msg % path)

        self._default_style_name = self._data.get('style', None)
        self._default_nullable = False
        self._default_characters = self._data.get('characters', '.')

        self._structure = self._data.get('structure', None)
        self._groups = self._data.get('groups', None)

        # r'([(][a-z]+[)])([+]|[;]|[:]|[/]|[|]|[\\]|[-]|[_]|[.]|)'
        self._find_sep_re = re.compile(r'([(][a-z]+[)])([_]|[.]|)')
        self._split_re = re.compile(r'[(]([a-z]+)[)]')
        self._groups_regex = None

    def get_structure(self):
        return self._structure

    def find_group_style_name(self, group_name):
        style = self._default_style_name
        if group_name not in self._groups:
            return style
        style = self._groups[group_name].get('style', self._default_style_name)
        return style

    def find_group_characters(self, group_name):
        char_str = self._default_characters
        if group_name not in self._groups:
            return char_str
        char_str = self._groups[group_name].get('characters',
                                                self._default_characters)
        if char_str != '.':
            char_str = '[' + char_str + ']'
        assert isinstance(char_str, basestring)
        return char_str

    def find_group_validator_dicts(self, group_name):
        validator_dicts = []
        if group_name not in self._groups:
            return validator_dicts
        validator_dicts = self._groups[group_name].get('validators', None)
        assert isinstance(validator_dicts, (list, tuple))
        return validator_dicts

    def find_group_nullable(self, group_name):
        validator = self._default_nullable
        if group_name not in self._groups:
            return validator
        validator = self._groups[group_name].get('nullable',
                                                 self._default_style_name)
        return validator

    def group_names(self):
        structure = self._structure
        names = []
        groups_found = self._find_sep_re.findall(structure)
        for grp in groups_found:
            name = self._split_re.findall(grp[0])[0]
            names.append(name)
        return names

    def groups_regex(self):
        structure = self._structure

        groups_pattern = ''
        groups_found = self._find_sep_re.findall(structure)
        for grp in groups_found:
            grp_name = self._split_re.findall(grp[0])[0]
            grp_chars = self.find_group_characters(grp_name)
            grp_sep = grp[1]
            if len(grp_sep) == 0:
                # greedy match for last group, so we get_text the entire text
                groups_pattern += r'(?P<%s>%s+)' % (grp_name, grp_chars)
                continue
            else:
                groups_pattern += r'(?P<%s>%s+?)' % (grp_name, grp_chars)
                groups_pattern += r'([%s])' % grp_sep

        self._groups_regex = re.compile(groups_pattern)
        return self._groups_regex


class Validator(object):
    def __init__(self, *args, **kwargs):
        assert len(args) == 0
        h = repr(args) + repr(kwargs)
        self._filepath = kwargs.get('filepath', h)

        h = hashlib.new('sha1')
        h.update(self._filepath)
        self._name = kwargs.get('name', h.hexdigest())

    def get_filepath(self):
        return self._filepath

    def get_name(self):
        return self._name

    filepath = property(get_filepath)
    name = property(get_name)


class RegexValidator(Validator):
    def __init__(self, pattern=None, *args, **kwargs):
        super(RegexValidator, self).__init__(*args, **kwargs)

        self._pattern = pattern
        self._regex = re.compile(self._pattern)

    def get_pattern(self):
        return self._pattern

    def get_regex(self):
        return self._regex

    def check(self, text):
        r = self._regex.match(text)
        return bool(r)

    regex = property(get_regex)
    pattern = property(get_pattern)


class DictValidator(Validator):
    """
    The words to use for splitting and checking.
    """
    def __init__(self, words=None, language=None, excludes=None, *args, **kwargs):
        super(DictValidator, self).__init__(*args, **kwargs)

        # if language is None:
        #     language = 'en'
        assert isinstance(words, list)
        self._language = language
        self._word_names = words
        self._excludes = excludes
        self._speller = None
        self._default_lang = 'en'  # 'en_AU'

    def get_language(self):
        return self._language
    language = property(get_language)

    def get_words(self):
        return self._word_names

    def get_speller(self):
        words = self.get_words()
        language = self._language
        excludes = self._excludes
        words_path, words_list = load_words_config(words, excludes=excludes)

        speller_type = None
        speller = None
        if language is False:
            if len(words_list) > 0:
                speller_type = 'request_pwl_dict'
                speller = enchant.request_pwl_dict(words_path)
            else:
                speller_type = 'no language, no words_list'
                speller = None

        elif language is True:
            if len(words_list) > 0:
                speller_type = 'DictWithPWL1'
                speller = enchant.DictWithPWL(
                    default_lang,
                    words_path)
            else:
                speller_type = 'Dict1'
                speller = enchant.Dict()

        elif language is None:
            if len(words_list) > 0:
                speller_type = 'DictWithPWL2'
                speller = enchant.DictWithPWL(
                    self._default_lang,
                    words_path)
            else:
                speller_type = 'Dict2'
                speller = enchant.Dict(default_lang)

        elif isinstance(language, basestring):
            speller_type = 'Dict3'
            speller = enchant.Dict(language)

        # print 'speller', speller, speller_type
        self._speller = speller
        return self._speller

    def check(self, text):
        speller = self._speller
        if speller is None:
            speller = self.get_speller()
        return speller.check(text)

    def suggest(self, text):
        speller = self._speller
        if speller is None:
            speller = self.get_speller()
        return speller.suggest(text)


class FunctionValidator(Validator):
    def __init__(self, module_name=None, function_name=None, *args, **kwargs):
        super(FunctionValidator, self).__init__(*args, **kwargs)

        self._module_name = module_name
        self._function_name = function_name
        func = import_function(module_name=self._module_name,
                               function_name=self._function_name)
        self._callable = func

    def check(self, text):
        return text in list(self._callable())

    def suggest(self, text):
        values = list(self._callable())

        data = collections.defaultdict(list)
        for value in values:
            d = levenshtein_dist(value, text)
            data[d].append(value)

        suggestions = []
        for k in sorted(data.keys()):
            for v in data[k]:
                suggestions.append(v)
        return suggestions


class Correction(object):
    def __init__(self, word=None, correct=None, map_range=None, suggestions=None):
        if not isinstance(word, Word):
            msg = 'word argument must be of type Word: %r'
            raise TypeError(msg % correct)
        if correct is None:
            msg = 'correct argument must not be None: %r'
            raise TypeError(msg % correct)
        if map_range is None:
            msg = 'map_range argument must not be None: %r'
            raise TypeError(msg % map_range)
        if suggestions is None:
            msg = 'suggestions argument must not be None: %r'
            raise TypeError(msg % suggestions)

        self._word = word
        self._correct = correct
        self._map_range = map_range
        self._suggestions = suggestions

    def get_word(self):
        return self._word

    def get_correct(self):
        return self._correct

    def get_map_range(self):
        return self._map_range

    def get_suggestions(self):
        return self._suggestions


class Word(object):
    def __init__(self, text, validator_plugins):
        if not isinstance(text, basestring):
            raise TypeError('Incorrect type for "text" argument')
        if validator_plugins is None:
            raise TypeError('"validator_plugins" argument cannot be None')
        if not isinstance(validator_plugins, list):
            raise TypeError('"validator_plugins" argument must be a list')
        if len(validator_plugins) == 0:
            raise TypeError('"validator" argument must have at least 1 plugin.')

        self._orig_text = text
        self._text = text
        self._validators = validator_plugins

    def set_text(self, text):
        self._text = text

    def get_text(self):
        return self._text

    def suggest(self, max_num=None):
        result = []
        # TODO: Make sure we test the suggestions by the same characters as the
        #  validator was.
        bad_char_regex = re.compile(r'^[a-zA-Z0-9]*$')
        for validator in self._validators:
            if not isinstance(validator, (DictValidator, FunctionValidator)):
                continue
            suggest = validator.suggest(self._text) or []
            if suggest:
                suggest = [str(s) for s in suggest]
                # NOTE: We don't want any non Alpha-Numeric numbers to be in
                #  the suggestions, if we do get them, we remove them immediately.
                for i, s in enumerate(suggest):
                    if bad_char_regex.match(s) is None:
                        suggest.pop(i)
                result += suggest

        if max_num is not None:
            result = result[:max_num]
        return result

    def check(self):
        result = False
        for validator in self._validators:
            if validator.check(self._text):
                result = True
                break
        return result


class Group(object):
    def __init__(self, name, raw_text, nullable, validator_plugins, style):
        if not isinstance(raw_text, basestring):
            raise TypeError('Incorrect type for "raw_text" argument')
        if validator_plugins is None:
            raise TypeError('"validator_plugins" argument cannot be None')
        if not isinstance(validator_plugins, list):
            raise TypeError('"validator_plugins" argument must be a list')
        if len(validator_plugins) == 0:
            raise TypeError('"validator" argument must have at least 1 plugin.')

        self._name = name
        self._raw_text = raw_text
        self._nullable = nullable
        self._validators = validator_plugins
        self._style = style

    def get_name(self):
        return self._name

    def get_text(self):
        return self._raw_text

    def set_text(self, text):
        self._raw_text = text

    def get_nullable(self):
        return self._nullable

    def correct(self):
        words = self.split()
        for word in words:
            ok = word.check()
            if ok is False:
                return False
        return True

    def spans(self):
        result = {}
        text = self.get_text()
        split = self._style.split(text)
        start = 0
        end = 0
        for s in split:
            end += len(s)
            result[s] = (start, end)
            start += len(s)
        return result

    def split(self):
        text = self.get_text()
        split = self._style.split(text)
        words = []
        for s in split:
            word = Word(s, self._validators)
            words.append(word)
        return words


class Text(object):
    """
    A chunk of text data to validate.
    """

    def __init__(self, text, convention=None):
        self._raw_text = text
        self._correction_map = [None] * len(text)
        self._groups = []

        global _conventions
        conv = None
        if convention in _conventions:
            conv = _conventions[convention]
        else:
            conv = Convention(convention)
            _conventions[convention] = conv
        self._convention = conv

    def get_raw_text(self):
        return self._raw_text

    def set_raw_text(self, text):
        self._raw_text = text
        self._groups = []
        self._correction_map = [None] * len(text)

    def get_convention(self):
        return self._convention

    def get_structure(self):
        return self._convention.get_structure()

    def get_text(self):
        conv = self.get_convention()
        struct = conv.get_structure()
        text = struct
        grps = self.get_groups()
        names = conv.group_names()
        for grp in grps:
            name = grp.get_name()
            if name not in names:
                print 'warning, bad name.'
                continue
            text = text.replace('(%s)' % name, grp.get_text(), 1)
        return text

    def get_groups(self):
        self._groups = self.split()
        return self._groups

    def get_group(self, name):
        grps = self.get_groups()
        for grp in grps:
            if grp.get_name() == name:
                return grp
        return None

    def check(self):
        result = True
        for grp in self.split():
            for word in grp.split():
                ok = word.check()
                if not ok:
                    result = False
                    break
        return result

    def best_guess(self):
        result = self.get_text()
        cors = self.corrections()
        for cor in cors:
            if cor is None:
                continue
            if cor.get_correct() is True:
                continue

            word = cor.get_word()
            suggestions = cor.get_suggestions()
            if len(suggestions) > 0:
                text = word.get_text()
                suggest = suggestions[0]

                # Match case of suggestion with original text
                if text.isupper():
                    suggest = suggest.upper()
                elif text[0].isupper():
                    suggest = suggest[0].upper() + suggest[1:]

                if text != suggest:
                    # TODO: This method of replacing isn't great because if the
                    #  same word is added into the text multiple times it will
                    #  only be replaced once.
                    result = result.replace(text, suggest, 1)

        return result

    def check_map(self):
        bits = [1] * len(self._raw_text)
        corrections = self.correction_char_map()
        for c in corrections:
            if c is None:
                continue
            ok = c.get_correct()
            start, end = c.get_map_range()
            for i in range(start, end):
                if i >= start and i < end:
                    bits[i] = int(ok)
        return bits

    def corrections(self, max_num=None):
        result = []
        spans = self.spans()
        grps = self.split()
        for grp in grps:
            name = grp.get_name()
            start, end = spans[name]
            words = grp.split()
            for word in words:
                ok = word.check()
                suggestions = []
                if ok is False:
                    suggestions = word.suggest(max_num=max_num)
                x = Correction(
                    word=word,
                    correct=ok,
                    map_range=(start, end),
                    suggestions=suggestions)
                result.append(x)
        return result

    def correction_char_map(self, max_num=None):
        corrections = self.corrections(max_num=max_num)
        for c in corrections:
            start, end = c.get_map_range()
            for i in range(start, end):
                if i >= start and i < end:
                    self._correction_map[i] = c
        return self._correction_map

    def spans(self):
        result = {}
        text = self.get_raw_text()  # self._raw_text
        regex = self._convention.groups_regex()
        match = regex.match(text)
        if match is None:
            return result
        for key in match.groupdict():
            start, end = match.span(key)
            result[key] = (start, end)
        return result

    def split(self):
        if len(self._groups) > 0:
            return self._groups
        grps = []
        regex = self._convention.groups_regex()
        match = regex.match(self._raw_text)
        if match is None:
            return grps

        for key in match.groupdict():
            name = key
            value = match.groupdict().get(key)
            nullable = self._convention.find_group_nullable(key)

            validator_dicts = self._convention.find_group_validator_dicts(key)
            if len(validator_dicts) == 0:
                msg = 'No validators found: %r'
                raise RuntimeError(msg % validator_dicts)

            validators = []
            for d in validator_dicts:
                if not isinstance(d, dict):
                    raise TypeError('Invalid validator type: %r' % d)

                validator_cfg = d
                filename = d.get('filename', None)
                if filename is not None:
                    assert isinstance(filename, basestring)
                    validator_cfg = load_validator_config(filename)
                    if len(validator_cfg) == 0:
                        msg = 'Validator not found: %r'
                        raise RuntimeError(msg % validator_cfg)

                validator = construct_validator(validator_cfg)
                if validator not in validators:
                    validators.append(validator)

            style_name = self._convention.find_group_style_name(key)
            style = Style(style_name)

            grp = Group(name, value, nullable, validators, style)
            grps.append(grp)
        return grps
