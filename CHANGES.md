## GOATS 23.11.0 (2023-11-27)


### New Features

- Added data product type support. [[#GOATS-117](https://noirlab.atlassian.net/browse/GOATS-117)]
- Enhanced GOA query feedback: Extended the GOA query functionality to construct and return comprehensive download information. This enhancement includes detailed feedback to GOATS users regarding the status of their queries, encompassing error notifications, the count of downloaded files, and alerts about potentially missed files due to the absence of user authentication. [[#GOATS-122](https://noirlab.atlassian.net/browse/GOATS-122)]
- Added calibration radio button to `GOA` query form: Introduced an option to include, exclude, or solely download calibration data for an observation ID. [[#GOATS-123](https://noirlab.atlassian.net/browse/GOATS-123)]
- Added GOA observation ID URL: Implemented a new feature to display a URL for GOA observation ID on the observation page for viewing available data files. [[#GOATS-152](https://noirlab.atlassian.net/browse/GOATS-152)]
- Enhanced observation record management: Introduced a new view to efficiently handle the deletion of all data products associated with an observation record. This update includes a confirmation page for deletion operations, ensuring user confirmation before proceeding with data removal. Additionally, the update fixes a typo and improves permission handling for both `GET` and `POST` requests for deleting all data products, enhancing the overall user experience and security. [[#GOATS-158](https://noirlab.atlassian.net/browse/GOATS-158)]


### Changes

- Updated URL to reflect active tab: Enhanced the target page to modify the URL in accordance with the currently active tab, ensuring that refreshing the page maintains the user's selected tab. [[#GOATS-159](https://noirlab.atlassian.net/browse/GOATS-159)]


### Bug Fixes

- Simplified redirecting users to the target list view for consistency and better UX. [[#GOATS-126](https://noirlab.atlassian.net/browse/GOATS-126)]
- Fixed thumbnail deletion for data products: Resolved a bug where data product thumbnails were not being deleted properly along with the data product, leading to multiple copies. [[#GOATS-154](https://noirlab.atlassian.net/browse/GOATS-154)]


### Enhancements

- Enhanced download and decompression performance: Optimized the process for downloading and decompressing tar files from GOA, significantly reducing the time required. Implemented streaming for data downloads, which minimizes memory usage for large files. [[#GOATS-155](https://noirlab.atlassian.net/browse/GOATS-155)]


## GOATS 23.10.0 (2023-10-26)


### New Features

- Integrate Firefox add-on: `antares2goats` hosted on Firefox has been integrated into `GOATS`. Users will be able to install the browser add-on, configure the token, and use the add-on without issue. [[#GOATS-110](https://noirlab.atlassian.net/browse/GOATS-110)]
- `astroquery` and `GOATS` enhanced for calibration files: Extended `astroquery` to download associated calibration files as a tar archive. `GOATS` now automatically downloads and ingests these files for an observation record into saved data products. [[#GOATS-118](https://noirlab.atlassian.net/browse/GOATS-118)]
- Added observation and thumbnail deletion: Added the ability to delete observations from a target and fixed a bug to correctly delete associated thumbnails from data products. [[#GOATS-121](https://noirlab.atlassian.net/browse/GOATS-121)]
- GOA Public Data Connection and Gemini Update: Introduced GOA connection for public data. Added query features. Improved Gemini facility documentation and code quality. Extended astroquery for future integration. [[#GOATS-6](https://noirlab.atlassian.net/browse/GOATS-6)]
- GOA Proprietary Data Connection and Gemini Update: Introduced GOA connection for proprietary data. Added GOA credential management. [[#GOATS-7](https://noirlab.atlassian.net/browse/GOATS-7)]


### Changes

- Removed CLI for installing extension: Due to Chrome being the only browser to be able to install an extension from the CLI, removing all references and code to install from the CLI. Users will only be able to install the `antares2goats` extension via the extension store. [[#GOATS-111](https://noirlab.atlassian.net/browse/GOATS-111)]
- Improved GOATS frontend: Enhanced the user interface by adding two new input fields for GOA queries. Refined tab views for target management, specifically when adding existing observations or updating statuses. [[#GOATS-117](https://noirlab.atlassian.net/browse/GOATS-117)]
- Optimized GOA data and overhauled `astroquery` for Gemini: Implemented compressed and tar files for efficient data retrieval from GOA. Completed a major refactoring of the `astroquery` package for Gemini, in preparation for a future merge into the main `astroquery` project. [[#GOATS-119](https://noirlab.atlassian.net/browse/GOATS-119)]


### Other

- Add Makefile for `antares2goats` packaging: Created a Makefile to automate the packaging of `antares2goats` into a ZIP file for uploading to Firefox and Chrome extension stores. [[#GOATS-103](https://noirlab.atlassian.net/browse/GOATS-103)]


## GOATS 23.09.0 (2023-09-25)


### New Features

- Incorporated token support in `antares2goats`: Integrated token authentication to allow users to securely save queries and targets from `ANTARES`. Revamped the Options page for token input. [[#GOATS-100](https://noirlab.atlassian.net/browse/GOATS-100)]
- Chrome extension v1: The initial version of the Chrome extension has been implemented, paving the way for enhanced browser functionality. A custom exception handling mechanism has been integrated within the GOATS Click, improving user experience in the command line interface. Additionally, a new CLI command facilitates the straightforward installation of the Chrome extension, while modifications to the ANTARES plugin now allow for direct query creation from the extension. To round off these updates, a new view has been established to monitor browser extension push notifications. [[#GOATS-72](https://noirlab.atlassian.net/browse/GOATS-72)]
- Added CLI command `install-extension`: CLI framework created so users in the future can install the browser extension for GOATS. Installation can be done in the `install` step or after with `install-extension`. [[#GOATS-83](https://noirlab.atlassian.net/browse/GOATS-83)]
- Single-Target Creation via Extension: Enhanced the extension to directly create individual targets within ANTARES, eliminating the need for query generation. [[#GOATS-85](https://noirlab.atlassian.net/browse/GOATS-85)]
- "Select All" feature enhancement: Users can now effortlessly select all targets with a single click, streamlining the addition process and enhancing user experience. Additionally, the query results have been refined to eliminate superfluous information, promoting a cleaner, more intuitive interface. [[#GOATS-91](https://noirlab.atlassian.net/browse/GOATS-91)]
- Added token authentication: Admins can now generate tokens for authentication in the backend of GOATS, facilitating secure interactions with the `antares2goats`` browser extension. [[#GOATS-99](https://noirlab.atlassian.net/browse/GOATS-99)]


### Changes

- GOATS Prompt Overhaul: Enhanced user experience during GOATS installation and execution with transparent process descriptions and progress updates. [[#GOATS-67](https://noirlab.atlassian.net/browse/GOATS-67)]
- GOATS ANTARES Broker webpage v1: Enhanced integration with GOATS, leveraging the `antares2goats`` extension for streamlined performance and alignment. [[#GOATS-80](https://noirlab.atlassian.net/browse/GOATS-80)]
- Removed non-functional broker plugins: TNS, Fink and LASAIR. [[#GOATS-82](https://noirlab.atlassian.net/browse/GOATS-82)]


## GOATS 23.08.0 (2023-08-25)


### New Features

- GOATS CLI: The GOATS CLI was updated to use Python Click, simplifying the command-line interface. The CLI is now included with the package installation. Use the goats command in the terminal to start. [[#GOATS-42](https://noirlab.atlassian.net/browse/GOATS-42)]
- Added v1 of GOATS footer: A custom footer was developed for the GOATS platform. The update involved integrating essential elements from the `tom_base/tom_common` files and initiating the use of custom CSS. [[#GOATS-44](https://noirlab.atlassian.net/browse/GOATS-44)]
- Added v1 of GOATS navbar: A custom navbar was developed for the GOATS platform. [[#GOATS-45](https://noirlab.atlassian.net/browse/GOATS-45)]
- Design initial version of GOATS CSS and layout: Bootstrap serves as a foundational element in our project, being a critical component of the TOM Toolkit. We leverage its robust framework as a starting point, extending and customizing it to create our own distinctive style that aligns with our specific needs and branding. [[#GOATS-47](https://noirlab.atlassian.net/browse/GOATS-47)]
- Created v1 of GOATS banner: A new banner has been added to display site logo and affiliates. [[#GOATS-48](https://noirlab.atlassian.net/browse/GOATS-48)]
- Improved CLI for GOATS: The CLI for GOATS now supports a development server that allows for real-time template modifications. Additionally, shorthand options have been introduced for a more streamlined user experience. [[#GOATS-51](https://noirlab.atlassian.net/browse/GOATS-51)]


### Other

- Tooling for release notes: Added infrastructure to produce useful, summarized change logs with `towncrier`. [[#GOATS-22](https://noirlab.atlassian.net/browse/GOATS-22)]
- `pytest` GitHub Action Integration: Established automated unit testing and initial code coverage assessment. This action, triggered on every 'push' event, provides continual testing and a basic coverage report, laying the groundwork for future integration with Codecov. [[#GOATS-24](https://noirlab.atlassian.net/browse/GOATS-24)]
- `pytest` infrastructure started: Established a `pytest` infrastructure for `goats`, introducing robust unit and integration tests. This setup enhances the reliability and maintainability of the codebase, facilitating more secure code updates and deployments. [[#GOATS-25](https://noirlab.atlassian.net/browse/GOATS-25)]
- Standard `pyproject.toml` started: Implemented a `pyproject.toml` file for `goats` to standardize build tool dependencies, streamlining the build process and ensuring consistency across different environments. [[#GOATS-28](https://noirlab.atlassian.net/browse/GOATS-28)]
- Integrated `flake8` in GitHub Actions: Incorporated `flake8` into the GitHub Actions pipeline, enabling automatic linting checks for Python code. This enforces code quality standards across `goats`. [[#GOATS-33](https://noirlab.atlassian.net/browse/GOATS-33)]
- Overrode default TOMToolkit index page and updated `pyproject.toml`: Improved pip installation process, enhancing user interface customization for GOATS and project distribution. [[#GOATS-43](https://noirlab.atlassian.net/browse/GOATS-43)]
- Optimized GitHub Actions and integrated HTML linting: GitHub Actions now operate selectively, with the HTML linter (`htmlhint`) triggered when template HTML files change, and unit tests and `flake8` checks run when Python files change. Additionally, common Jinja templating settings are now ignored by the HTML linter, thanks to the updated `htmlhint` configuration. [[#GOATS-53](https://noirlab.atlassian.net/browse/GOATS-53)]
- CSS linting added to GitHub Actions: Used stylelint to ensure CSS code quality. [[#GOATS-54](https://noirlab.atlassian.net/browse/GOATS-54)]
- JS Testing using `jest`: Implemented a test suite for JavaScript files in the GOATS project using `jest`. Ensures robust testing across the website and integrates GitHub action to run tests automatically. A badge has been added to the repository to show the test status. [[#GOATS-61](https://noirlab.atlassian.net/browse/GOATS-61)]
