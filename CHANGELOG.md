# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- Add a changelog
- dependencies: upgrade apkeep from 0.17.0 to 0.18.0
- dependencies: upgrade django to 5.2.11
- languages: update Chinese Simplified, Estonian, German, Norwegian, Russian, Swedish

## [1.32.2] - 2025-12-06

- [Dependencies] Upgrade django to 5.2.9, urllib3 to 2.6.0, fonttools to 4.61.0 by @codeurimpulsif in #680
- [Storage] add missing file.close() by @codeurimpulsif in #681
- [Template] Remove some unsecure DOM interpretation by @codeurimpulsif in #682

## [1.32.1] - 2025-11-20

- [Dependencies] upgrade django to version 5.2.8 by @codeurimpulsif in #679

## [1.32.0] - 2025-09-28

- feat: add version label to search results for clarity by @emmanuel-ferdman in #668
- [Licence] Add ODbL licence for database and API results by @codeurimpulsif in #669
- [Static] Remove Django admin files and collect static files by @codeurimpulsif in #665
- fix: typos in the importtracker command error by @Porkepix in #671
- [Dependencies] Migrate to Django 5.2 by @codeurimpulsif in #670
- [Dependencies] Upgrade dev dependencies by @codeurimpulsif in #674
- [Chore] Bump exodus-core from 1.3.13 to 1.3.14 by @codeurimpulsif in #675
- [CI] Add Python 3.12 and 3.13 tests by @codeurimpulsif in #676

## [1.31.0] - 2024-07-27

- tech: Minor code improvements by @pnu-s in #628
- chore: Bump exodus-core from 1.3.12 to 1.3.13 by @pnu-s in #629
- [Translation] Add 15 new languages by @codeurimpulsif in #656
- chore(deps): Bump gunicorn from 22.0.0 to 23.0.0 by @dependabot[bot] in #641
- chore(deps): Bump setuptools from 75.1.0 to 78.1.1 by @dependabot[bot] in #645
- chore(deps): Bump requests from 2.32.3 to 2.32.4 by @dependabot[bot] in #646
- [Command] Fix importtrackers categories link by @codeurimpulsif in #658
- [Submit] Fix: remove "temporary" workaround for it & es languages by @codeurimpulsif in #659
- [Design] Add icon for external links button by @codeurimpulsif in #634
- [Translation] Generate mo files by @codeurimpulsif in #661
- [Dependency] Remove protobuf by @codeurimpulsif in #662
- [Accessibility] Add missing or change bad media descriptions by @codeurimpulsif in #660

## [1.30.0] - 2024-07-20

- Improve titles and Open Graph properties by @codeurimpulsif in #619
- chore(deps): Bump urllib3 from 2.2.1 to 2.2.2 by @dependabot in #623
- chore(deps): Bump certifi from 2024.2.2 to 2024.7.4 by @dependabot in #626
- chore(deps): Bump setuptools from 69.5.1 to 70.0.0 by @dependabot in #627
- [Integration] add video in "Better understand" → "Trackers" page by @codeurimpulsif in #625

## [1.29.0] - 2024-05-24

- chore: Upgrade to apkeep 0.16.0, python 3.11 & Debian bookworm by @Jean-BaptisteC in #612

## [1.28.6] - 2024-04-17

- chore(deps): Bump idna from 3.6 to 3.7 by @dependabot in #613
- chore(deps): Bump sqlparse from 0.4.4 to 0.5.0 by @dependabot in #614
- chore(deps): Bump gunicorn from 20.1.0 to 22.0.0 by @dependabot in #615

## [1.28.5] - 2024-03-19

- chore(deps): Bump django from 3.2.23 to 3.2.25 by @dependabot in #609
- chore: Upgrade exodus-core to 1.3.12 & androguard to 4.1.1 by @pnu-s in #610

## [1.28.4] - 2024-03-11

