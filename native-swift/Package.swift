// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "WidgetWallSwift",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .executable(name: "WidgetWallSwift", targets: ["WidgetWallSwift"]),
    ],
    targets: [
        .executableTarget(
            name: "WidgetWallSwift",
            path: "Sources/WidgetWallSwift"
        )
    ]
)
