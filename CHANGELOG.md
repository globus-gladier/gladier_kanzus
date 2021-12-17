# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## 0.1.0 (2021-12-17)

### Features

* Uses dials v1
* Uses three separate flows to handle the data:
    * Watchdog-transfer-flows to move the data into theta
    * A dials flow to process the data
    * A publish flow for publishing to the ACDC website