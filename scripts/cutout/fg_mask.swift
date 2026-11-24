// fg_mask.swift <in_dir> <out_dir>
// 用 macOS Vision 的主体分割（VNGenerateForegroundInstanceMaskRequest，macOS 14+）逐帧生成人像蒙版。
// 输入目录里的 *.png 逐张处理，输出同名 8 位灰度 PNG（白 = 人和手里的道具）。
// 比 VNGeneratePersonSegmentationRequest 干净：发丝、手持道具、肩后背景都更少残留。
import Vision
import CoreImage
import Foundation

let a = CommandLine.arguments
guard a.count >= 3 else { print("usage: fg_mask <in_dir> <out_dir>"); exit(2) }
let src = URL(fileURLWithPath: a[1]), dst = URL(fileURLWithPath: a[2])
try FileManager.default.createDirectory(at: dst, withIntermediateDirectories: true)
let files = try FileManager.default.contentsOfDirectory(atPath: src.path).filter { $0.hasSuffix(".png") }.sorted()
let ctx = CIContext()
let gray = CGColorSpace(name: CGColorSpace.linearGray)!
var empty = 0
for f in files {
  autoreleasepool {
    guard let ci = CIImage(contentsOf: src.appendingPathComponent(f)) else { return }
    let req = VNGenerateForegroundInstanceMaskRequest()
    let h = VNImageRequestHandler(ciImage: ci)
    do {
      try h.perform([req])
      if let r = req.results?.first {
        let buf = try r.generateScaledMaskForImage(forInstances: r.allInstances, from: h)
        try ctx.writePNGRepresentation(of: CIImage(cvPixelBuffer: buf), to: dst.appendingPathComponent(f), format: .L8, colorSpace: gray)
      } else {
        // 这一帧没认出主体：写一张全黑，后面的时间平滑会用前后帧补
        empty += 1
        let black = CIImage(color: .black).cropped(to: ci.extent)
        try ctx.writePNGRepresentation(of: black, to: dst.appendingPathComponent(f), format: .L8, colorSpace: gray)
      }
    } catch { print("fail", f, error) }
  }
}
print("masks", files.count, "empty", empty)
