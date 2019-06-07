# BracketDot

BracketDot is tools for auto converting to modern Objective-C coding style.

## Prerequisites
You have to prepare newer version than Python 3.6.

## Installation

```shell
cd ${BracketDotDirectory}
pip install .
```

### iOS Lint
Install Command Line Tools from Apple Developer site and run the following command.

```shell
gem install xcpretty
brew install swiftlint
```

## Usage

```shell
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
