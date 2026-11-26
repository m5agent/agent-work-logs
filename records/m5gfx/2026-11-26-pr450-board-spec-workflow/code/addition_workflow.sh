#!/bin/sh
# Trial: add a displayless board copied from M5NanoC6 with only catalog JSON,
# boards.hpp enum and chip .inl descriptor/table entry. No targets.json or test edits.
export PATH=/opt/homebrew/bin:$PATH
W=/tmp/m5gfx-450
cd "$W" || exit 1

echo "## 1. trial board files"
python3 - <<'EOF'
import json
b=json.load(open('extras/board_spec/boards/m5nanoc6.json'))
b.update(id='m5trialc6', name='M5TrialC6', official_name='M5Stack TrialC6', legacy_board_id=159)
b.pop('official_name_verified', None); b['spec']={'links':{}}
for pin in b['pins'].values(): pin.pop('measured_by', None); pin['verified']={'roles':'datasheet'}
open('extras/board_spec/boards/m5trialc6.json','w').write(json.dumps(b, indent=2)+"\n")
s=open('src/lgfx/boards.hpp').read()
old='    , board_M5UnitPoEP4X = 158\n'
assert old in s
open('src/lgfx/boards.hpp','w').write(s.replace(old, old+'    , board_M5TrialC6 = 159\n', 1))
s=open('src/board_detect/m5/esp32c6.inl').read()
old='static constexpr board_desc_t desc_nanoc6 = {\n'
assert old in s
new=('static constexpr board_desc_t desc_trialc6 = {\n'
     '  { static_cast<board_id_t>(lgfx::board_M5TrialC6), "M5TrialC6", 0 },\n'
     '  no_power(), no_reset(), no_shared_sd(), no_display_pins(), no_pins(),\n'
     '  no_internal_i2c(), no_options(), no_pins(),\n'
     '};\n'+old)
s=s.replace(old,new,1)
old2='  { &desc_nanoc6, construct_displayless, "board_M5NanoC6", nullptr },\n'
assert old2 in s
open('src/board_detect/m5/esp32c6.inl','w').write(s.replace(old2, old2+'  { &desc_trialc6, construct_displayless, "board_M5TrialC6", nullptr },\n',1))
EOF
cd "$W/extras/board_spec" || exit 1

echo
echo "## 2. check before generate (formatter hint expected)"
node cli/spec.js check 2>&1 | tail -3

echo
echo "## 3. npm run generate"
npm run generate 2>&1 | tail -4

echo
echo "## 4. check after generate"
node cli/spec.js check 2>&1 | tail -2

echo
echo "## 5. node tests, trial board present"
npm test 2>&1 | grep -E "^ℹ (tests|pass|fail|skipped)"

echo
echo "## 6. touched files (no targets.json, no test/* edits)"
cd "$W" || exit 1
git status --porcelain

echo
echo "## 7. revert trial board"
git checkout -- src/lgfx/boards.hpp src/board_detect/m5/esp32c6.inl
rm -f extras/board_spec/boards/m5trialc6.json
git status --porcelain | sed 's/^/remaining: /'

echo
echo "## 8. guard: display constructor without targets wiring_fields (m5atoms3 entry removed)"
python3 - <<'EOF'
import json
p='extras/board_spec/targets.json'
d=json.load(open(p)); del d['m5gfx_board_desc']['boards']['m5atoms3']
open(p,'w').write(json.dumps(d, indent=2)+"\n")
EOF
cd "$W/extras/board_spec" || exit 1
npm test 2>&1 | grep -A6 "display constructors need nonempty" | head -8
cd "$W" || exit 1
git checkout -- extras/board_spec/targets.json
echo
echo "## 9. final status (empty = clean)"
git status --porcelain
