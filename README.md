# Naming Convention

Naming Convention is used to provide an API for parsing and validating user text input.

This project will help with parsing and validating user input text for correctness.

# Goal

Our goal:
> Help users input text that follows a convention, is spelled correctly and reduces similar synonymous words. 

An application that expects user text input may be incorrect, we aim to help users provide correct input, allowing for less customised and more structured data.

# Features

- validate text
- define validate character set / encoding
- define naming styles
- define naming conventions
- provide suggestions to users
- provide cascading hierarchical centralised word lists.
  - some words are common across an entire domain.
  - some words will only be used on a single project.
- allow mechanisms for reading word lists from a file system file.
- allow mechanisms for reading word lists from a network database.
- cache word lists locally per-user.
  - update every X minutes.
- add / remove / update centralised word list entries.
- use re-mapping suggestions for new names unlisted in a database.
  - when defining a new name for the database, the name is checked for simplicity and possible re-use of names.
- log user suggestions in order to build up a 'memory' and improve hit-rate for calculated suggestions.


Convention must be correct.
- correct number of split chars
- no bad chars
- define the split chars and groups.
- word type must be correct

Style must be correct or ability to convert to.
- to be written

Each word must have correct spelling
- to be written

text parsing.
1) split Text into Groups using convention.
2) split Groups into Words using style.
3) test spelling for each word.


# Usage

## Basic


## Advanced

# Installation

## Requirements

- [Python 2.6+](http://www.python.org/downloads/)
- [GNU Aspell](http://aspell.net/)
- [aspell-python-py2](https://pypi.python.org/pypi/aspell-python-py2)

# Naming Styles

The namingConvention project comes with the following default naming styles:

- Lower camel case: `soLongAndThanksForAllTheFish`
  - First letter is lower case.
  - Also known as Camel Case.
- Upper camel case: `SoLongAndThanksForAllTheFish`
  - First letter is upper case.
  - Also known as Pascal Case.
- Snake case: `So_long_and_thanks_for_all_the_fish`
  - Upper or lower does not matter.
  - Also known as Underscore separated.
- Lower snake case: `so_long_and_thanks_for_all_the_fish`
- Upper snake case: `So_Long_And_Thanks_For_All_The_Fish`
- Lower case: `solongandthanksforallthefish`
- Upper case: `SOLONGANDTHANKSFORALLTHEFISH`

See the Python [PEP 8](https://www.python.org/dev/peps/pep-0008/#descriptive-naming-styles) for a description of naming styles.

You may also add more styles using config files. 

# Naming Convention

# Naming Structure

# Custom Dictionaries

# Correctness

Correctness is defined by:
- Correct Spelling
- Text structure
- Valid characters


