import Foundation
import Vision

for file in CommandLine.arguments.dropFirst() {
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = false
    let image = URL(fileURLWithPath: file)
    try VNImageRequestHandler(url: image).perform([request])
    let lines = (request.results ?? []).compactMap { $0.topCandidates(1).first?.string }
    print(file + "\t" + lines.joined(separator: " | "))
}
