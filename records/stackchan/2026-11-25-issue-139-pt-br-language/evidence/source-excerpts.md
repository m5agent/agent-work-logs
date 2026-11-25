# StackChan #139 — source excerpts

- Repository: https://github.com/m5stack/StackChan
- Commit: `28b9f0c8bd6acd81cb3c70f1a93c3e373b39d400` (main, v1.6.2 merge, 2026-11-04)
- Collected: 2026-11-25 (UTC), read-only sparse clone (app, firmware, server)

## app/lib/util/value_constant.dart:160-205 — display-name map only (`pt` present at :180)
```dart
  /// Supported languages map
  /// Key: Language code (ISO 639-1)
  /// Value: Display name in English and native language
  static const Map<String, String> languages = {
    "en": "English",
    "zh": "Chinese Mandarin 普通话",
    "yue": "Cantonese 粵語",
    "ja": "Japanese 日本語",
    "ko": "Korean 한국어",
    "ru": "Russian Русский",
    "es": "Spanish Español",
    "ar": "Arabic العربية",
    "fr": "French Français",
    "vi": "Vietnamese Tiếng Việt",
    "it": "Italian Italiano",
    "id": "Indonesian Bahasa Indonesia",
    "hi": "Hindi हिन्दी",
    "fi": "Finnish Suomi",
    "th": "Thai ไทย",
    "de": "German Deutsch",
    "pt": "Portuguese Português",

  ...
    "cs": "Czech Čeština",
    "pl": "Polish Polski",
    "ro": "Romanian Română",
```

## app/lib/view/popup/edit_agent.dart:84-100 — dropdown list is built from `tts_voices` keys
```dart
  // Load TTS data and build the language list from it.
  Future<void> loadTtsList() async {
    ttsData = await XiaoZhiUtil.shared.getTtsList();

    // The language list is derived from the ttsVoices keys.
    if (ttsData?.ttsVoices != null) {
      languageList.value = ttsData!.ttsVoices!.keys.toList();
    }

    // Default to the first available language.
    if (languageList.isNotEmpty && selectedLanguage.isEmpty) {
      selectedLanguage.value = languageList.first;
    }

    // Refresh the voice tones for the selected language.
    _updateTtsVoiceList(selectedLanguage.value);
  }
```

## app/lib/view/popup/edit_agent.dart:196-206 — the selected key is sent as `language`
```dart
    final agentParams = AgentCreate(
      agentName: agentNameController.text.trim(),
      llmModel: selectedModel.value!.name!,
      ttsVoice: selectedTtsVoice.value!.voiceId!,
      ttsSpeechSpeed: ttsSpeed.value,
      ttsPitch: ttsPitch.value,
      asrSpeed: asrSpeed.value,
      language: selectedLanguage.value,
      character: characterController.text.trim(),
      memory: memoryController.text.trim(),
      memoryType: memoryType.value,
```

## app/lib/view/popup/edit_agent.dart:246-252 — unknown keys fall back to the raw code
```dart
  String getLanguagesTitle(String lg) {
    if (ValueConstant.languages[lg] != null) {
      return ValueConstant.languages[lg]!;
    } else {
      return lg;
    }
  }
```

## app/lib/view/popup/edit_agent.dart:432-449 — picker items are exactly `languageList`
```dart
  void showLanguagePicker() {
    final initialIndex = model.languageList.indexOf(
      model.selectedLanguage.value,
    );
    showPicker(
      title: "Select Language",
      items: model.languageList
          .map((value) => getLanguagesTitle(value))
          .toList(),
      initialIndex: initialIndex.clamp(0, model.languageList.length - 1),
      onSelected: (index) {
        // Assign the language key (e.g. zh/en), not its display name.
        model.selectedLanguage.value = model.languageList[index];
      },
    );
  }

  void showTtsPicker() {
```