- chore: Upgrade exodus-core to 1.3.10 by @pnu-s in #603
- Add issue templates for bug report, feature request and question by @codeurimpulsif in #604
- chore: Improve error catching by @pnu-s in #607
- chore: Upgrade exodus-core to 1.3.11 & androguard to 4.1.0 by @pnu-s in #608

## [1.28.3] - 2024-01-18

- style: Indent HTML templates with djhtml by @pnu-s in #601
- feat: Remove name and firstname from API key creation by @pnu-s in #602

## [1.28.2] - 2024-01-16

- chore: Upgrade exodus-core to 1.3.9 by @pnu-s in #596
- Update Github actions by @Jean-BaptisteC in #597
- tech: Remove inline CSS usage by @pnu-s in #600

## [1.28.1] - 2023-11-21

- chore: Upgrade apkeep to v0.15.0 by @pnu-s in #586
- Remove F-droid reference for Blokada on Next page by @codeurimpulsif in #587
- chore: Specify python version to help Dependabot by @pnu-s in #589
- Add CodeQL workflow for GitHub code scanning by @lgtm-com in #559
- ci: Tweak codeql.yml to ignore static admin js files by @pnu-s in #592
- docs: Update LGTM badges in README.md by @pnu-s in #593
- chore: Upgrade django to 3.2.23 by @pnu-s in #594
- fix: Totally disable submissions when parameter is set by @pnu-s in #595

## [1.28.0] - 2023-09-20

- feat(api): Add tracker option to applications API endpoint by @pnu-s in #585

## [1.27.8] - 2023-08-31

- Update Github actions by @Jean-BaptisteC in #576
- Remove privacytools.io from next page by @codeurimpulsif in #571
- chore: Use timer to query API fewer times on submission page by @pnu-s in #579
- chore: Upgrade dependencies by @pnu-s in #580
- chore: Upgrade django by @pnu-s in #581

## [1.27.7] - 2023-01-31

- fix: Use google-play-scraper to retrieve icon from gplay by @pnu-s in #568
- chore(deps): Upgrade dependencies by @pnu-s in #569

## [1.27.6] - 2022-12-28

- Use Whitenoise to serve static resources by @U039b in #556
- chore: Upgrade dependencies by @pnu-s in #566
- chore: Upgrade google-play-scrapper to fix paid apps check by @pnu-s in #567

## [1.27.5] - 2022-10-19

- fix: Increase max size for db fields issuer and subject by @pnu-s in #548
- feat: Only return latest report when exact handle searched by @pnu-s in #549
- feat: Return latest app name in /search/handle api endpoint by @pnu-s in #551
- Fix icon redirection by adding language code and leading slash to URI by @codeurimpulsif in #554

## [1.27.4] - 2022-10-09

- chore: Bump django from 3.2.14 to 3.2.15 by @pnu-s in #544
- fix: Make sure all app icons are square by @pnu-s in #545
- chore: Bump jquery from 3.4.1 to 3.6.1 by @pnu-s in #552
- chore: Update admin static files by @pnu-s in #553

## [1.27.3] - 2022-07-13

- fix: Use correct link to see existing api keys by @pnu-s in #537
- chore: Upgrade to Django 3.2 by @pnu-s in #538
- chore: Bump django from 3.2.13 to 3.2.14 by @pnu-s in #539

## [1.27.2] - 2022-07-02

- ci: Optimize order of jobs by @pnu-s in #536

## [1.27.1] - 2022-06-18

- Upgrade workflow by @Jean-BaptisteC in #533
- Update Android permissions by @Jean-BaptisteC in #495
- fix: Upgrade google-play-scraper to fix paid apps check by @pnu-s in #534

## [1.27.0] - 2022-06-02

- fix: Change alt attribute to find gplay icon by @pnu-s in #530
- chore: Upgrade various dependencies by @pnu-s in #531
- feat: Keep submissions always enabled for admin by @pnu-s in #528
- feat: Use apkeep instead of gpapi to download apps by @pnu-s in #532

