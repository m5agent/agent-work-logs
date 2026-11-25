import Foundation
import Vision

let image = URL(fileURLWithPath: CommandLine.arguments[1])
let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.usesLanguageCorrection = false
request.recognitionLanguages = ["en-US"]
try VNImageRequestHandler(url: image).perform([request])
let lines = (request.results ?? []).compactMap { $0.topCandidates(1).first?.string }
let output = try JSONEncoder().encode(lines)
FileHandle.standardOutput.write(output)
