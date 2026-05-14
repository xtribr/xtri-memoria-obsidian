// swift-tools-version: 6.0

import PackageDescription

let package = Package(
    name: "CorretorXMac",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .executable(name: "CorretorXMac", targets: ["CorretorXMac"])
    ],
    targets: [
        .executableTarget(name: "CorretorXMac")
    ]
)