## [1.26.3] - 2022-04-24

- fix: Remove buggy link for existing API keys by @pnu-s in #520
- fix: Only keep one device model by @pnu-s in #521
- chore: Upgrade django to 2.2.28 by @pnu-s in #522

## [1.26.2] - 2022-03-26

- chore: Upgrade to Debian bullseye by @pnu-s in #506
- Upgrade Minio and RabbitMQ server by @codeurimpulsif in #507
- Add contrib directory with systemd services for worker and scheduler by @codeurimpulsif in #508
- Update documentation for Debian 11 and Celery 5 by @codeurimpulsif in #509
- Download icons for f-droid from website by @Niveshkrishna in #510
- feat: Switch to pipenv as package manager by @pnu-s in #511
- chore: Bump exodus-core from 1.3.5 to 1.3.6 by @pnu-s in #512
- feat: Add documentation field for trackers by @pnu-s in #503

## [1.26.1] - 2022-02-15

- Fix docker-compose uid and documentation by @codeurimpulsif in #490
- ci: Test with python 3.7 & 3.9 by @pnu-s in #480
- fix: Fix getting icon in refresh report scripts by @pnu-s in #496
- Bump django from 2.2.26 to 2.2.27 by @dependabot in #498

## [1.26.0] - 2022-01-20

### Breaking change

- Drops support for Python 3.6 (and lower)

### What's Changed

- Improving docker tooling by @LupusMichaelis in #435
- chore(deps): Bump Pillow, exodus-core & requests by @pnu-s in #488
- fix: Set categories from ETIP on tracker creation by @pnu-s in #483

## [1.25.0] - 2022-01-08

- fix: Prevents overwriting request variable in analysis page by @pnu-s in #466
- Update exit code by @Jean-BaptisteC in #475
- Bump lxml from 4.6.3 to 4.6.5 by @dependabot in #476
- feat: New API endpoints to count elements (trackers, reports, apps) by @pnu-s in #478
- fix: Use localized metadata for Fdroid icon in case of failure by @pnu-s in #477

## [1.24.0] - 2021-10-06

