# Unauthenticated probe of the voice catalog endpoint

- Date: 2026-11-25 (UTC)
- Purpose: confirm whether the language catalog used by the app can be read without
  a XiaoZhi account token.

Command (no credentials, no cookies):

```bash
curl -s -m 15 -w '%{http_code}\n' https://xiaozhi.me/api/user/tts-list
```

Observed response:

```
401
{"success":false,"message":"No token provided"}
```

Interpretation:

- The endpoint requires an authenticated account token, so the actual language /
  voice keys could **not** be inspected from this environment.
- The 401 is a property of the endpoint's authentication, not evidence about which
  languages the catalog contains.
- No account credentials were used, borrowed or stored for this check.
