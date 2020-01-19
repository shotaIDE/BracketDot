# BracketDot

## What is this ?

A tool that runs lint focusing only on the latest changes in Git.

The supported lint is as follows.

- Swift
  - Spell checker
  - Static analytics by SwiftLint
- Objective-C
  - Warnings by xcodebuild
  - Static analytics by OCLint

## Prerequisites

You have to prepare newer version than Python 3.6.

## Installation

```shell
cd ${BracketDotDirectory}
pip install .
```

### Swift Lint

```shell
brew install swiftlint
```

### Objective-C Lint

Install Command Line Tools from Apple Developer site and run the following command.

```shell
brew tap oclint/formulae
brew install oclint
gem install xcpretty
```

## Usage

### Swift Lint

```shell
cd ${Swift_Project_Directory}
difflint-swift --last
```

### Bracket Dot

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

### Objective-C Lint

```shell
cd ${Objective-C Project Directory}
difflint-objc --last --project Project.xcodeproj --target Target --config Debug
```
