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
