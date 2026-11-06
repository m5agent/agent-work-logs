# DOC3 summary — product docs Unit pages audit (nuxt-m5-docs @ c06d36fcf)

- Baseline: gitlab 121 `shaoxiang/nuxt-m5-docs` `c06d36fcf45e30c99d89c19dca991a41b975e216` (master, read-only)
- Reference: UIFlow2 docs/driver commit `509a67aadb66b16f6c0e684f87fed178982c4686` (gitlab 163), `platform/units/catalog.json` (sha256 in results.json)
- Validation: document/datasheet/source cross-check only. **hardware validation NOT RUN; virtual-device validation NOT RUN.**
- Coverage: **32 units / 64 pages** (32 EN + 32 ZH full; 8 JA page spot-checks for findings). 40–60 page target exceeded.
- Deliverables: `results.json` (per-page records + findings + fixed-by-new-commits + NOT RUN), `candidates/*.md` (5) + `evidence/observations.md`, `extracts/` (automated extraction + digest), `audit_extract.py`.

## Coverage table (32 units; EN+ZH read, JA spot-check where noted)

| Unit | Pages | Result | Note |
| --- | --- | --- | --- |
| ENV (U001) | EN:32-34/107-108; ZH same; JA same | **FINDING C1** | spec table contradicts same-page comparison table (Temp ±0.2 vs ±0.5℃, Humidity ±0.1% vs ±5%RH, Pressure ±1 vs ±0.12hPa) |
| ENV-II (U001-B) | EN:40-43/114-115; ZH; JA | **FINDING C1** | Temp range -40~120 vs -40~125; Humidity 10~90 vs 0~100%RH; Pressure ±1 vs ±0.12hPa |
| ENV-III (U001-C) | EN:40-43/109-110; ZH; JA | **FINDING C1** | Temp -40~120 vs -40~125; Humidity 10~90 vs 0~100; Pressure ±3.9Pa vs ±0.12hPa |
| ENV-IV (U001-D) | EN/ZH | PASS | SHT40/BMP280 table consistent with comparison table |
| ENV-Pro (U169) | EN/ZH | MINOR (in C1) | comparison "Range" cell = "Scan speed: 10.8 seconds" (not a range) |
| ToF (U010) | EN/ZH | PASS | VL53L0X/0x29/3–200cm/±3% consistent. Observation not candidate: "independent of target reflectivity" unqualified (no datasheet check performed) |
| ToF4M (U172) | EN/ZH | PASS | VL53L1CXV0FY/1, 0x29, 4–400cm consistent |
| Angle (U005) | EN/ZH | PASS | 10K pot, 0–2500mV, PORT.B analog; catalog bus=adc |
| ADC (U013) | EN/ZH | PASS | ADS1100 16-bit, PGA 1/2/4/8, 8–128SPS, 90µA, 0x48 |
| ADC v1.1 (U013-V11) | EN/ZH | PASS+FIXED | no chip ±5V claim; DC0–12V terminal + 2.048V ref + rates 15/30/60/240 consistent; comparison table fixed by 4882025ad → catalog's adc-v1.1 gap is stale (C5) |
| DAC (U012) | EN/ZH | PASS | MCP4725 12-bit, 0–3.3V, 0x60 |
| DAC2 (U012-B) | EN/ZH | PASS+FIXED | GP8413 15-bit, 10V, 0x58–0x5F default 0x59; ZH:21 common-ground note (#5 C addressed) |
| Relay (U023) | EN/ZH | PASS | 5V@40mA, 6ms/4ms coil, GPIO |
| 2Relay (U131) | EN/ZH | PASS | AC250V/DC28V@8A, coil DC5V@154mA, GPIO direct drive |
| RGB (U003) | EN/ZH | PASS | SK6812, DC5V, 256 levels, UiFlow2 link |
| Buzzer (U132) | EN/ZH | PASS | passive 4KHz 1/2 duty, 5V@86mA, 72dB; PORT.B Signal; Arduino pin 26 matches PORT.B yellow + ledc API |
| 8Servos (U165) | EN/ZH | PASS | STM32F030F4P6, 8ch, DC5V@3A max, 9–24V/5V inputs, 0x25 |
| Joystick (U024) | EN/ZH | PASS-DISMISSED | "REG 0x52" checked vs UIFlow2 driver `joystick.py` `_read(): readfrom_mem_into(addr,0x52,buf)` → matches official implementation, not a defect |
| Joystick2 (U024-V2) | EN/ZH | PASS + catalog data issue C4 | page consistent (SKU U024-V2, 0x63, 16-bit); `catalog.json:5173` sku U169 duplicates ENV-Pro |
| CardKB v1.1 (U035-B) | EN/ZH | PASS | ATMega8A, 50 keys, 0x5F, UiFlow2 cardkb.html |
| CardKB2 (U215) | EN/ZH; JA | **FINDING C3** | UiFlow2 section "coming soon..." (line 147) while official UIFlow2 `cardkb2.rst` exists; Protocol section lacks register summary. Catalog also repeats stale "no Unit driver" claim (C5) |
| CAN (U085) | EN/ZH | PASS | CA-IS3050G, 1Mbps; isolation values not measured |
| Mini CAN (U179) | EN/ZH | PASS | 1Mbit/s, ISO11898-2, 9–24V + 5V; UiFlow2 can.html covers both |
| INA226-1A (U200-1A) | EN/ZH; JA | **FINDING C2** | Model Size PDF/PNG → Unit CAN U085 assets (82/84); UiFlow2 docs link missing (10A has it at EN:103) |
| INA226-10A (U200) | EN/ZH; JA | **FINDING C2** | same wrong U085 Model Size assets (82/84); UiFlow2 link present EN:103 |
| SSR (U122) | EN/ZH | PASS+FIXED | zero-cross description EN:15; ZH:56 phase/load-dependent switching (#5 A addressed) |
| DCSSR (U140) | EN/ZH | PASS | 0x50, ESP32C3, DC3–32V control / DC24–220V load, 10A |
| TimerPWR (U189) | EN/ZH | PASS | 0x56, INA3221, 3.7V battery, 5V output, LGS4056H; catalog claims no public driver but UIFlow2 509a67aa has `unit/timerpwr.py` (C5) |
| Step16 (U198) | EN/ZH | PASS | STM32G031, 16-position 8421 BCD, 0x48 default, UiFlow2 step16.html; catalog claims no public driver but UIFlow2 has `unit/step16.py` (C5) |
| Encoder (U135) | EN/ZH | PASS | STM32F030F4P6, 0x40, 30-position, 2×SK6812 |
| Light (U021) | EN/ZH | PASS | 10K photoresistor; catalog bus gpio-adc |
| DoF6 (U228) | EN/ZH | DEDUPE-ONLY | issue #7 still open: BMI270 zero offsets still labeled "Accuracy" (EN:54,57; ZH:54,57) — evidence for existing #7, no new candidate. Catalog claims "No Unit DoF driver" (stale, see C5) |

## Findings / candidates

| ID | Candidate (Target) | Severity | Title |
| --- | --- | --- | --- |
| C1 | `candidates/env-family-spec-table-contradictions.md` (gitlab 121) | docs-quality | ENV / ENV-II / ENV-III 规格表与同页对比表/传感器数据矛盾 |
| C2 | `candidates/ina226-model-size-assets-and-uiflow2-link.md` (gitlab 121) | docs-quality | INA226-1A/10A Model Size 资源指向 Unit CAN (U085)；1A 缺少 UiFlow2 链接 |
| C3 | `candidates/cardkb2-uiflow2-coming-soon.md` (gitlab 121) | minor | CardKB2 的 UiFlow2 段仍是 coming soon（官方文档已存在） |
| C4 | `candidates/catalog-joystick2-sku-u169.md` (github m5agent/m5stack-esp-emulator) | minor | catalog.json Joystick2 sku 误填 U169（应为 U024-V2） |
| C5 | `candidates/catalog-stale-uiflow2-driver-gaps.md` (github m5agent/m5stack-esp-emulator) | minor | catalog research gaps 过期：TimerPWR/Step16/DoF6/CardKB2 声称无 UIFlow2 驱动；ADC v1.1 矛盾已修复但旧 gap 仍在 |

## Fixed by newer docs commits (useful to comment/close on tracker)

| Open issue | Observed at c06d36fcf | Evidence |
| --- | --- | --- |
| #5 A (SSR overriding microsecond claim) | fixed on Unit SSR page | `static/en/unit/Unit_SSR.md:15` zero-cross description; `static/zh_CN/unit/Unit_SSR.md:56` switching delay depends on AC phase/load; commit `e78de2a3f` (refs #5) |
| #5 C (DAC2 isolation terminology) | fixed on Unit DAC2 page | `static/zh_CN/unit/Unit_DAC2.md:21` "模拟输出与主机共地"; commit `e78de2a3f` |
| #3 (ADC chip/terminal ranges) | unit ADC v1.1 page now consistent (Hat ADC pages are #3 scope, not audited here) | `static/en/unit/Unit_ADC_v1.1.md:14-60`; commits `4882025ad` / `e78de2a3f` |
| #7 (DoF6/9/10 BMI270 terminology) | **still open**: page still uses "Accuracy" for zero offsets | `static/en/unit/Unit_DoF6.md:54,57`; `static/zh_CN/unit/Unit_DoF6.md:54,57` |
| #13 (INA226/DoF10/AIN4-20mA examples) | not overlapping: targets `arduino/projects` pages; DOC3-C2 is Unit product page assets/link | — |

## Catalog cross-check (platform/units/catalog.json)

- Catalog sha256 `195289684c30b6e08dfa12bdf7bd3065a1a258110013b1d16766318c3f11a323`. Checked SKU / I2C address / bus / chips for all 32 units.
- Corroboration: catalog `env` gap (`:9441`) independently records the ENV temperature contradiction (+0.2°C spec vs +0.5°C comparison) → supports DOC3-C1.
- Data issues found: Joystick2 sku `U169` duplicate (C4); stale "no public UIFlow2 driver" gaps for TimerPWR/Step16/DoF6/CardKB2 and stale ADC v1.1 contradiction gap (C5). Catalog `env`/others gaps still valid are NOT counted as docs defects.
- Addresses/chips: all 32 units' page I2C addresses matched catalog `address_7bit` where the page states one; no SKU mismatches besides Joystick2.

## NOT RUN / limitations

- **Device Service 8905 example runs: NOT RUN.** The selected Unit product pages embed no runnable MicroPython example — only external UIFlow2/UIFlow1/Arduino tutorial links; `Unit_Buzzer` contains a single Arduino C++ sketch (not a guest program), and running Unit behavior needs a Unit fixture/injection. 8905 was reachable (`GET /health` 200, `/api/v1/devices` returned devices) but there was no applicable page example, so no session was created (and none was left running).
- Physical/electrical measurement of power, current, isolation, accuracy claims: **NOT RUN**; only document/datasheet/source cross-checks.
- JA pages: only 8 JA spot-checks for the four findings (ENV family/INA226/CardKB2); full JA parity audit not performed.
- Catalog numeric sweep limited to 32 selected units (SKU/address/bus/chips), not all 160.
- No tracked file in any repo was modified; no gh/glab writes; ports 8787/8830 untouched.

## Dedupe against open product issues #1–#14

- #1–#13 (prior GitLab 121 doc audit, iid list from the 2026-11-02 record + #1 volcengine Basic): none of C1–C3 duplicate them; #3/#5/#7 status notes above; #4 (Hat SPK2), #2 (Stamp LoRa), #6 (S021), #8–#12 (structure/examples/EXTIO2/Chain), #13 (Arduino example semantics) are different files/pages.
- #14 (Lead note: CoreS3 device-page review, baseline d2e67d91): device page, outside DOC3 Unit-page scope — no overlap.
