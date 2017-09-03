# Naming Convention

Naming Convention is used to provide an API for parsing and validating user text input.

This project will help with parsing and validating user input text for correctness.

Please note this project is still a work in progress and requires more work before the tool is robust. This project should not be used in production without testing beforehand.  

# Goal

Our goal:
> Help users input text that follows a convention, is spelled correctly and reduces similar synonymous words. 

An application that expects user text input may be incorrect, we aim to help users provide correct input, allowing for more structured and less "customised" data.

# Features

Below we list the feature set of this project, both currently supported and planned future features.

## Supported 

- Validate text based on a convention or nomenclature
- Define validate character set
- Define naming styles
- Define naming conventions
- Provide suggestions to users
- Cache word lists to speed up performance.
- Allow extensive configuration and re-use of configuration segments.
  - Some words are common across an entire domain.
  - Some words will only be used on a single project.
- Allow mechanisms for reading word lists from a file system file.
- Allow mechanisms for reading word lists from a network database.
- Use suggestions for new names previously unused.
  - When defining a new name for the database, the name is checked if it already exists, and encourages re-use of names.

## Planned

- Add / Remove / Update centralised word list entries.
- Log user suggestions in order to build up a 'memory' and improve hit-rate for calculated suggestions.

# Usage

```python
import namingcon.lib
txt = namingcon.lib.Text('badSpellling', 'word_any')

print txt.check()
print txt.best_guess()
print txt.corrections()
```

# Installation

## Requirements

- [Python 2.6+](http://www.python.org/downloads/)
- [pyenchant](https://pypi.python.org/pypi/pyenchant)

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

# Custom Words / Dictionaries

# Correctness

Correctness is defined by:
- Correct spelling
- Text structure
- Valid characters


