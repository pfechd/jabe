UI_FILES := $(wildcard src/ui/*.ui)
QRC_FILES := $(wildcard src/ui/*.qrc)
PY_FILES := $(addprefix src/python/generated_ui/,$(notdir $(UI_FILES:.ui=.py)))
RC_FILES := $(addprefix src/python/generated_ui/,$(notdir $(QRC_FILES:.qrc=.py)))

all: $(PY_FILES) $(RC_FILES)

src/python/generated_ui/%.py: src/ui/%.ui
	pyuic5 $< -o $@

src/python/generated_ui/%.py: src/ui/%.qrc
	pyrcc5 $< -o $(addsuffix _rc.py, $(basename $@))

clean:
	rm -f $(PY_FILES)
	rm -f $(RC_FILES)
