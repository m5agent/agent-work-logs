# CoreS3 integrated-camera QR acceptance on 0046

The registered CoreS3 UIFlow2 v2.5.3 programming image is `b9fe8334023c1b1f95e7c51b3a63724e621a6789812083848ed3ea7eaa332d49`, divisor 1 and one instruction per TB. Use that image and exact locked 0046 WASM `210db550d50847a3d4f66d86f81c8d1cdb2ac106ebf6bac16cccc60f4da0e211` for every comparison. The earlier locked 0043 accepted the official display example on this same firmware. Retain that point separately from new scanner acceptance.

| Original at UIFlow2 revision `a61a29409f09f1f4bebae05e15c4bd6dcc4956b6` | Source SHA-256 | Independent program oracles |
| --- | --- | --- |
| `examples/advanced/code_scanner/qrcode_detect_example.py` | `69fe47a881b313d9599472fe0f8e92cd5dfaec4832b0624a1ef387c19fa96374` | Exact original UART payload and QR type, blue label around (10,10) |
| `examples/advanced/image/cores3_image_find_qrcode_example.py` | `f3e197abec9c0060a9b06a6d06202c0e2f57786757ba35d0f9c58d6696ab615f` | Blue label around (0,0), blue border at detected corners, exact payload from the original `qrcode_list` if it can be read after interrupt |

Both take physical-model QVGA RGB565 snapshots at 320×240. Keep the original Python source within the workbench upload and UART0 raw-paste path. Both receive the same checked scene bytes in a separate immutable file for each run.

## Fixed source and controls

- Generate a single synthetic QR scene encoding the exact ASCII string `M5STACK-WASM-QR`. Pin an encoder version, QR version 2, error correction M, six pixels per module, four white quiet-zone modules, and the chosen mask. Center the full 198×198 block in a white 320×240 canvas at (61,21). Its active modules occupy (85,45) through (234,194). Keep only the rendered matrix and generator receipt. An independent host decoder must return exactly the expected payload before accepting the positive fixture.
- Generate the independent all-white QVGA image as a negative. Stream both as big-endian RGB565 DVP wire bytes of exactly 153,600 bytes, pin each SHA-256 before boot, and reuse those exact bytes in both original programs. The display evidence is separately hashed in its RGB565LE representation.
- On a private copy of the static site, a small load path verifies the chosen immutable scene asset, writes a fixed file under `/bridge` into Emscripten MEMFS during pre-run, and writes `M5SW_CAMERA_FRAME` before board initialization. It accepts no guest filename. Recompute the private site and engine asset manifest identities, clearly preserve the unchanged C/WASM and source-archive identities, and keep the stock site available as the control.
- The locked C path already opens `M5SW_CAMERA_FRAME` during `m5_lcd_cam_attach` and reads chronological high-byte-first DVP data in `lcd_cam_fill_frame` before LCD_CAM/GDMA. A model-file fixture keeps actual SCCB, capture, GDMA, guest decoder, and LCD paths intact.
- Run the blank control before each positive. Require QVGA clean transfer and no code-scanner payload, no blue overlay and no size or overflow warnings. For each positive require exact payload witness and blue label in the top strip y=0–40. For the Image API require additional blue border pixels near the four predicted hit lines x=85/234 and y=45/194, using a tolerance for detector corners. Keep guest frame events, original source hashes and normal Worker stop evidence. A same-code scene frame alone establishes camera display.

## Follow-up boundaries

Use the same camera transport for the two in-guest DL detector examples after sourcing an independently admitted image with expected person regions and stable model labels. The synthetic QR and default camera bars provide negative controls for detection. `examples/advanced/dl/cores3_example_human_face_recognition.py` also constructs `DualButtonUnit((8,9))` and requires a separate two-button stimulus for enrollment and recognition. Module13.2 QRCode runs its own UART peer on TX17/RX18, and Unit QRCode uses its own I²C 0x21 device. Neither accessory uses this integrated camera route.
