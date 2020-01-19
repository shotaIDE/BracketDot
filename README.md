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

## How to start ?

Requires **Python 3.6** or higher

### Swift

Clone this repository on your local.

Install this package by using pip.

```shell
cd ${Bracket Dot Directory}
pip install .
```

Install [SwiftLint](https://github.com/realm/SwiftLint).

```shell
brew install swiftlint
```

Move directory to your swift project which you want to analyze and run command as below.

```shell
cd ${Swift Project Directory}
difflint-swift --last
```

You can get analytics results in `./difflint_report.json`.

### Objective-C

Clone this repository on your local.

Install this package by using pip.

```shell
cd ${Bracket Dot Directory}
pip install .
```

Install **Command Line Tools** from Apple Developer site.

Install [OCLint](http://docs.oclint.org/en/stable/intro/installation.html) and [xcpretty](https://github.com/xcpretty/xcpretty).

```shell
brew tap oclint/formulae
brew install oclint
gem install xcpretty
```

Move directory to your Objective-C project which you want to analyze and run command as below.

```shell
cd ${Objective-C Project Directory}
difflint-objc --last --project Project.xcodeproj --target Target --config Debug
```

You can get analytics results in `./difflint_report.json`.

### Bracket Dot

**This feature is currently under development and should not be used by non-developers.**

Clone this repository on your local.

Install this package by using pip.

```shell
cd ${Bracket Dot Directory}
pip install .
```

Move directory to your Objective-C project which you want to analyze and run command as below.

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