## app/lib/util/xiao_zhi_util.dart:30-36, 255-270 — TTS catalog comes from the xiaozhi.me API
```dart
  static final XiaoZhiUtil shared = XiaoZhiUtil._internal();

  XiaoZhiUtil._internal() {
    _dio.options.baseUrl = "https://xiaozhi.me/";
    _dio.options.connectTimeout = const Duration(seconds: 10);
    _dio.options.receiveTimeout = const Duration(seconds: 10);
    _dio.options.validateStatus = (state) {
  ...
  }

  /// Get voice list
  Future<TTsList?> getTtsList() async {
    final response = await _dio.get("api/user/tts-list");
    if (response.data != null) {
      XiaozhiResponse<TTsList> xiaozhiResponse = XiaozhiResponse.fromJsonT(
        response.data,
        factory: (value) => TTsList.fromJson(value),
      );
      if (xiaozhiResponse.success) {
        return xiaozhiResponse.data;
      }
    }
    return null;
  }
```

## app/lib/view/popup/xiaozhi_welcome_page.dart:163-169 — same derivation on the welcome page
```dart

  Future<void> loadTtsList() async {
    ttsData = await XiaoZhiUtil.shared.getTtsList();
    if (ttsData?.ttsVoices != null) {
      languageList.value = ttsData!.ttsVoices!.keys.toList();
    }
    _selectDefaultTtsVoice(preferredLanguage: selectedLanguage.value);
```

## firmware/main/Kconfig.projbuild:79-86 — device UI already offers Portuguese (pt-PT)
```kconfig
    config LANGUAGE_AR_SA
        bool "Arabic"
    config LANGUAGE_HI_IN
        bool "Hindi"
    config LANGUAGE_PT_PT
        bool "Portuguese"
    config LANGUAGE_PL_PL
        bool "Polish"
```

## firmware/main/CMakeLists.txt:192-193, 243 — maps Kconfig to locales/pt-PT/language.json
```cmake
elseif(CONFIG_LANGUAGE_PT_PT)
    set(LANG_DIR "pt-PT")

# Define generation path
set(LANG_JSON "${XIAOZHI_MAIN_DIR}/assets/locales/${LANG_DIR}/language.json")
```

## server/internal/xiaozhi/xiaozhi.go:44-48, 273-281 — server-side catalog uses the same upstream endpoint
```go
	tokenPath          = "api/developers/token"
	agentTemplatesList = "api/developers/agent-templates/list"
	ttsList            = "api/user/tts-list"
	devices            = "api/developers/devices"
	generateLicense    = "api/developers/generate-license"
  ...
// GetTTSList returns the developer account's available TTS voices.
func GetTTSList() (*xiaozhi.TTSList, error) {
	var resp xiaozhi.XiaoZhiResponse[xiaozhi.TTSList]
	if err := doRequest("GET", ttsList, nil, &resp); err != nil {
		g.Log().Error(ctx, "Get TTS voice list failed: %v", err)
		return nil, err
	}
	if !resp.Success {
		return nil, newXiaoZhiFailureError("get TTS voice list", resp.Message)
```

## server/internal/service/agent.go:128-160 — the server unions `languages` + `tts_voices` keys
```go
func getFirstAvailableTtsVoice(voiceList *xiaozhiModel.TTSList) (string, string) {
	if voiceList == nil {
		return "", ""
	}

	languages := make([]string, 0, len(voiceList.Languages)+len(voiceList.TTSVoices))
	addLanguage := func(language string) {
		if language == "" {
			return
		}
		if slices.Contains(languages, language) {
			return
		}
		languages = append(languages, language)
	}
	for _, language := range voiceList.Languages {
		addLanguage(language)
	}

	remaining := make([]string, 0, len(voiceList.TTSVoices))
	for language := range voiceList.TTSVoices {
		remaining = append(remaining, language)
	}
	sort.Strings(remaining)
	for _, language := range remaining {
		addLanguage(language)
	}

	for _, language := range languages {
		for _, voice := range voiceList.TTSVoices[language] {
			voiceID := strings.TrimSpace(voice.VoiceID)
			if voiceID == "" {
				continue
```
