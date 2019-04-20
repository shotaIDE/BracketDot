# BracketDot

BracketDot is tools for auto converting to modern Objective-C coding style.

## Prerequisites
You have to prepare newer version than Python 3.6.

## Installation

```sh
cd ${BracketDotDirectory}
pip install .
```

## Usage

```sh
cd ${Objective-C Project Directory}
bracket-dot
```

Objective-C files will be converted as below.

Before:

```objc:sample.m
String *title = [[self sharedInstance] generateTitle];
```

After:

```objc:sample.m
String *title = self.sharedInstance.generateTitle;
```
