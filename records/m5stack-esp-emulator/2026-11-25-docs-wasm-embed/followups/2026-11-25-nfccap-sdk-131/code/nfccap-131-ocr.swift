import Foundation
import Vision

for p in CommandLine.arguments.dropFirst() {
    let r = VNRecognizeTextRequest()
    r.recognitionLevel = .accurate
    let h = VNImageRequestHandler(url: URL(fileURLWithPath: p))
    try h.perform([r])
    print(URL(fileURLWithPath: p).lastPathComponent)
    if let lines = r.results?.compactMap({ $0.topCandidates(1).first?.string }) {
        print(lines.joined(separator: " | "))
    }
}
