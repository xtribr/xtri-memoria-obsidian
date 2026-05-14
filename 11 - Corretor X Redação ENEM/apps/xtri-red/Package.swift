// swift-tools-version: 6.0

import PackageDescription

let package = Package(
    name: "XTRIRED",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .executable(name: "XTRI-RED", targets: ["XTRIRed"])
    ],
    targets: [
        .executableTarget(name: "XTRIRed")
    ]
)
