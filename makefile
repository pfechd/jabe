UI_FILES := $(wildcard src/ui/*.ui)
PY_FILES := $(addprefix src/python/generated_ui/,$(notdir $(UI_FILES:.ui=.py)))

all: $(PY_FILES)

src/python/generated_ui/%.py: src/ui/%.ui
	pyuic5 $< -o $@

clean:
	rm -f $(PY_FILES)
