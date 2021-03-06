# BracketDot

[![CircleCI](https://circleci.com/gh/shotaIDE/BracketDot.svg?style=shield)](https://circleci.com/gh/shotaIDE/BracketDot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is this ?

A tool that runs lint focusing only on the latest changes in Git.

The supported lint is as follows.

- Swift
  - Spell checker
  - Static analytics by SwiftLint
- Objective-C
  - Warnings by xcodebuild
  - Static analytics by OCLint

## How to start ?

Requires **Python 3.6** or higher

Install by using pip.

```shell
pip install bracketdot
```

### Check Swift codes

Install [SwiftLint](https://github.com/realm/SwiftLint).

```shell
brew install swiftlint
```

Move directory to your swift project which you want to analyze and run the following command.

```shell
cd ${Swift Project Directory}
difflint-swift --last
```

You can get analytics results in `./difflint_report.json`.

### Check Objective-C codes

Install **Command Line Tools** from Apple Developer site.

Install [OCLint](http://docs.oclint.org/en/stable/intro/installation.html) and [xcpretty](https://github.com/xcpretty/xcpretty).

```shell
brew tap oclint/formulae
brew install oclint
gem install xcpretty
```

Move directory to your Objective-C project which you want to analyze and run the following command.

```shell
cd ${Objective-C Project Directory}
difflint-objc --last --project Project.xcodeproj --target Target --config Debug
```

You can get analytics results in `./difflint_report.json`.

### Fix legacy Objective-C notation

**This feature is currently under development and should not be used by non-developers.**

Move directory to your Objective-C project which you want to analyze and run the following command.

```shell
cd ${Objective-C Project Directory}
bracket-dot
```

Objective-C files will be converted as follows.

Before:

```objc:sample.m
String *title = [[self sharedInstance] generateTitle];
```

After:

```objc:sample.m
String *title = self.sharedInstance.generateTitle;
```

## How to develop ?

Clone this repository to your local, and execute the following command.

```shell
cd ${Bracket Dot Directory}
pip install -e '.[dev]'
```

You can debug by using launch configuration for VSCode.
