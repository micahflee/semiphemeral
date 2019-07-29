# Semiphemeral Changelog

## 0.5

* Bugfix: Fixed issue fetching tweets from the Twitter API in unlike mode

## 0.4

* Feature: Support for unliking old tweets that the Twitter API doesn't make easy, by reliking/unliking them all
* Feature: Add support for logging events to file
* Feature: Add `configure --debug` option
* Feature: Add `configure --port` option
* Bugfix: Fetches 240 character tweets, instead of just the first 140 characters

## 0.3

* Bugfix: jQuery wasn't included in the PyPi package, so tweets page of configure web app was broken. jQuery is now included
* Bugfix: When fetching, fetch likes if the delete likes setting is enabled rather than the delete tweets setting
* Bugfix: Exit gracefully when running stats if semiphemeral isn't configured yet

## 0.2

* Bugfix: PyPi package now include HTML templates and static resources

## 0.1

* First release
