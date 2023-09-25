VERSION ?=
BUILD_DIR := build
CHROME_DIR := $(BUILD_DIR)/chrome
FIREFOX_DIR := $(BUILD_DIR)/firefox

.PHONY: all clean chrome firefox

# Build both Chrome and Firefox extensions.
all: clean chrome firefox

# Provide a list of available commands.
help:
	@echo "Available targets:"
	@echo "  make all VERSION=YY.MM.Major     - Build both Chrome and Firefox extensions (default)"
	@echo "  make chrome VERSION=YY.MM.Major  - Build Chrome extension"
	@echo "  make firefox VERSION=YY.MM.Major - Build Firefox extension"
	@echo "  make clean                       - Clean build directories"
	@echo ""
	@echo "Do not use leading zeros in the version number!"

# Clean up build directories.
clean:
	@echo "Cleaning up build directories..."
	rm -rf $(BUILD_DIR)
	mkdir -p $(CHROME_DIR) $(FIREFOX_DIR)

# Version check, specific to each target.
ifeq ($(filter $(MAKECMDGOALS), help clean),)
ifeq ($(VERSION),)
$(error VERSION is not set. Use `make VERSION=YY.MM.Major` to set the version.)
endif
endif

# Build Chrome extension.
chrome: clean
	@echo "Building Chrome extension version $(VERSION)..."
	cp -r ./src/* $(CHROME_DIR)
	mv $(CHROME_DIR)/chrome-manifest.json $(CHROME_DIR)/manifest.json
	rm $(CHROME_DIR)/firefox-manifest.json
	sed -i '' 's/"version": "[0-9]*\.[0-9]*\.[0-9]*"/"version": "$(VERSION)"/' $(CHROME_DIR)/manifest.json
	cd $(CHROME_DIR) && zip -r ../chrome-antares2goats-$(VERSION).zip .

# Build Firefox extension.
firefox: clean
	@echo "Building Firefox extension version $(VERSION)..."
	cp -r ./src/* $(FIREFOX_DIR)
	mv $(FIREFOX_DIR)/firefox-manifest.json $(FIREFOX_DIR)/manifest.json
	rm $(FIREFOX_DIR)/chrome-manifest.json
	sed -i '' 's/"version": "[0-9]*\.[0-9]*\.[0-9]*"/"version": "$(VERSION)"/' $(FIREFOX_DIR)/manifest.json
	cd $(FIREFOX_DIR) && zip -r ../firefox-antares2goats-$(VERSION).zip .
