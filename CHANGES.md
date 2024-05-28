## GOATS 24.5.0 (2024-05-28)


### New Features

- Link JS9 button to open file with JS9: Extended the serializer to include data URL for JS9. [[#GOATS-208](https://noirlab.atlassian.net/browse/GOATS-208)]
- Added serializer tests: Wrote test cases for serializers used to validate API requests. [[#GOATS-234](https://noirlab.atlassian.net/browse/GOATS-234)]
- Added api view tests: Wrote test cases for API viewsets. [[#GOATS-239](https://noirlab.atlassian.net/browse/GOATS-239)]
- Enhanced UI with modal to display header: Implemented buttons to display modals with detailed file headers and to eventually trigger JS9 views. Added event listeners for smooth modal interactions and developed a function to build reusable modals. [[#GOATS-246](https://noirlab.atlassian.net/browse/GOATS-246)]
- Changed DRAGONS run initialization: Extended backend logic to disable all bias files outside a specified day range of the observations during the initialization of a DRAGONS run. Optimized number of database queries when creating a DRAGONS run. [[#GOATS-257](https://noirlab.atlassian.net/browse/GOATS-257)]
- Enhanced file retrieval with header inclusion: Added a query parameter, `?include=header`, to include header information for files in DRAGONS runs. [[#GOATS-258](https://noirlab.atlassian.net/browse/GOATS-258)]
- Added DRAGONS recipes and primitives API v1: Implemented REST API endpoints for DRAGONS recipes and primitives. The system now includes serializers for filtering by query parameters. Models were structured to connect recipes with primitives, allowing users to enable or disable individual primitives. This version supports only default recipes. [[#GOATS-259](https://noirlab.atlassian.net/browse/GOATS-259)]
- Developed interactive DRAGONS recipe cards: Constructed interactive recipe cards for DRAGONS, featuring a built-in code editor for dynamic user customization. Also implemented a logger widget for real-time log monitoring. Created a utility class for common JavaScript functionalities and modified the backend by removing the storage of individual Primitives. [[#GOATS-261](https://noirlab.atlassian.net/browse/GOATS-261)]
- Linked header API to modal display: Connected backend header API with modal UI to enable header information display when a button is clicked. Improved the header information presentation and error handling. [[#GOATS-263](https://noirlab.atlassian.net/browse/GOATS-263)]
- Linked run selector to recipe card generator: The DRAGONS run selector now dynamically updates the displayed recipes when a new run is selected. [[#GOATS-264](https://noirlab.atlassian.net/browse/GOATS-264)]
- Moved Ace editor local: Served Ace editor from app, removing CDN dependency. [[#GOATS-266](https://noirlab.atlassian.net/browse/GOATS-266)]
- Added daily conda caching: Implemented a GitHub action to create and cache the goats conda environment daily for quicker testing. [[#GOATS-270](https://noirlab.atlassian.net/browse/GOATS-270)]
- Extended models tests: Added comprehensive tests for newer models in GOATS. [[#GOATS-271](https://noirlab.atlassian.net/browse/GOATS-271)]
- Added workflow to generate releases and update version. [[#GOATS-278](https://noirlab.atlassian.net/browse/GOATS-278)]


### Changes

- Allow changing DRAGONS setup files names: Users can now change the DRAGONS setup files names. Removed the ability to change the log file name and removed from form. Added helper functions to get the path of DRAGONS setup files. [[#GOATS-250](https://noirlab.atlassian.net/browse/GOATS-250)]
- Changed "Unknown" to "Other" for the file type when extracting file metadata. [[#GOATS-256](https://noirlab.atlassian.net/browse/GOATS-256)]


### Bug Fixes

- Fixed bug in JS9 to ensure correct color for labels. [[#GOATS-208](https://noirlab.atlassian.net/browse/GOATS-208)]
- Fixed file count and duplicate entries: Corrected the bug in the total file count calculation and prevented duplicates in the list of files downloaded to ensure an accurate count. [[#GOATS-247](https://noirlab.atlassian.net/browse/GOATS-247)]
- Fixed JS9 and Ace conflict: Used no-conflict Ace with own namespace. [[#GOATS-256](https://noirlab.atlassian.net/browse/GOATS-256)]

## GOATS 24.04.0 (2024-04-26)


### New Features

- Add toggle for file enable/disable: Checkbox functionality was added to allow users to enable or disable files for DRAGONS reduction runs. Additionally, a CSS class was introduced to limit the size of tables when displaying large lists of files. [[#GOATS-209](https://noirlab.atlassian.net/browse/GOATS-209)]
- Implemented file list generation: Version 1 of generating the file list for users was implemented, focusing on both frontend and backend development. This initial version is set to be revised based on user feedback. [[#GOATS-237](https://noirlab.atlassian.net/browse/GOATS-237)]
- Switched to `ruff` for faster linting and formatting. [[#GOATS-254](https://noirlab.atlassian.net/browse/GOATS-254)]


### Changes

- Refactored API structure: Updated API endpoints and class names for DRAGONS reduction. The code now uses a flat REST API structure, enabling filtering via query parameters. For more details, access `/api/` in debug mode to explore possible endpoints. [[# GOATS-235](https://noirlab.atlassian.net/browse/ GOATS-235)]
- Updated GitHub action to use conda environment with DRAGONS: The GitHub action for running unit tests has been fixed by using the `goats` conda environment. The environment is cached to reuse builds if it has not changed. [[#GOATS-240](https://noirlab.atlassian.net/browse/GOATS-240)]
- Refactored frontend for efficiency: Combined setup steps and streamlined file listing for DRAGONS runs. Changed the timing of metadata extraction from data products to occur during downloading from GOA. This update ensures that metadata is always refreshed in tandem with data product updates, leading to faster loading and listing of file metadata. [[#GOATS-243](https://noirlab.atlassian.net/browse/GOATS-243)]
- Refactored DRAGONS setup to MVC: Enhanced the DRAGONS run setup process by adopting the Model-View-Controller architecture, improving reactivity and maintainability of components. [[#GOATS-244](https://noirlab.atlassian.net/browse/GOATS-244)]

## GOATS 24.03.0 (2024-03-25)


### New Features

- DRAGONS integration and conda environment creation: DRAGONS is now part of the GOATS stack. A dedicated Conda environment file, `environment.yml`, is available for easy installation by users cloning the repository. Additionally, the stack now includes a Redis server to support the latest changes in GOATS infrastructure. [[#GOATS-210](https://noirlab.atlassian.net/browse/GOATS-210)]
- Add dark mode toggle to navbar: Added a dark mode toggle to the navbar using Halfmoon UI as a CSS dependency. [[#GOATS-212](https://noirlab.atlassian.net/browse/GOATS-212)]
- Real-time communication enhanced: Implemented real-time communication between the backend and frontend using Django Channels and Redis. [[#GOATS-213](https://noirlab.atlassian.net/browse/GOATS-213)]
- Extend CLI for Redis setup and running: Extended the `install` CLI to allow users to setup the Redis server. Modified the `run` CLI to run the Redis server in a separate thread alongside GOATS and Huey. [[#GOATS-216](https://noirlab.atlassian.net/browse/GOATS-216)]
- Switched to Django Channels: Enhanced downloads and notifications using WebSocket communication. The download user interface was refactored to improve the overall user experience. Toast popups were introduced for real-time notifications. Gevent was removed to address and resolve asynchronous operation issues encountered with Django Channels. [[#GOATS-219](https://noirlab.atlassian.net/browse/GOATS-219)]
- Implemented DRAGONS setup and config: Added a new Django model and serializer for DRAGONS run setup, enhancing the platform's ability to handle DRAGONS reduction configurations asynchronously through the web interface. Initiated REST framework setup to streamline data exchange. [[#GOATS-230](https://noirlab.atlassian.net/browse/GOATS-230)]

## GOATS 24.02.0 (2024-02-26)


### New Features

- Extended error handling in OCSClient: The update introduces a dictionary return type for OCSClient methods, now including a 'success' key to clearly indicate the outcome of requests. Additionally, a 'return_raw_data' option has been implemented, allowing the inclusion of raw XML responses in the returned payload. [[#GOATS-180](https://noirlab.atlassian.net/browse/GOATS-180)]
- Passwords for external services are securely stored using encryption to enhance data security. [[#GOATS-194](https://noirlab.atlassian.net/browse/GOATS-194)]
- Implement key retrieval in Gemini facility: Added utility functions to retrieve keys based on user and identifier. [[#GOATS-196](https://noirlab.atlassian.net/browse/GOATS-196)]
- Customizable server address and port: Users can now specify the address and port to run GOATS, accepting formats like '8000', '0.0.0.0:8000', or '192.168.1.5:8000'. [[#GOATS-88](https://noirlab.atlassian.net/browse/GOATS-88)]


### Bug Fixes

- Correctly handle missing "value" in parameter set from XML data from OCS: The OCSParser received enhancements to effectively handle missing values in nested XML elements and improved its key naming strategy to utilize both the value and type of parameter sets for clearer and more accurate data representation. [[#GOATS-200](https://noirlab.atlassian.net/browse/GOATS-200)]


## GOATS 24.01.0 (2024-01-26)


### New Features

- Add CLI data product save location: Implemented a new option in the CLI to specify the save directory `--media-dir` for data products. [[#GOATS-174](https://noirlab.atlassian.net/browse/GOATS-174)]
- Implemented Gemini OCS communication client: Added XML-RPC and URL endpoint handling in the OCS client and created a parser to convert XML data into dictionaries suitable for web view presentation. [[#GOATS-179](https://noirlab.atlassian.net/browse/GOATS-179)]
- Implemented Gemini ID parsing: Added `GeminiID` class to parse and handle both program and observation IDs for use in `OCSClient`, enhancing ID management and validation. [[#GOATS-187](https://noirlab.atlassian.net/browse/GOATS-187)]
- Implemented key models for OCS API access: Added UserKey and ProgramKey models to manage API keys for OCS queries. Extended GeminiID to include class methods for validating program and observation IDs. [[#GOATS-189](https://noirlab.atlassian.net/browse/GOATS-189)]
- Implemented key management frontend: Enhanced the Gemini OT interface with new views and forms for key management. [[#GOATS-191](https://noirlab.atlassian.net/browse/GOATS-191)]


### Changes

- Switched to temporary directory usage: `GOATS` now downloads and unpacks archive data into a temporary directory, preventing collisions during decompression. Additionally, optimized the process of moving downloaded files to the destination folder by implementing parallelization. [[#GOATS-169](https://noirlab.atlassian.net/browse/GOATS-169)]


### Bug Fixes

- Fixed client availability for xmlrpc: Resolved an issue where the client was not correctly set up for XML-RPC communication, ensuring proper functioning of remote procedure calls. Expanded testing with remote data to avoid more issues. [[#GOATS-188](https://noirlab.atlassian.net/browse/GOATS-188)]


## GOATS 23.12.0 (2023-12-22)


### New Features

- Implemented Huey for background tasks: Integrated Huey, a lightweight Python task queue, into GOATS to handle background tasks using sqlite3. This addition streamlines the data download process, eliminating the need for users to endure unresponsive periods during downloads and keeps the application lightweight by avoiding complex libraries. [[#GOATS-129](https://noirlab.atlassian.net/browse/GOATS-129)]
- Implemented navbar download display and recent downloads view: Introduced a new update mechanism in the navbar for displaying background downloads across all pages using polling and implemented a new view for accessing recent downloads. [[#GOATS-157](https://noirlab.atlassian.net/browse/GOATS-157)]
- Allowed editing of query names in query list view. [[#GOATS-78](https://noirlab.atlassian.net/browse/GOATS-78)]


### Changes

- Implemented dark mode and enhanced UI flexibility: Switched to dark mode for GOATS, limited to light or dark because bootstrap 4 does not support switching using themes. Integrated Font Awesome icons to improve the user interface aesthetics and enabled setting Plotly theme from Django settings for customizable visualizations. [[#GOATS-109](https://noirlab.atlassian.net/browse/GOATS-109)]
- Modified view for observations: Included the target sidebar in the observation view to provide a cohesive user experience, enabling users to see target information alongside specific observation details. [[#GOATS-112](https://noirlab.atlassian.net/browse/GOATS-112)]
- Enhanced GOATS CLI for worker management: Extended the GOATS command-line interface to include the `--workers` option in the `goats run` command, enabling users to spin up or down `greenlet`` workers as needed. This feature allows for flexible worker management while maintaining a lightweight footprint, though users should be cautious not to start too many or too few workers. [[#GOATS-129](https://noirlab.atlassian.net/browse/GOATS-129)]
- Change data product storage organization: Data products are now organized by observation ID folders, nested under target and facility folders. [[#GOATS-156](https://noirlab.atlassian.net/browse/GOATS-156)]
- Improved target deletion process: Enhanced deletion of targets now includes removal of all associated observation records and their data products. [[#GOATS-170](https://noirlab.atlassian.net/browse/GOATS-170)]


### Bug Fixes

- Fixed a bug in TOMToolkit where the time was incorrectly displayed with the month instead of the minute. [[#GOATS-166](https://noirlab.atlassian.net/browse/GOATS-166)]


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