- feat: Add possibility to disable submissions in settings (#458)
- fix: Patch gpapi locally to download apk from GPlay (#462)

## [1.23.1] - 2021-09-19

- fix: Prevents hanging if app has no version, version_code or app_name (#457)
- fix: Downgrade urllib3 to fix issue with gpapi (#456)
- fix: Fix issue with all apps reported as paid apps (#455)
- docs: Update API request email address (#453)
- chore(deps): Bump dependencies (#444)
- ci: Replace Travis CI by GitHub Actions (#446)

## [1.23.0] - 2021-08-16

- feat: Add API key creation page

## [1.22.0] - 2021-05-09

- feat: Add search by name in trackers page (#431)
- chore(deps): Bump handlebars from 4.2.0 to 4.7.7
- fix: Add missing noreferrer on link
- docs: Update API documentation to list permissions in /search/details
- chore(deps): Bump djangorestframework from 3.11.0 to 3.11.2

## [1.21.0] - 2021-03-21

- Add German translations 🇩🇪
- Fail with explicit message if attempting to scan paid app
- Remove GPlaycli references
- Update dependencies
- Update README documentation

## [1.20.6] - 2021-02-06

- Add categories to API endpoints
- Update API documentation

## [1.20.5] - 2021-01-10

- Link to new analysis on home page
- Add --no-cache-dir option for pip in Dockerfile

## [1.20.4] - 2020-11-08

- New options (q,d) for import_from_etip command

## [1.20.3] - 2020-10-27

- Fix auto_update_trackers
- Allow any host in the Docker configuration
- Adds Docker folder
- Adds possibility to overwrite CSRF_COOKIE_SECURE setting

## [1.20.2] - 2020-10-17

- Replace buster by buster-slim in Docker image

## [1.20.1] - 2020-10-17

- Report contact link now leads to Organization page
- New FUNDING.yml file
- Use environment variables in docker settings
- Trackers auto update & apk upload for Docker dev env
- Remove gplaycli from Docker configuration
- Tweak some details in MEN theme

## [1.20.0] - 2020-08-29

- Add tracker categories

## [1.19.1] - 2020-07-14

- Precise that tracker stats are only for GPlay
- Add new analysis admin button on report

## [1.19.0] - 2020-07-02

- Add more recent devices to the list of mobile devices
- Add Android TV to the list of mobile devices
- Increase max length of permission names
- Display 'Google Play' instead of 'google'

## [1.18.2] - 2020-06-30

- Update /search API endpoints to handle sources

## [1.18.1] - 2020-06-30

- Add extra log line for app download
- Use correct link in admin queries list
- Update /applications API endpoint to handle sources

## [1.18.0] - 2020-06-28

- Add F-Droid as a second source of applications
- Add command to download F-Droid index
- Add Celery scheduler for Docker instances
- Fix redirect issue using a slice of the fullpath

Some of this changes need manual interventions (for the first F-Droid index import and for Docker run), read the documentation.

## [1.17.0] - 2020-05-30

- More explanation about the search input
- Add new colors for trackers statistics
- Add alert message for apps with georestrictions
- Add short option for API endpoint 'applications'
- Improve Docker setup for development

## [1.16.0] - 2020-05-30

- Add Greek translation 🇬🇷

## [1.15.2] - 2020-05-29

- Fix bugs to allow apk download with API call

## [1.15.1] - 2020-05-01

- Change analysis page title when analysis is complete
- SET CSRF cookies to secure: true
- Docs: Add CONTRIBUTING.md

## [1.15.0] - 2020-04-28

- New reports page
- New elements in trackers list page

## [1.14.3] - 2020-04-11

- Allow blank signatures for trackers
- Add new page with list of trackers for admin
- Make sure the updated date is changed after reports refresh

## [1.14.2] - 2020-04-04

- Bump to exodus-core 1.2.1 & Pillow 6.2.2
- Temporary workaround for IT & ES languages

## [1.14.1] - 2020-04-04

- Various bug fixes related to new translations

## [1.14.0] - 2020-03-29

- Only display latest reports on tracker page
- Add Italian translations 🇮🇹
- Use EN by default for Exodus Privacy website links

## [1.13.3] - 2020-03-08

- Add possibility to paste Google play URL into search field
- Remove XFrameOptionsMiddleware

## [1.13.2] - 2020-02-16

- Add new open API endpoint to get latest report id & date (fix #317)
- Set PostgreSQL version in Dockerfile to 11*

## [1.13.1] - 2020-02-10

- Fix: make sure temp directory exists before downloading APK

## [1.13.0] - 2020-02-09

- Use gpapi for APK download instead of gplaycli
- Only calculate statistics every 3 days and store it in DB
- Add new command `import_from_etip`
- Move version number to tooltip to gain space in navbar

## [1.12.0] - 2020-02-07

- Fix a couple of bugs to allow adding additional languages
- Add Spanish translation 🇪🇸
- Fix issue with API not called when pasting Gplay URL in new analysis form
- Remove check existing report API call until issue #317 is fixed

## [1.11.0] - 2020-01-28

- Allow customization of UI
- Fix link for Prism break in English
- Docker: Allow customization of gplaycli.conf
- Docker: Patch variable docId to docid in gplaycli.py
- API: Added certificate details in GET /api/report/<report_id>

## [1.10.4] - 2020-01-28

- Add trackers & permissions in search results

## [1.10.3] - 2020-01-28

- Remove old CSS rules for printed reports
- Prevent wrapped spaces in navbar
- Improve rendering of "Read the article" buttons
- Add delay to avoid hitting too much the API when searching
- Use TrigramSimilarity to search for applications
- Refacto and improve logs of refresh trackers function

## [1.10.2] - 2020-01-28

- Requires auth on API endpoint /search/
- Upgrade to Django 2.2
- Only display spinner if apk file loaded
- Fail properly for apps with too long version or name

## [1.10.1] - 2020-01-28

- Only submit analysis if an application handle is given
- Create deprecated note for Vagrant install
- Set auto cleanup time to 24h instead of 1h

## [1.10.0] - 2020-01-28

- Add Celery beat for scheduling periodic tasks
- Allow the user to upload an APK
- Add dedicated task to cleanup analysis requests
- Add dedicated task to recompute all reports
- Trigger reports update after trackers update
- Add LGTM code analysis
- Change delete report link to button
- Remove unused code related to DNS & HTTP
- Update and clean requirements

## [1.9.5] - 2019-12-17

- Enforce API key verification (#276)
- Merge API tests
- Fix conficts and import in API tests

## [1.9.4] - 2019-12-08

- Add a button to delete a report from its page (#280)
- Add details & colors to analysis list
- Limit analysis list to only first 200
- Fix missing semi-colon in CSS
- Extend box-shadow in search boxe, include helper
- Add permissions to API endpoint /search/handle/details
- Refacto tests for trackers module

## [1.9.3] - 2019-12-02

- Remove F-droid link on EP logo
- Add alt tags for images
- Missing update for switching to new Celery version
- Return exact handle match - if it exists - on home page
- Bump pillow from 5.0.0 to 6.2.0
- Bump versions of exodus-core, gplaycli, gpapi & protobuf
- Set back tooltip on permission name

## [1.9.2] - 2019-11-19

- Switch to new Celery version
- Docker Python 3.5-stretch to 3.7-buster
- Remove overwritten Celery setting
- New icons for language selector, contact & alternatives

## [1.9.1] - 2019-11-16

- Update travis CI to use python 3.7
- Bump ruamel.yaml to 0.16.5

## [1.9.0] - 2019-11-11

- Fix bug with paginator and unordered list (#261)
- Link to sections on report page
- Revert ordering for reports list in tracker page
- Truncate long permission name only on mobile
- Enable PGSQL trigram extension during docker startup
- Remove tooltips with permission details in report page
- UI tweaks: margins & labels
- New theme for exodus

## [1.8.0] - 2019-10-21

- Improve dockerfile dependencies management
- Add hadolint linter and docker build test
- Added filter to show only reports of latest application version #226 (#248)
- Update count with application count in tracker page (#254)
- Change tracker labels & update French translation
- Refacto paginator & translate to French
- Fix bug with number of 'no trackers' reports
- First version of the page about Exodus Privacy
- First version of new analysis page

## [1.7.0] - 2019-10-07

- Clean translation files
- Added message about mobile site
- "Let's go" buttons width made same on Homepage (#238)
- Remove search module (merge into exodus main module)
- Add endpoint for latest app icon
- Remove applications page (#243)
- Ignore missing cache file during apk download
- Minor UI tweaks after review of new pages

## [1.6.2] - 2019-09-26

- Fix broken translations

## [1.6.1] - 2019-09-26

- Fix broken translation for "Recognized trackers"
- Fix link and label on the home page link to "better understand"

## [1.6.0] - 2019-09-26

- Add understand page template
- Add new pages about trackers, permissions and what's next
- Only look for exact app handle instead of similar one

## [1.5.0] - 2019-09-23

- Add favicon
- Use trigram similarity to improve application search
- Add page to display latest report and add link in search results
- New UI for the report page
- New trackers_list page to fit with new theme
- New tracker detailed page
- Make titles of different pages uniform
- Add AOSP permissions details in french language

## [1.4.0] - 2019-09-10

- Fix rendering bug with search button on home page
- Fix for responsive tables not taking 100% width in bootstrap 4
- Feat/api add report update timestamp (#205)
- Upgrade jQuery to 3.4.1 & handlebars to 4.2.0
- Add rel="noreferrer" to external links
- Fix HTML & JS indentation
- Add new svg images for exodus v2
- Add new home page with EP logo and exodus description
- Add extra links and text on home page + extra tweaks
- Make UI of different pages uniform & take review comments into account
- Change default per_page settings for paginator to 25
- Put signature at the bottom of report page and improve responsiveness
- Flake8 compliance-ish for exodus scripts
- Add flake8 linter stage to TravisCI

## [1.3.3] - 2019-08-07

- Fix bug with sorting trackers in stats
- Take CSS suggestions from mmuman for printing reports
- More robust download apk function
- Fixed HTML indentation in base.html
- Upgrading to Bootstrap 4.3.1 and removing unused JS files
- New version of navbar using links instead of buttons
- Add last CSS tweaks for new navbar

## [1.3.2] - 2019-07-31

- feat(admin): add logout on dropdown menu
- Add rounded corner icon on report & search page (#181)
- Fix issue with malformed report on admin page
- Remove Trollius and upgrade pyshark to 0.4.2.4
- Move tracker stats to trackers/stats && optimize stats calculation
- Added tests for tracker stats page
- Add travis CI with django tests
- Add Travis badge to README

## [1.3.1] - 2019-07-15

- [Docker] replace deprecated MAINTAINER (#177)
- Update to exodus-core 1.0.19

## [1.3.0] - 2019-07-08

- Reorganized README and FAQ
- Improve Docker-compose (#58)
- Optimization of static analysis
- Add missing migrations
- Set back to filter by creation_date instead of version code
- Fix most PEP8 compliance issues
- Display only the latest report on the submission page
- Fix display glitch on submission page
- Fix badge size bug with 100+ permissions/trackers
- Reorganize reports list page
- Remove dropdowns for reports & applications in nav bar
- Update to exodus-core 1.0.18
- Fix vulnerabilities in pyyaml & mistune

## [1.2.2] - 2019-05-31

- Migrate to exodus-core 1.0.17
- Update refreshapkcertificates to refresh UAID (#61)
- Add additionnal try/catch to avoid malformed reports bug
- Add search and filter fields for trackers in Admin page

## [1.2.1] - 2019-05-31

- Add dexdump
- Fix missing application save
- Change APK version display
- Rename APK signature to APK fingerprint
- Add importtrackers command allowing to retrieve the trackers definitions from the official εxodus platform
- Thread pool has been fixed in Minio helper
- Handle X509 parsing error
- Open analysis \o/
- Add translation possibility
- Fix icon perceptual hash
- Fix bad regex on search endpoint
- Migrate to exodus-core 1.0.16
- Add a 4 minutes timeout on APK download
- Handle fingerprinting errors
- Tell only free applications are supported
- Add UTF-8 decoding for trackers import
- Paginator for the reports apps list, apps list in trackers detail
- Migrate to Gplaycli 3.21
- Add list of all applications endpoint
- Security: Only staff users can access the APK
- Add compact reports details API endpoint
- Add docker-compose, Dockerfile for dev environment
- Add application count
- Add script to refresh the missing apk certificates
- Update to latest Django 1.11.X
- Adding special and dangerous permissions count

## [1.2.0] - 2018-02-16

- Implement REST API providing reports
- Add Exodus Privacy menu
- List existing reports before submission
- Fix memory leak in static analysis process
- Add pagination in report_list
- Fix list of reports on analysis submission form
- Make reports list responsive
- Application search engine
- Add tracker list API endpoint

## [1.1.0] - 2017-12-10

- Get APK version code
- Add settings template
- Hide list of domains in statistics page
- More explicit disclaimer about static analysis
- Add a REST API for Android application
- Improve documentation
- Sort permissions in alphanumeric order or name
- Implement static analysis v2
- Display how many applications include each tracker in statistic page
- Add "number of tracker" badge
- List reports for each tracker

## [1.0.0] - 2017-11-24

- First version of εxodus
