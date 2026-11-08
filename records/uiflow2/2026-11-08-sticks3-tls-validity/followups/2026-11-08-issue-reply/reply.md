I rechecked the publicly published UIFlow2 v2.5.5 preview image on a StickS3 virtual device. The native application and TLS library are unchanged. Probe files were composed into the VFS.

Both `ssl.SSLContext.wrap_socket()` and `ssl.wrap_socket()` used `CERT_REQUIRED`, the supplied CA and server name, plus a client certificate.

- RTC 2026-10-27 completed two independent mutually authenticated TLS/HTTP exchanges. The peer authenticated the expected client certificate in both exchanges.
- RTC 2010-10-27 rejected both connections with the certificate-validity-in-the-future error.
- RTC 2040-10-27 rejected both connections with the certificate-expired error. Neither negative control produced an authenticated HTTP request.

The test used the actual RTC date with the epoch adjustment set to zero. Each input generated a separate certificate with validity from 2020-01-01 to 2035-01-01.

The base firmware SHA256 is `fd85648dfa1fd9656448aa45e86ee63be537a4534e959e422c0be4d45b3466c7`. The runtime SHA256 is `27df1b40de946c694b8c193ad850668118eea8656f0308e6e77b322f0b2c695e`.

This is **virtual-device validation** of the certificate-time path. The original v2.5.3 image, AWS IoT account/MQTT delivery and physical Wi-Fi remain **NOT RUN**. The original AWS setup still needs confirmation on the updated firmware.

Reproduction commands, exact application/probe hashes, serial RTC observations, peer results, capture/ZIP hashes and retained-history checks are in the [fixed-commit validation record](https://github.com/m5agent/agent-work-logs/blob/aabffece44e325ca894513026296e1b1f797d911/records/uiflow2/2026-11-08-sticks3-tls-validity/report.md).
